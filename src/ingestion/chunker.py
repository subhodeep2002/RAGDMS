"""
Chunks documents for embedding. Security docs benefit from smaller chunks
to keep technique/CVE context tight within each chunk.
"""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
import config


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Splits documents into chunks suitable for embedding.
    Preserves metadata from parent documents.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(documents)
    print(f"[Chunker] {len(documents)} documents → {len(chunks)} chunks")
    return chunks
