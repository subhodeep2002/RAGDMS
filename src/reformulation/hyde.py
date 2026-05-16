"""
HyDE (Hypothetical Document Embedding):
Instead of embedding the query, generate a hypothetical answer document
and embed THAT — it lives in the same vector space as real docs.

Example:
  Input:  "How do attackers move laterally in Windows environments?"
  Hypothetical doc: "Attackers commonly use Pass-the-Hash, PsExec, and WMI
                     to move laterally in Windows networks..."
  → Embed the hypothetical doc for retrieval
"""

import os
import sys
from langchain_core.prompts import ChatPromptTemplate

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
import config


HYDE_PROMPT = ChatPromptTemplate.from_template(
    """You are a cybersecurity knowledge base author. Write a short, factual passage
(3-5 sentences) that would directly answer the following security question.
This passage will be used to search a document database — write it as if it is
an excerpt from a security report or knowledge base article.

Output ONLY the passage, no preamble.

Question: {query}

Passage:"""
)


class HyDEAgent:
    def __init__(self):
        if config.LLM_PROVIDER == "ollama":
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(model=config.LLM_MODEL, base_url=config.OLLAMA_BASE_URL, temperature=0.3)
        elif config.LLM_PROVIDER == "anthropic":
            from langchain_anthropic import ChatAnthropic
            self.llm = ChatAnthropic(model=config.LLM_MODEL, temperature=0.3)
        else:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(model=config.LLM_MODEL, temperature=0.3)

        self.chain = HYDE_PROMPT | self.llm

    def reformulate(self, query: str) -> str:
        """Returns a hypothetical document to use as the retrieval query."""
        response = self.chain.invoke({"query": query})
        return response.content.strip()
