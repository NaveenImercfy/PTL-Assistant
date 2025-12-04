"""
Vertex AI Memory Bank Configuration

This module provides configuration and callbacks for Vertex AI Memory Bank integration.
Per ADK Documentation: https://google.github.io/adk-docs/sessions/memory/

Vertex AI Memory Bank provides:
- Long-term knowledge storage across multiple sessions
- Semantic search across past conversations
- Automatic memory extraction and consolidation
- Persistent memory managed by Vertex AI

Prerequisites:
1. Google Cloud Project with Vertex AI API enabled
2. Agent Engine instance created in Vertex AI
3. Environment variables set:
   - GOOGLE_CLOUD_PROJECT
   - GOOGLE_CLOUD_LOCATION
4. Authentication: gcloud auth application-default login
"""

import os
from typing import Optional

try:
    from google import adk
    from google.adk.memory import VertexAiMemoryBankService
    from google.adk.tools.preload_memory_tool import PreloadMemoryTool
    MEMORY_BANK_AVAILABLE = True
except ImportError:
    VertexAiMemoryBankService = None
    PreloadMemoryTool = None
    MEMORY_BANK_AVAILABLE = False


def get_memory_service(agent_engine_id: Optional[str] = None) -> Optional[VertexAiMemoryBankService]:
    """
    Create and return a Vertex AI Memory Bank Service instance.
    
    Args:
        agent_engine_id: The Agent Engine ID from Vertex AI.
                        If None, reads from AGENT_ENGINE_ID environment variable.
    
    Returns:
        VertexAiMemoryBankService instance or None if not available
    
    Example:
        memory_service = get_memory_service("1234567890")
        runner = adk.Runner(memory_service=memory_service)
    """
    if not MEMORY_BANK_AVAILABLE:
        return None
    
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION")
    agent_engine_id = agent_engine_id or os.environ.get("AGENT_ENGINE_ID")
    
    if not all([project_id, location, agent_engine_id]):
        print("Warning: Vertex AI Memory Bank not configured. Missing:")
        if not project_id:
            print("  - GOOGLE_CLOUD_PROJECT environment variable")
        if not location:
            print("  - GOOGLE_CLOUD_LOCATION environment variable")
        if not agent_engine_id:
            print("  - AGENT_ENGINE_ID environment variable or parameter")
        return None
    
    try:
        return VertexAiMemoryBankService(
            project=project_id,
            location=location,
            agent_engine_id=agent_engine_id
        )
    except Exception as e:
        print(f"Error creating Vertex AI Memory Bank Service: {e}")
        return None


async def auto_save_session_to_memory_callback(callback_context):
    """
    Callback function to automatically save completed sessions to Memory Bank.
    
    Per ADK Documentation, this extracts meaningful information from sessions
    and stores it in the long-term memory for future retrieval.
    
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
            print(f"Session {session.id} saved to Memory Bank")
    except Exception as e:
        print(f"Error saving session to Memory Bank: {e}")


def get_preload_memory_tool():
    """
    Get PreloadMemoryTool instance for agents.
    
    PreloadMemoryTool automatically retrieves relevant memories at the beginning
    of each agent turn, providing context from past conversations.
    
    Returns:
        PreloadMemoryTool instance or None if not available
    """
    if MEMORY_BANK_AVAILABLE and PreloadMemoryTool:
        return PreloadMemoryTool()
    return None


# Configuration instructions for deployment
MEMORY_BANK_SETUP_INSTRUCTIONS = """
# Vertex AI Memory Bank Setup Instructions

## Option 1: Using ADK Server Flag (Recommended for Deployment)

When starting the ADK server, use the --memory_service_uri flag:

```bash
adk api_server rag/ --memory_service_uri="agentengine://YOUR_AGENT_ENGINE_ID"
```

Or for web interface:
```bash
adk web rag/ --memory_service_uri="agentengine://YOUR_AGENT_ENGINE_ID"
```

## Option 2: Manual Configuration in Code

```python
from rag.memory_config import get_memory_service, auto_save_session_to_memory_callback
from rag.main_agent import main_agent
from google import adk

# Get memory service
memory_service = get_memory_service("YOUR_AGENT_ENGINE_ID")

# Configure agent with memory callback
main_agent.after_agent_callback = auto_save_session_to_memory_callback

# Create runner with memory service
runner = adk.Runner(
    app_name="rag",
    root_agent=main_agent,
    memory_service=memory_service
)
```

## Prerequisites

1. Create Agent Engine in Vertex AI:
   - Go to Vertex AI Console
   - Create an Agent Engine instance
   - Note the Agent Engine ID

2. Set Environment Variables:
   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_CLOUD_LOCATION="us-central1"
   export AGENT_ENGINE_ID="your-agent-engine-id"
   ```

3. Authenticate:
   ```bash
   gcloud auth application-default login
   ```

## Adding Memory Tools to Agent

The agent can use:
- PreloadMemoryTool: Always retrieves memory at start of each turn
- LoadMemoryTool: Retrieves memory when agent decides it's helpful

Example:
```python
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

agent = Agent(
    ...
    tools=[PreloadMemoryTool(), ...]
)
```
"""

