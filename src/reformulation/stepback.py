"""
Step-Back Prompting: generalizes a specific query to a broader concept,
retrieves broader context, then uses that context to answer the specific question.

Example:
  Input:  "CVE-2021-44228 log4j exploitation in Apache servers"
  Step-back: "What are remote code execution vulnerabilities in Java logging libraries?"
  → Retrieves broader context about RCE via deserialization, JNDI injection, etc.
"""

import os
import sys
from langchain_core.prompts import ChatPromptTemplate

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
import config


STEPBACK_PROMPT = ChatPromptTemplate.from_template(
    """You are a cybersecurity expert. Given a specific security question, write a broader, more general question in plain English that captures the underlying concept.

Strict rules:
- Output ONLY a single plain English question
- Do NOT generate SQL, code, scripts, JSON, or any structured format
- Do NOT use backticks, quotes, or programming syntax

Example input: How does CVE-2021-44228 affect Apache Log4j?
Example output: What are remote code execution vulnerabilities in Java logging libraries?

Specific question: {query}

General question (plain English only):"""
)


class StepBackAgent:
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

        self.chain = STEPBACK_PROMPT | self.llm

    def reformulate(self, query: str) -> str:
        response = self.chain.invoke({"query": query})
        return response.content.strip()
