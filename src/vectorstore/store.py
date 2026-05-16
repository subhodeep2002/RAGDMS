"""
Builds and manages the ChromaDB vector store.
Supports both OpenAI and sentence-transformers embeddings.
"""

import os
import sys
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
import config


def get_embeddings():
    """Returns the configured embedding model."""
    if config.EMBEDDING_PROVIDER == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=config.EMBEDDING_MODEL, base_url=config.OLLAMA_BASE_URL)
    elif config.EMBEDDING_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=config.EMBEDDING_MODEL)
    else:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)


def build_vectorstore(chunks: List[Document]) -> Chroma:
    """
    Embeds chunks and persists them to ChromaDB.
    If the store already exists, adds documents to it.
    """
    embeddings = get_embeddings()

    vectorstore = Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_PERSIST_DIR,
    )

    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        vectorstore.add_documents(batch)
        print(f"[VectorStore] Embedded {min(i + batch_size, len(chunks))}/{len(chunks)} chunks")

    print(f"[VectorStore] Store saved to {config.CHROMA_PERSIST_DIR}")
    return vectorstore


def load_vectorstore() -> Chroma:
    """Loads an existing ChromaDB vector store from disk."""
    embeddings = get_embeddings()
    vectorstore = Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_PERSIST_DIR,
    )
    count = vectorstore._collection.count()
    print(f"[VectorStore] Loaded store with {count} documents.")
    return vectorstore
