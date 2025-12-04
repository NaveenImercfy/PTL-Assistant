# Vertex AI Memory Bank Setup Guide

This guide explains how to configure Vertex AI Memory Bank for long-term knowledge storage across multiple sessions.

Per ADK Official Documentation: https://google.github.io/adk-docs/sessions/memory/

## What is Vertex AI Memory Bank?

Vertex AI Memory Bank provides:
- **Long-term Knowledge**: Stores information from past conversations across multiple sessions
- **Semantic Search**: Advanced search capabilities to find relevant past conversations
- **Automatic Extraction**: Intelligently extracts and consolidates meaningful information from conversations
- **Persistent Storage**: Managed by Vertex AI, survives application restarts

## Prerequisites

### 1. Google Cloud Setup

```bash
# Set your Google Cloud project
export GOOGLE_CLOUD_PROJECT="your-project-id"  # e.g., "aitrack-29a9e"
export GOOGLE_CLOUD_LOCATION="your-location"   # e.g., "us-east4"

# Authenticate
gcloud auth application-default login

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com --project=${GOOGLE_CLOUD_PROJECT}
```

### 2. Create Agent Engine

You need to create an Agent Engine instance in Vertex AI:

1. Go to [Vertex AI Console](https://console.cloud.google.com/vertex-ai)
2. Navigate to **Agent Engine**
3. Create a new Agent Engine instance
4. Note the **Agent Engine ID** (you'll need this for configuration)

**Note**: You do NOT need to deploy your agent to Agent Engine Runtime to use Memory Bank. The Agent Engine instance is just for Memory Bank configuration.

### 3. Set Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT="aitrack-29a9e"
export GOOGLE_CLOUD_LOCATION="us-east4"
export AGENT_ENGINE_ID="your-agent-engine-id"  # From step 2
```

## Configuration Methods

### Method 1: Using ADK Server Flag (Recommended for Deployment)

This is the simplest method. When starting your ADK server, add the `--memory_service_uri` flag:

```bash
# For API Server
adk api_server rag/ --memory_service_uri="agentengine://YOUR_AGENT_ENGINE_ID"

# For Web Interface
adk web rag/ --memory_service_uri="agentengine://YOUR_AGENT_ENGINE_ID"
```

**Example:**
```bash
adk api_server rag/ --memory_service_uri="agentengine://1234567890"
```

### Method 2: Manual Configuration in Code

If you need more control, you can configure Memory Bank programmatically:

```python
from rag.memory_config import get_memory_service, auto_save_session_to_memory_callback
from rag.main_agent import main_agent
from google import adk

# Get memory service
memory_service = get_memory_service("YOUR_AGENT_ENGINE_ID")

# Configure agent with memory callback (saves sessions automatically)
main_agent.after_agent_callback = auto_save_session_to_memory_callback

# Create runner with memory service
runner = adk.Runner(
    app_name="rag",
    root_agent=main_agent,
    memory_service=memory_service
)
```

## Adding Memory Tools to Agent

### Option A: PreloadMemoryTool (Always Retrieve Memory)

This tool automatically retrieves relevant memories at the beginning of each agent turn:

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

**Note**: `load_memory_tool` (for session state) is different from `LoadMemoryTool` (for Memory Bank). Both can be used together:
- `load_memory_tool`: Accesses current session's state (short-term)
- `LoadMemoryTool`: Accesses Memory Bank (long-term across sessions)

## Automatic Session Saving

To automatically save completed sessions to Memory Bank, use the callback:

```python
from rag.memory_config import auto_save_session_to_memory_callback
from rag.main_agent import main_agent

# Configure agent to save sessions to Memory Bank after each conversation
main_agent.after_agent_callback = auto_save_session_to_memory_callback
```

This callback:
- Extracts meaningful information from the session
- Stores it in Memory Bank
- Makes it searchable for future conversations

## How It Works

1. **Session Interaction**: User interacts with agent via a Session
2. **Memory Retrieval**: Agent uses PreloadMemoryTool or LoadMemoryTool to search Memory Bank
3. **Context Enhancement**: Retrieved memories provide context from past conversations
4. **Session Completion**: After conversation, `add_session_to_memory` saves session to Memory Bank
5. **Future Queries**: Future conversations can search and retrieve relevant past information

## Example Use Cases

### Use Case 1: Remembering Student Preferences

```python
# Session 1: Student says "I prefer explanations with examples"
# This gets saved to Memory Bank

# Session 2: Student asks new question
# Agent retrieves memory: "This student prefers examples"
# Agent automatically uses example-based explanation style
```

### Use Case 2: Cross-Session Context

```python
# Session 1: Student asks about "Pythagorean theorem" in Grade 10 Math
# Session 2: Student asks "Can you explain that again?"
# Agent searches Memory Bank, finds previous conversation
# Agent provides explanation based on past context
```

## Testing Memory Bank

### Test 1: Verify Memory Service is Configured

```python
from rag.memory_config import get_memory_service

memory_service = get_memory_service()
if memory_service:
    print("✅ Memory Bank configured!")
else:
    print("❌ Memory Bank not configured. Check prerequisites.")
```

### Test 2: Check if Sessions are Being Saved

Look for log messages:
```
Session s_123 saved to Memory Bank
```

### Test 3: Verify Memory Retrieval

Send a message that should trigger memory search:
```
"What did we discuss about crocodiles before?"
```

The agent should retrieve relevant past conversations from Memory Bank.

## Troubleshooting

### Issue: Memory Bank not working

**Check:**
1. ✅ Agent Engine ID is correct
2. ✅ Environment variables are set
3. ✅ Authentication is configured (`gcloud auth application-default login`)
4. ✅ Vertex AI API is enabled
5. ✅ `--memory_service_uri` flag is used (if using Method 1)

### Issue: Sessions not being saved

**Check:**
1. ✅ `after_agent_callback` is configured
2. ✅ Memory service is properly initialized
3. ✅ Check logs for errors

### Issue: Memory not being retrieved

**Check:**
1. ✅ PreloadMemoryTool or LoadMemoryTool is in agent's tools
2. ✅ Memory Bank has stored sessions (check if sessions are being saved)
3. ✅ Search query is relevant to stored memories

## Differences: Session State vs Memory Bank

| Feature | Session State | Memory Bank |
|---------|--------------|-------------|
| **Scope** | Single session | Multiple sessions |
| **Duration** | Temporary (session lifetime) | Persistent (long-term) |
| **Purpose** | Current conversation context | Past conversation knowledge |
| **Tool** | `load_memory_tool` | `PreloadMemoryTool` / `LoadMemoryTool` |
| **Storage** | SessionService | Vertex AI Memory Bank |

**Both can be used together:**
- Session State: "What did the user ask in THIS conversation?"
- Memory Bank: "What did the user ask in PAST conversations?"

## References

- [ADK Memory Documentation](https://google.github.io/adk-docs/sessions/memory/)
- [Vertex AI Memory Bank Overview](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)
- [Agent Engine Setup](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)

