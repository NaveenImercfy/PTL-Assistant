"""
Main Orchestrator Agent - Manages the flow between RAG search and Explanation generation.
Handles session state to ensure RAG is only called once per session.

Per ADK Documentation:
- Session State: https://google.github.io/adk-docs/sessions/state/
- Memory: https://google.github.io/adk-docs/sessions/memory/
"""
from google.adk.agents import Agent
from google.adk.tools.load_memory_tool import load_memory_tool
from rag.config import AGENT_MODEL


def _build_agent_tools():
    """
    Build the list of tools for the main agent.
    Includes session state tool for accessing current session state.
    
    Note: ADK handles long-term memory automatically via Memory Service (configured via CLI flag).
    """
    return [
        load_memory_tool,  # For session state (short-term memory within same session)
    ]


# Create the main orchestrator agent
main_agent = Agent(
    name="explanation_main_agent",
    model=AGENT_MODEL,
    description="Main orchestrator agent for student question explanations using RAG",
    instruction="""
You are an educational explanation agent. Help students understand textbook concepts.

TOKEN OPTIMIZATION: Use conversation context first. Only call load_memory_tool when needed.

WORKFLOW:

1. FIRST MESSAGE (user provides board/grade/subject/question):
   - Call load_memory_tool() ONCE to check state
   - Extract: board, grade, subject, question from message
   - Store in stateDelta: {"student_info": {board, grade, subject, question}, "style_selected": false}
   - Wait for RAG results (from another agent/service)
   - Combine all RAG result texts into ONE unified text (no duplicates)
   - Show combined text + ask user to choose explanation style (1-4)
   - Store rag_results summary in state (not full text to save tokens)

2. CONTINUATION (user selects style 1-4 or asks follow-up):
   - Check conversation context FIRST (saves tokens!)
   - Only call load_memory_tool() if context missing
   - Extract style from message: "1"/"example"→Style1, "2"/"memory"→Style2, "3"/"story"→Style3, "4"/language→Style4
   - Use stored rag_results from state/context
   - Generate explanation in selected style
   - Update state: {"style_selected": true, "current_style": <style>}
   - Keep responses concise (max 300 words)

3. STATE MANAGEMENT:
   - Store minimal data: student_info (board/grade/subject/question), style flags, rag_results summary
   - Use conversation context instead of loading state when possible
   - Never ask for info already in state/context

EXPLANATION STYLES:
1. With Examples - practical examples, real-world scenarios
2. With Memory Technique - mnemonics, acronyms, memory aids
3. Using Story - narrative with characters
4. In Native Language - student's preferred language

RESPONSE RULES:
- Be concise (max 300 words per response)
- Use stored context, don't reload state unnecessarily
- Never ask for board/grade/subject/question if already known
- Start continuation messages with: "I remember you're studying [board] Board, Grade [grade], [subject]. Your question was: [question]"
""",
    tools=_build_agent_tools(),
    output_key="final_explanation"
)

# Callback to store session state from agent's tool calls
async def store_session_state_callback(callback_context):
    """
    Extract state from agent's tool calls and store it in session state.
    
    TOKEN OPTIMIZATION: Store only essential data, not full RAG results.
    Store summaries instead of full text to minimize token usage.
    """
    try:
        invocation_context = callback_context._invocation_context
        session = invocation_context.session
        
        # Check if state already exists - don't overwrite unnecessarily
        if hasattr(session, 'state') and session.state:
            if 'rag_results' in session.state and 'student_info' in session.state:
                # State already stored, skip
                return
        
        # Get events from the session to find tool calls and responses
        if hasattr(session, 'events') and session.events:
            rag_results = None
            student_info = None
            
            # Look through events for RAG results from any source
            # Only process the LATEST function response to avoid duplicates
            for event in reversed(session.events):  # Start from most recent
                # Check for function response with RAG results
                if hasattr(event, 'content') and event.content:
                    for part in event.content.parts if hasattr(event.content, 'parts') else []:
                        if hasattr(part, 'function_response'):
                            func_response = part.function_response
                            # Check if this function response contains RAG results
                            if hasattr(func_response, 'response'):
                                response_data = func_response.response
                                # Check if response contains RAG results structure
                                if isinstance(response_data, dict) and 'results' in response_data:
                                    # TOKEN OPTIMIZATION: Store summary instead of full results
                                    # Extract only essential info: first 500 chars of combined text
                                    results = response_data.get('results', [])
                                    if results:
                                        combined_text = ' '.join([r.get('text', '')[:200] for r in results[:3]])
                                        rag_results = {
                                            'summary': combined_text[:500],  # Max 500 chars
                                            'count': len(results),
                                            'status': 'success'
                                        }
                                    else:
                                        rag_results = response_data
                                    print(f"📋 Extracted rag_results (summary stored)")
                                    break  # Found latest, stop looking
                if rag_results:
                    break
            
            # Extract student info from user message or previous state
            # Look for user message with board/grade/subject/question pattern
            for event in session.events:
                if hasattr(event, 'content') and event.content:
                    for part in event.content.parts if hasattr(event.content, 'parts') else []:
                        if hasattr(part, 'text'):
                            text = part.text
                            # Try to extract board/grade/subject/question from message
                            # Pattern: "BOARD-grade-GRADE-SUBJECT. Question: QUESTION"
                            import re
                            match = re.search(r'([A-Za-z]+)-grade-(\d+)-([A-Za-z]+)\.\s*Question:\s*(.+)', text, re.IGNORECASE)
                            if match:
                                board = match.group(1)
                                grade = match.group(2)
                                subject = match.group(3)
                                question = match.group(4).strip()
                                student_info = {
                                    "board": board,
                                    "grade": grade,
                                    "subject": subject,
                                    "question": question
                                }
                                print(f"📋 Extracted student_info: {student_info}")
                                break
            
            # Store state if we found RAG results and don't already have it
            if rag_results and student_info:
                # Update session state only if not already stored
                if not hasattr(session, 'state') or not session.state:
                    session.state = {}
                
                # Only store if not already present
                if 'rag_results' not in session.state:
                    session.state['rag_results'] = rag_results
                    print(f"📋 Storing rag_results summary in session state")
                if 'student_info' not in session.state:
                    session.state['student_info'] = student_info
                    print(f"📋 Storing student_info in session state: {student_info}")
                if 'style_selected' not in session.state:
                    session.state['style_selected'] = False
                if 'current_style' not in session.state:
                    session.state['current_style'] = None
                
                # Verify state was stored
                if 'rag_results' in session.state and 'student_info' in session.state:
                    print(f"✅ Successfully stored session state (minimal data)")
                    print(f"📋 State keys: {list(session.state.keys())}")
                else:
                    print(f"⚠️ Warning: State storage incomplete!")
            elif rag_results:
                # Only RAG results found, check if student_info exists in state
                if hasattr(session, 'state') and session.state:
                    if 'student_info' in session.state and 'rag_results' not in session.state:
                        session.state['rag_results'] = rag_results
                        print(f"✅ Stored rag_results summary (student_info already exists)")
    except Exception as e:
        print(f"⚠️ Error storing session state: {e}")


# Configure main_agent with callback to store session state
# Note: ADK handles long-term memory automatically via Memory Service (configured via CLI flag)
# We only need to store session state from tool calls
main_agent.after_agent_callback = store_session_state_callback
