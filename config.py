import os
from dotenv import load_dotenv

load_dotenv()

# LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")

# Embeddings
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "ollama")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Vector Store
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
COLLECTION_NAME = "security_knowledge_base"

# Retrieval
TOP_K = 5

# Chunking
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

# Data paths
RAW_DATA_DIR = "./data/raw"
PROCESSED_DATA_DIR = "./data/processed"
QUERIES_DIR = "./data/queries"
