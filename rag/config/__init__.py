"""
Configuration settings for the Vertex AI RAG engine.
"""
import os

# Google Cloud Project Settings
# These are used for Vertex AI operations (RAG corpora, embeddings, etc.)
# For the ADK agent model to work, you need EITHER:
# 1. GOOGLE_API_KEY environment variable (for Google AI API), OR
# 2. GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION with proper GCP credentials
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "aitrack-29a9e")  # Fallback to default project
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-east4")  # Default location for Vertex AI and GCS resources

# GCS Storage Settings
GCS_DEFAULT_STORAGE_CLASS = "STANDARD"
GCS_DEFAULT_LOCATION = "US"
GCS_LIST_BUCKETS_MAX_RESULTS = 50
GCS_LIST_BLOBS_MAX_RESULTS = 100
GCS_DEFAULT_CONTENT_TYPE = "application/pdf"  # Default content type for uploaded files

# RAG Corpus Settings
RAG_DEFAULT_EMBEDDING_MODEL = "text-embedding-004"
RAG_DEFAULT_TOP_K = 10  # Default number of results for single corpus query
RAG_DEFAULT_SEARCH_TOP_K = 5  # Default number of results per corpus for search_all
RAG_DEFAULT_VECTOR_DISTANCE_THRESHOLD = 0.5
RAG_DEFAULT_PAGE_SIZE = 50  # Default page size for listing files

# Agent Settings
AGENT_NAME = "rag_corpus_manager"  # For original RAG management agent
AGENT_MODEL = "gemini-2.5-flash"
AGENT_OUTPUT_KEY = "last_response"

# Explanation Agent Settings
EXPLANATION_AGENT_NAME = "explanation_main_agent"
EXPLANATION_AGENT_OUTPUT_KEY = "final_explanation"

# Vertex AI Memory Bank Settings (Optional - for long-term knowledge storage)
# Per ADK Documentation: https://google.github.io/adk-docs/sessions/memory/
AGENT_ENGINE_ID = os.environ.get("AGENT_ENGINE_ID")  # Set this to enable Memory Bank
# To enable Memory Bank:
# 1. Create Agent Engine in Vertex AI Console
# 2. Set AGENT_ENGINE_ID environment variable
# 3. Start ADK server with: --memory_service_uri="agentengine://${AGENT_ENGINE_ID}"
# See VERTEX_AI_MEMORY_BANK_SETUP.md for detailed instructions

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
