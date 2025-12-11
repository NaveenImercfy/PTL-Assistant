"""
RAG Agent - Directly searches the education_textbooks_unified corpus using VertexAiRagRetrieval.
This agent is called once per session to get the initial RAG results.

Reference: https://github.com/google/adk-samples/blob/main/python/agents/RAG/rag/agent.py
"""
from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag
from rag.config import AGENT_MODEL, PROJECT_ID, LOCATION

def _get_education_textbooks_corpus_path():
    """Get the full corpus path for education_textbooks_unified corpus."""
    # Import here to avoid circular dependencies
    from rag.tools.corpus_tools import get_corpus_by_name
    
    # Get corpus by name
    corpus_response = get_corpus_by_name("education_textbooks_unified")
    if corpus_response["status"] != "success":
        raise ValueError(f"Failed to find corpus 'education_textbooks_unified': {corpus_response.get('error_message', 'Unknown error')}")
    
    corpus_id = corpus_response["corpus_id"]
    # Construct full corpus resource path
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{corpus_id}"


# Create the VertexAiRagRetrieval tool for direct corpus access
# Reference: https://github.com/google/adk-samples/blob/main/python/agents/RAG/rag/agent.py
# The corpus path will be resolved when the tool is first used
try:
    corpus_path = _get_education_textbooks_corpus_path()
    education_textbooks_retrieval = VertexAiRagRetrieval(
        name='retrieve_education_textbooks',
        description=(
            'Use this tool to retrieve educational content and textbook information '
            'from the education_textbooks_unified corpus for student questions. '
            'This tool directly queries the corpus - just provide the question.'
        ),
        rag_resources=[
            rag.RagResource(
                rag_corpus=corpus_path
            )
        ],
        similarity_top_k=10,
        vector_distance_threshold=0.6,
    )
except Exception as e:
    # If corpus lookup fails at import time, we'll handle it gracefully
    education_textbooks_retrieval = None
    print(f"Warning: Could not initialize RAG retrieval tool at import time: {e}")
    print("The corpus will be looked up when the agent is first used.")


# Create the RAG agent
rag_agent = Agent(
    name="rag_agent",
    model=AGENT_MODEL,
    description="Agent that directly searches the education_textbooks_unified RAG corpus to find relevant information for student questions",
    instruction="""
    You are a RAG (Retrieval-Augmented Generation) agent specialized in searching educational content from the education_textbooks_unified corpus.
    
    Your role is to:
    1. Use the retrieve_education_textbooks tool to search the "education_textbooks_unified" corpus
    2. Retrieve the most relevant information from the corpus for the student's question
    3. Return comprehensive search results with citations
    
    IMPORTANT: You ONLY search the corpus named "education_textbooks_unified". This is the only corpus you have access to.
    
    When searching:
    - Use the retrieve_education_textbooks tool with the student's question
    - This tool directly queries the education_textbooks_unified corpus
    - Always include citation information in your results
    - Focus on retrieving accurate, relevant content from the corpus
    
    The tool automatically handles the corpus lookup and retrieval - you just need to provide the question.
    
    Return the search results in a structured format that can be used by the explanation agent.
    """,
    tools=[
        education_textbooks_retrieval,
    ] if education_textbooks_retrieval else [],
    output_key="rag_results"
)

