# Postman Guide for ADK API Server

This guide shows you how to test your ADK API server endpoints using Postman.

## Prerequisites

1. ADK API server must be running:
   ```bash
   adk api_server
   ```
   Server runs on: `http://127.0.0.1:8000` (or `http://localhost:8000`)

2. Environment variables must be set:

   **Option A: Use Vertex AI (Recommended)**
   ```bash
   export GOOGLE_CLOUD_PROJECT="aitrack-29a9e"
   export GOOGLE_CLOUD_LOCATION="us-east4"
   # Make sure GOOGLE_API_KEY is NOT set (or unset it)
   unset GOOGLE_API_KEY
   gcloud auth application-default login
   ```

   **Option B: Use Google AI API Key**
   ```bash
   export GOOGLE_API_KEY="your-valid-api-key"
   # Get API key from: https://ai.google.dev/
   ```
   
   **Important:** If you get a "403 PERMISSION_DENIED - API key was reported as leaked" error, you need to:
   - Get a new API key from Google AI Studio (https://ai.google.dev/)
   - Or switch to Vertex AI (Option A) by unsetting GOOGLE_API_KEY

## API Endpoints

### 1. Run Agent (Main Endpoint)

**Endpoint:** `POST /run`

**Request Configuration:**

- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/run`
- **Headers:**
  - `Content-Type: application/json`

**Important:** You must create a session first before sending messages!

**Step 1: Create Session**

**Endpoint:** `POST /apps/{app_name}/users/{user_id}/sessions/{session_id}`

- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/apps/rag/users/u_123/sessions/s_123`
- **Headers:** `Content-Type: application/json`
- **Body:** `{}` (empty JSON object)

**Step 2: Send Message**

**Request Body (JSON):**

```json
{
  "app_name": "rag",
  "user_id": "u_123",
  "session_id": "s_123",
  "newMessage": {
    "role": "user",
    "parts": [
      {
        "text": "Your message here"
      }
    ]
  },
  "streaming": false
}
```

**Field Descriptions:**
- `app_name`: Always use `"rag"` (matches your agent package name)
- `user_id`: Unique identifier for the user (e.g., `"u_123"`)
- `session_id`: Unique identifier for the session (e.g., `"s_123"`)
- `newMessage`: Object with:
  - `role`: `"user"` (the role of the message sender)
  - `parts`: Array with one object containing:
    - `text`: The actual message/question to send to the agent
- `streaming`: Set to `false` for regular requests, `true` for streaming responses

**Example Requests:**

#### Example 1: List GCS Buckets
```json
{
  "app_name": "rag",
  "user_id": "u_123",
  "session_id": "s_123",
  "newMessage": {
    "role": "user",
    "parts": [
      {
        "text": "List all GCS buckets"
      }
    ]
  },
  "streaming": false
}
```

#### Example 2: Search RAG Corpus
```json
{
  "app_name": "rag",
  "user_id": "u_123",
  "session_id": "s_123",
  "newMessage": {
    "role": "user",
    "parts": [
      {
        "text": "What is Chain of Thought (CoT)?"
      }
    ]
  },
  "streaming": false
}
```

#### Example 3: Create RAG Corpus
```json
{
  "app_name": "rag",
  "user_id": "u_123",
  "session_id": "s_123",
  "newMessage": {
    "role": "user",
    "parts": [
      {
        "text": "Create a RAG corpus named 'test-corpus' with description 'Test corpus for Postman'"
      }
    ]
  },
  "streaming": false
}
```

#### Example 4: Search All Corpora
```json
{
  "app_name": "rag",
  "user_id": "u_123",
  "session_id": "s_123",
  "newMessage": {
    "role": "user",
    "parts": [
      {
        "text": "How do multiple teams collaborate to operationalize GenAI models?"
      }
    ]
  },
  "streaming": false
}
```

**Response Format:**

The response will be a JSON array of events. Look for the `content.parts[0].text` field to get the agent's answer.

Example response structure:
```json
[
  {
    "modelVersion": "gemini-2.5-flash",
    "content": {
      "parts": [
        {
          "text": "Agent's response here..."
        }
      ],
      "role": "model"
    },
    "finishReason": "STOP",
    "author": "explanation_main_agent",
    "actions": {
      "stateDelta": {
        "final_explanation": "Agent's response here..."
      }
    }
  }
]
```

**Note:** The response contains detailed metadata including token usage, model version, and agent actions. Extract the text from `content.parts[0].text` or `actions.stateDelta.final_explanation` for the actual response.

### 2. Create Session

**Endpoint:** `POST /apps/{app_name}/users/{user_id}/sessions/{session_id}`

**Request Configuration:**

- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/apps/rag/users/u_123/sessions/s_123`
- **Headers:**
  - `Content-Type: application/json`

**Request Body:** Empty `{}` or no body

**Response:** Session creation confirmation

## Postman Setup Steps

1. **Create a New Request:**
   - Click "New" → "HTTP Request"
   - Name it: "ADK - Run Agent"

2. **Configure the Request:**
   - Method: Select `POST`
   - URL: Enter `http://127.0.0.1:8000/run`

3. **Set Headers:**
   - Click "Headers" tab
   - Add header:
     - Key: `Content-Type`
     - Value: `application/json`

4. **Set Body:**
   - Click "Body" tab
   - Select "raw"
   - Choose "JSON" from dropdown
   - Paste the JSON request body (use examples above)

5. **Save and Send:**
   - Click "Save" to save the request
   - Click "Send" to execute

## Postman Collection Setup

You can create a Postman Collection with multiple requests:

### Collection Variables:
- `base_url`: `http://127.0.0.1:8000`
- `app_name`: `rag`
- `user_id`: `u_123`
- `session_id`: `s_123`

### Pre-request Script (Optional):
```javascript
// Auto-generate session ID if needed
if (!pm.collectionVariables.get("session_id")) {
    pm.collectionVariables.set("session_id", "s_" + Date.now());
}
```

## Important Notes

### Which Agent is Used?

Your project exports `main_agent` (explanation_main_agent) as the default `root_agent`. This agent is designed for:
- ✅ Searching RAG corpora
- ✅ Generating educational explanations
- ❌ **Cannot** perform GCS bucket operations
- ❌ **Cannot** create/manage RAG corpora

If you need GCS or corpus management features, you would need to use the `rag_management_agent` instead (requires code changes to switch the root agent).

### Agent Capabilities

**Current Agent (explanation_main_agent):**
- Searches corpora by name
- Generates explanations in different styles
- Manages session state for educational conversations

**RAG Management Agent (not currently active):**
- Creates/manages RAG corpora
- Lists/manages GCS buckets
- Uploads files to GCS
- Imports documents to corpora

## Common Use Cases

### Use Case 1: Educational Explanation System
The main agent (`main_agent`) handles educational questions:

**First, create session:**
```bash
POST http://127.0.0.1:8000/apps/rag/users/student_001/sessions/session_001
Body: {}
```

**Then send message:**
```json
{
  "app_name": "rag",
  "user_id": "student_001",
  "session_id": "session_001",
  "newMessage": {
    "role": "user",
    "parts": [
      {
        "text": "I'm a CBSE grade 10 Mathematics student. Can you explain what is quadratic equations?"
      }
    ]
  },
  "streaming": false
}
```

### Use Case 2: RAG Corpus Management
The RAG management agent handles corpus operations:

**First, create session:**
```bash
POST http://127.0.0.1:8000/apps/rag/users/admin_001/sessions/admin_session
Body: {}
```

**Then send message:**
```json
{
  "app_name": "rag",
  "user_id": "admin_001",
  "session_id": "admin_session",
  "newMessage": {
    "role": "user",
    "parts": [
      {
        "text": "List all RAG corpora"
      }
    ]
  },
  "streaming": false
}
```

## Troubleshooting

### Error: "Field required: newMessage"
- Make sure you're using `newMessage` (camelCase), not `message` or `new_message`
- Ensure `newMessage` is an object with `role` and `parts` fields
- The `parts` array should contain objects with `text` field

### Error: "Session not found"
- You must create a session first using `POST /apps/rag/users/{user_id}/sessions/{session_id}`
- Use the same `user_id` and `session_id` when sending messages

### Error: "422 Unprocessable Content"
- Check that all required fields are present
- Verify JSON syntax is correct
- Ensure `app_name` matches your agent package name (`rag`)

### Error: "500 Internal Server Error"
- Check that environment variables are set
- Verify the server is running
- Check server logs for detailed error messages

### No Response or Empty Response
- Check that `streaming: false` is set
- Wait a few seconds for the agent to process
- Check server logs for any errors

## Tips

1. **Session Management:** Use the same `session_id` for related conversations to maintain context
2. **User IDs:** Use unique `user_id` values for different users
3. **Streaming:** Set `streaming: true` for real-time responses (requires handling Server-Sent Events)
4. **Error Handling:** Always check the response status and error messages

## Testing Checklist

- [ ] Server is running (`adk api_server`)
- [ ] Environment variables are set
- [ ] Postman request method is `POST`
- [ ] URL is correct (`http://127.0.0.1:8000/run`)
- [ ] Headers include `Content-Type: application/json`
- [ ] Session is created first (POST to `/apps/rag/users/{user_id}/sessions/{session_id}`)
- [ ] Body is valid JSON with `newMessage.role` and `newMessage.parts[0].text`
- [ ] `app_name` is set to `"rag"`
- [ ] `user_id` and `session_id` are provided

## Additional Resources

- ADK Documentation: https://google.github.io/adk-docs/
- ADK API Server Docs: https://google.github.io/adk-docs/runtime/api-server/

