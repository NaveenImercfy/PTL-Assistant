"""
RAG Agent - Searches corpus and retrieves relevant information for questions.
This agent is called once per session to get the initial RAG results.
"""
from google.adk.agents import Agent
from rag.tools import corpus_tools
from rag.config import AGENT_MODEL


# Create the RAG agent
rag_agent = Agent(
    name="rag_agent",
    model=AGENT_MODEL,
    description="Agent that searches RAG corpora to find relevant information for student questions",
    instruction="""
    You are a RAG (Retrieval-Augmented Generation) agent specialized in searching educational content.
    
    Your role is to:
    1. Search the specified corpus using the provided question
    2. Retrieve the most relevant information from the corpus
    3. Return comprehensive search results with citations
    
    When searching:
    - Use search_corpus_by_name to search a specific corpus by its display name
    - Always include citation information in your results
    - Focus on retrieving accurate, relevant content from the corpus
    
    Return the search results in a structured format that can be used by the explanation agent.
    """,
    tools=[
        corpus_tools.search_corpus_by_name_tool,
        corpus_tools.query_rag_corpus_tool,
    ],
    output_key="rag_results"
)

