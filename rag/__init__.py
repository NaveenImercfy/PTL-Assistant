# Export the main explanation agent as the default agent
from .main_agent import main_agent

# Also export the original RAG management agent if needed
from .agent import agent as rag_management_agent

# Set main_agent as the root agent for the explanation system
root_agent = main_agent

# Export the App with resumability enabled (if app.py exists)
try:
    from .app import app
except ImportError:
    # App configuration not available (fallback for older setups)
    app = None