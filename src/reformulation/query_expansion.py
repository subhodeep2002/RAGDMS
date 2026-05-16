"""
Query Expansion: enriches a vague query with security-domain terminology
before retrieval to improve recall.

Example:
  Input:  "weird traffic on my network"
  Output: "anomalous network traffic patterns indicating lateral movement,
           port scanning, or C2 beaconing in network intrusion detection"
"""

import os
import sys
from langchain_core.prompts import ChatPromptTemplate

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
import config


EXPANSION_PROMPT = ChatPromptTemplate.from_template(
    """You are a defensive security expert. Rewrite the following query into a clear, natural English sentence that is more precise and includes relevant cybersecurity terminology.

Strict rules:
- Output ONLY a single plain English sentence or short paragraph
- Do NOT generate SQL, code, scripts, JSON, or any structured format
- Do NOT use backticks, quotes, or programming syntax
- Add relevant MITRE ATT&CK technique names, attack categories, or threat behaviors in plain English
- Keep the original intent intact

Example input: something weird in my network traffic
Example output: anomalous network traffic patterns suggesting lateral movement, port scanning, command and control beaconing, or data exfiltration as described in MITRE ATT&CK techniques T1046 and T1071

Original query: {query}

Rewritten query (plain English only):"""
)


class QueryExpansionAgent:
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

        self.chain = EXPANSION_PROMPT | self.llm

    def reformulate(self, query: str) -> str:
        response = self.chain.invoke({"query": query})
        reformulated = response.content.strip()
        return reformulated
