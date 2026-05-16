"""
Enhanced RAG pipeline: query → reformulation agent → retrieve → LLM answer.
Supports all four reformulation strategies.
"""

import os
import sys
from typing import List, Dict, Literal

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
import config
from src.reformulation.query_expansion import QueryExpansionAgent
from src.reformulation.hyde import HyDEAgent
from src.reformulation.stepback import StepBackAgent
from src.reformulation.decomposition import SubQueryDecompositionAgent


ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """You are a defensive security analyst. Answer the question using the provided context.
Use as much relevant detail from the context as possible.
Only if the context contains absolutely no relevant information at all, say "Insufficient information in knowledge base."

Context:
{context}

Question: {question}

Answer:"""
)

ReformulationStrategy = Literal["expansion", "hyde", "stepback", "decomposition"]


class EnhancedRAG:
    def __init__(
        self,
        vectorstore: Chroma,
        strategy: ReformulationStrategy = "expansion",
    ):
        self.vectorstore = vectorstore
        self.strategy = strategy
        self.retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": config.TOP_K},
        )

        if config.LLM_PROVIDER == "ollama":
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(model=config.LLM_MODEL, base_url=config.OLLAMA_BASE_URL, temperature=0)
        elif config.LLM_PROVIDER == "anthropic":
            from langchain_anthropic import ChatAnthropic
            self.llm = ChatAnthropic(model=config.LLM_MODEL, temperature=0)
        else:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(model=config.LLM_MODEL, temperature=0)

        # Load the selected reformulation agent
        self.agent = self._load_agent(strategy)

    def _load_agent(self, strategy: ReformulationStrategy):
        if strategy == "expansion":
            return QueryExpansionAgent()
        elif strategy == "hyde":
            return HyDEAgent()
        elif strategy == "stepback":
            return StepBackAgent()
        elif strategy == "decomposition":
            return SubQueryDecompositionAgent()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def retrieve(self, query: str) -> List[Document]:
        if self.strategy == "decomposition":
            # Retrieve for each sub-query and merge unique results
            sub_queries = self.agent.decompose(query)
            seen = set()
            docs = []
            for sq in sub_queries:
                for doc in self.retriever.invoke(sq):
                    key = doc.page_content[:100]
                    if key not in seen:
                        seen.add(key)
                        docs.append(doc)
            return docs[: config.TOP_K * 2]  # allow more docs for decomposition
        else:
            reformulated = self.agent.reformulate(query)
            return self.retriever.invoke(reformulated)

    def answer(self, query: str) -> Dict:
        if self.strategy == "decomposition":
            sub_queries = self.agent.decompose(query)
            reformulated = " | ".join(sub_queries)
        else:
            reformulated = self.agent.reformulate(query)

        docs = self.retrieve(query)
        context = "\n\n---\n\n".join(d.page_content for d in docs)

        chain = ANSWER_PROMPT | self.llm
        response = chain.invoke({"context": context, "question": query})

        return {
            "query": query,
            "reformulated_query": reformulated,
            "retrieved_docs": docs,
            "answer": response.content,
            "pipeline": f"enhanced_{self.strategy}",
        }
