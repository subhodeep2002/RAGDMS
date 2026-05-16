"""
Baseline RAG pipeline: raw query → retrieve → LLM answer.
No query reformulation. Used as the control system.
"""

import os
import sys
from typing import List, Dict

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
import config


ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """You are a defensive security analyst. Answer the question using the provided context.
Use as much relevant detail from the context as possible.
Only if the context contains absolutely no relevant information at all, say "Insufficient information in knowledge base."

Context:
{context}

Question: {question}

Answer:"""
)


def get_llm():
    if config.LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=config.LLM_MODEL, base_url=config.OLLAMA_BASE_URL, temperature=0)
    elif config.LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=config.LLM_MODEL, temperature=0)
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=config.LLM_MODEL, temperature=0)


class BaselineRAG:
    def __init__(self, vectorstore: Chroma):
        self.vectorstore = vectorstore
        self.retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": config.TOP_K},
        )
        self.llm = get_llm()

    def retrieve(self, query: str) -> List[Document]:
        return self.retriever.invoke(query)

    def answer(self, query: str) -> Dict:
        docs = self.retrieve(query)
        context = "\n\n---\n\n".join(d.page_content for d in docs)

        chain = ANSWER_PROMPT | self.llm
        response = chain.invoke({"context": context, "question": query})

        return {
            "query": query,
            "reformulated_query": None,
            "retrieved_docs": docs,
            "answer": response.content,
            "pipeline": "baseline",
        }
