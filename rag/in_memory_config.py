"""
In-Memory Memory Configuration for Local Development

This module provides configuration for InMemoryMemoryService, which is the default
memory service for local development and prototyping.

Per ADK Documentation: https://google.github.io/adk-docs/sessions/memory/#in-memory-memory

InMemoryMemoryService Features:
- No persistence (data lost on restart) - perfect for local testing
- Basic keyword matching for search
- Stores full conversation history
- No setup required - it's the default
- Good for prototyping and local development

To use In-Memory Memory:
1. Don't specify --memory_service_uri (defaults to in-memory), OR
2. Explicitly use: --memory_service_uri="inmemory://"
3. Add PreloadMemoryTool or LoadMemoryTool to agent tools
4. Add callback to save sessions to memory
"""

import os
from typing import Optional

try:
    from google import adk
    from google.adk.memory import InMemoryMemoryService
    from google.adk.tools.preload_memory_tool import PreloadMemoryTool
    from google.adk.tools.load_memory_tool import LoadMemoryTool
    IN_MEMORY_AVAILABLE = True
except ImportError:
    InMemoryMemoryService = None
    PreloadMemoryTool = None
    LoadMemoryTool = None
    IN_MEMORY_AVAILABLE = False


def get_in_memory_service() -> Optional[InMemoryMemoryService]:
    """
    Create and return an InMemoryMemoryService instance.
    
    InMemoryMemoryService is the default memory service - no configuration needed!
    It's automatically used when no memory_service_uri is specified.
    
    Returns:
        InMemoryMemoryService instance or None if not available
    
    Example:
        memory_service = get_in_memory_service()
        runner = adk.Runner(memory_service=memory_service)
    """
    if not IN_MEMORY_AVAILABLE:
        return None
    
    try:
        return InMemoryMemoryService()
    except Exception as e:
        print(f"Error creating InMemoryMemoryService: {e}")
        return None


async def auto_save_session_to_memory_callback(callback_context):
    """
    Callback function to automatically save completed sessions to In-Memory Memory.
    
    This stores the full conversation in memory for future retrieval.
    Note: Data is lost when the application restarts (no persistence).
    
    Usage:
        agent = Agent(
            ...
            after_agent_callback=auto_save_session_to_memory_callback,
        )
    """
    try:
        invocation_context = callback_context._invocation_context
        session = invocation_context.session
        memory_service = invocation_context.memory_service
        
        if memory_service and hasattr(memory_service, 'add_session_to_memory'):
            await memory_service.add_session_to_memory(session)
            print(f"Session {session.id} saved to In-Memory Memory")
    except Exception as e:
        print(f"Error saving session to In-Memory Memory: {e}")


def get_preload_memory_tool():
    """
    Get PreloadMemoryTool instance for agents.
    
    PreloadMemoryTool automatically retrieves relevant memories at the beginning
    of each agent turn, providing context from past conversations.
    
    Returns:
        PreloadMemoryTool instance or None if not available
    """
    if IN_MEMORY_AVAILABLE and PreloadMemoryTool:
        return PreloadMemoryTool()
    return None


def get_load_memory_tool():
    """
    Get LoadMemoryTool instance for agents.
    
    LoadMemoryTool allows the agent to retrieve memory when it decides it's helpful.
    This is on-demand memory retrieval (unlike PreloadMemoryTool which always loads).
    
    Returns:
        LoadMemoryTool instance or None if not available
    """
    if IN_MEMORY_AVAILABLE and LoadMemoryTool:
        return LoadMemoryTool()
    return None


# Configuration instructions for local development
IN_MEMORY_SETUP_INSTRUCTIONS = """
# In-Memory Memory Setup Instructions (Local Development)

## Quick Start (No Configuration Needed!)

InMemoryMemoryService is the DEFAULT memory service. Just start your ADK server normally:

```bash
# Option 1: Default (automatically uses In-Memory Memory)
adk api_server rag/

# Option 2: Explicitly specify In-Memory Memory
adk api_server rag/ --memory_service_uri="inmemory://"

# Option 3: Web interface
adk web rag/
```

That's it! No additional setup required.

## Adding Memory Tools to Agent

### Option A: PreloadMemoryTool (Always Retrieve Memory)

This tool automatically retrieves relevant memories at the beginning of each turn:

```python
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from rag.main_agent import main_agent

# Add PreloadMemoryTool to agent tools
main_agent.tools.append(PreloadMemoryTool())
```

### Option B: LoadMemoryTool (On-Demand)

This tool allows the agent to retrieve memory when it decides it's helpful:

```python
from google.adk.tools.load_memory_tool import LoadMemoryTool
from rag.main_agent import main_agent

# Add LoadMemoryTool to agent tools
main_agent.tools.append(LoadMemoryTool())
```

**Note**: `load_memory_tool` (for session state) is different from `LoadMemoryTool` (for Memory Service):
- `load_memory_tool`: Accesses current session's state (short-term, same session)
- `LoadMemoryTool`: Accesses Memory Service (long-term, across sessions)

## Automatic Session Saving

To automatically save completed sessions to memory:

```python
from rag.in_memory_config import auto_save_session_to_memory_callback
from rag.main_agent import main_agent

# Configure agent to save sessions to memory after each conversation
main_agent.after_agent_callback = auto_save_session_to_memory_callback
```

## Features

✅ **No Setup Required** - Works out of the box
✅ **No Dependencies** - No Google Cloud setup needed
✅ **Perfect for Local Development** - Fast and simple
✅ **Full Conversation Storage** - Stores complete conversation history
✅ **Basic Keyword Search** - Searches using keyword matching

## Limitations

❌ **No Persistence** - Data is lost when application restarts
❌ **Basic Search** - Uses keyword matching (not semantic search)
❌ **Single Process** - Memory is only available within the same process

## When to Use

- ✅ Local development and testing
- ✅ Prototyping new features
- ✅ Quick demos and examples
- ✅ When you don't need persistence

## When NOT to Use

- ❌ Production deployments (use Vertex AI Memory Bank instead)
- ❌ When you need data persistence
- ❌ When you need advanced semantic search
- ❌ Multi-process deployments

## Example Usage

```python
from rag.in_memory_config import (
    get_in_memory_service,
    auto_save_session_to_memory_callback,
    get_preload_memory_tool
)
from rag.main_agent import main_agent
from google import adk

# Get in-memory service (optional - it's the default)
memory_service = get_in_memory_service()

# Add PreloadMemoryTool to agent
preload_tool = get_preload_memory_tool()
if preload_tool:
    main_agent.tools.append(preload_tool)

# Configure callback to save sessions
main_agent.after_agent_callback = auto_save_session_to_memory_callback

# Create runner (memory_service is optional - defaults to InMemoryMemoryService)
runner = adk.Runner(
    app_name="rag",
    root_agent=main_agent,
    memory_service=memory_service  # Optional - defaults to InMemoryMemoryService
)
```

## Testing Memory Retrieval

1. Start a conversation and complete it
2. Start a new conversation
3. Ask: "What did we discuss before?" or "What was my previous question?"
4. The agent should retrieve information from past conversations stored in memory
"""

