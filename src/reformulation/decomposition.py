"""
Sub-query Decomposition: breaks a complex multi-part query into simpler
sub-queries, retrieves docs for each, then merges results.

Example:
  Input:  "How do I detect and respond to ransomware on Windows?"
  Sub-queries:
    1. "How to detect ransomware activity on Windows systems?"
    2. "How to respond to and recover from a ransomware attack?"
"""

import os
import sys
from typing import List
from langchain_core.prompts import ChatPromptTemplate

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
import config


DECOMPOSE_PROMPT = ChatPromptTemplate.from_template(
    """You are a cybersecurity expert. Break the following security question into 2-4 simpler plain English sub-questions.

Strict rules:
- Output ONLY a numbered list of plain English questions
- Do NOT generate SQL, code, scripts, JSON, or any structured format
- Do NOT use backticks, quotes, or programming syntax
- Each question must be a simple natural language sentence

Example input: How do I detect and respond to ransomware on Windows?
Example output:
1. What are the signs of ransomware activity on a Windows system?
2. Which Windows event logs show ransomware behavior?
3. How should an organization respond after a ransomware infection?

Question: {query}

Sub-questions (plain English only):"""
)


class SubQueryDecompositionAgent:
    def __init__(self):
        if config.LLM_PROVIDER == "ollama":
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(model=config.LLM_MODEL, base_url=config.OLLAMA_BASE_URL, temperature=0)
        elif config.LLM_PROVIDER == "anthropic":
            from langchain_anthropic import ChatAnthropic
            self.llm = ChatAnthropic(model=config.LLM_MODEL, temperature=0)
        else:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(model=config.LLM_MODEL, temperature=0)

        self.chain = DECOMPOSE_PROMPT | self.llm

    def decompose(self, query: str) -> List[str]:
        """Returns a list of sub-queries."""
        response = self.chain.invoke({"query": query})
        lines = response.content.strip().split("\n")
        sub_queries = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Strip numbering like "1.", "1)", "-"
            for prefix in ["1.", "2.", "3.", "4.", "1)", "2)", "3)", "4)", "-", "*"]:
                if line.startswith(prefix):
                    line = line[len(prefix):].strip()
                    break
            if line:
                sub_queries.append(line)
        return sub_queries

    def reformulate(self, query: str) -> str:
        """Returns all sub-queries joined — used for single-query retrieval interface."""
        sub_queries = self.decompose(query)
        return " | ".join(sub_queries)
