# In-Memory Memory Setup Guide (Local Development)

This guide explains how to use In-Memory Memory for local development and testing.

Per ADK Official Documentation: https://google.github.io/adk-docs/sessions/memory/#in-memory-memory

## What is In-Memory Memory?

InMemoryMemoryService is the **default** memory service in ADK. It provides:
- ✅ **No Setup Required** - Works out of the box
- ✅ **No Dependencies** - No Google Cloud setup needed  
- ✅ **Perfect for Local Development** - Fast and simple
- ✅ **Full Conversation Storage** - Stores complete conversation history
- ✅ **Basic Keyword Search** - Searches using keyword matching

**Limitations:**
- ❌ **No Persistence** - Data is lost when application restarts
- ❌ **Basic Search** - Uses keyword matching (not semantic search)
- ❌ **Single Process** - Memory is only available within the same process

## Quick Start (No Configuration Needed!)

InMemoryMemoryService is the **DEFAULT** - just start your ADK server normally:

```bash
# Option 1: Default (automatically uses In-Memory Memory)
adk api_server rag/

# Option 2: Explicitly specify In-Memory Memory
adk api_server rag/ --memory_service_uri="inmemory://"

# Option 3: Web interface
adk web rag/
```

**That's it!** No additional setup required.

## How It Works

### 1. Memory Tools Already Configured

The agent already includes `PreloadMemoryTool` which:
- Automatically retrieves relevant memories at the start of each turn
- Searches past conversations stored in memory
- Provides context from previous sessions

### 2. Automatic Session Saving

Sessions are automatically saved to memory via the `auto_save_session_to_memory_callback`:
- After each conversation, the session is saved to memory
- Full conversation history is stored
- Available for search in future conversations

### 3. Memory Search

When a user asks a question, the agent:
1. Uses `PreloadMemoryTool` to search past conversations
2. Retrieves relevant memories from previous sessions
3. Uses this context to provide better answers

## Example Usage

### Session 1: First Conversation

```bash
# User asks:
"I'm CBSE grade 6 English student. What do crocodiles eat?"

# Agent responds with RAG results and explanation styles
# Session is automatically saved to In-Memory Memory
```

### Session 2: Second Conversation (Different Session ID)

```bash
# User asks:
"What did we discuss about crocodiles before?"

# Agent uses PreloadMemoryTool to search memory
# Finds previous conversation about crocodiles
# Responds: "We discussed that crocodiles eat fish, birds, and small animals..."
```

### Session 3: Same User, Different Question

```bash
# User asks:
"Can you explain that again?"

# Agent searches memory, finds context about:
# - Board: CBSE
# - Grade: 6
# - Subject: English
# - Previous question: "What do crocodiles eat?"
# Agent provides explanation based on stored context
```

## Testing Memory Retrieval

### Test 1: Verify Memory is Working

1. Start ADK server:
   ```bash
   adk api_server rag/
   ```

2. Send first message:
   ```json
   {
     "app_name": "rag",
     "user_id": "test_user",
     "session_id": "session_1",
     "newMessage": {
       "role": "user",
       "parts": [{"text": "I'm CBSE grade 6 English. What do crocodiles eat?"}]
     }
   }
   ```

3. Complete the conversation (select explanation style, etc.)

4. Start new session with same user_id:
   ```json
   {
     "app_name": "rag",
     "user_id": "test_user",  // Same user_id
     "session_id": "session_2",  // Different session_id
     "newMessage": {
       "role": "user",
       "parts": [{"text": "What did we discuss before?"}]
     }
   }
   ```

5. Agent should retrieve previous conversation from memory!

### Test 2: Check Memory Search

Ask questions that should trigger memory search:
- "What did I ask before?"
- "What was my previous question?"
- "Can you remind me what we discussed?"
- "What topics have we covered?"

The agent should search memory and provide relevant past conversation context.

## Configuration Options

### Option A: PreloadMemoryTool (Current - Always Loads Memory)

The agent currently uses `PreloadMemoryTool` which:
- ✅ Always retrieves memory at start of each turn
- ✅ Provides consistent context
- ✅ Best for most use cases

### Option B: LoadMemoryTool (On-Demand)

If you prefer on-demand memory retrieval, modify `rag/main_agent.py`:

```python
# In _build_agent_tools() function, change:
if MEMORY_TOOLS_AVAILABLE and PreloadMemoryTool:
    tools_list.insert(1, PreloadMemoryTool())

# To:
if MEMORY_TOOLS_AVAILABLE and LoadMemoryTool:
    tools_list.insert(1, LoadMemoryTool())
```

This allows the agent to decide when to retrieve memory instead of always loading it.

## Differences: Session State vs In-Memory Memory

| Feature | Session State | In-Memory Memory |
|---------|--------------|------------------|
| **Scope** | Single session | Multiple sessions |
| **Duration** | Session lifetime | Until app restart |
| **Purpose** | Current conversation context | Past conversation knowledge |
| **Tool** | `load_memory_tool` | `PreloadMemoryTool` / `LoadMemoryTool` |
| **Storage** | SessionService | InMemoryMemoryService |

**Both work together:**
- Session State: "What did the user ask in THIS conversation?"
- In-Memory Memory: "What did the user ask in PAST conversations?"

## Troubleshooting

### Issue: Memory not being retrieved

**Check:**
1. ✅ Is `PreloadMemoryTool` in the agent's tools list?
2. ✅ Are sessions being saved? (Check logs for "Session saved to Memory Service")
3. ✅ Is the same `user_id` being used? (Memory is scoped by user_id)
4. ✅ Has at least one conversation been completed and saved?

### Issue: Sessions not being saved

**Check:**
1. ✅ Is `after_agent_callback` configured? (Already configured in `main_agent.py`)
2. ✅ Check logs for errors when saving sessions
3. ✅ Verify Memory Service is available

### Issue: Memory lost on restart

**This is expected!** In-Memory Memory doesn't persist across restarts.
- ✅ For local development: This is fine - just restart and test again
- ❌ For production: Use Vertex AI Memory Bank instead (see VERTEX_AI_MEMORY_BANK_SETUP.md)

## When to Use In-Memory Memory

✅ **Use for:**
- Local development and testing
- Prototyping new features
- Quick demos and examples
- When you don't need persistence
- Single-process deployments

❌ **Don't use for:**
- Production deployments (use Vertex AI Memory Bank)
- When you need data persistence
- When you need advanced semantic search
- Multi-process deployments

## Migration to Vertex AI Memory Bank

When ready for production, switch to Vertex AI Memory Bank:

```bash
# Instead of:
adk api_server rag/

# Use:
export AGENT_ENGINE_ID="your-agent-engine-id"
adk api_server rag/ --memory_service_uri="agentengine://${AGENT_ENGINE_ID}"
```

No code changes needed! The same `PreloadMemoryTool` and callback work with both.

## References

- [ADK Memory Documentation](https://google.github.io/adk-docs/sessions/memory/)
- [In-Memory Memory Section](https://google.github.io/adk-docs/sessions/memory/#in-memory-memory)
- [Searching Memory Within a Tool](https://google.github.io/adk-docs/sessions/memory/#searching-memory-within-a-tool)

