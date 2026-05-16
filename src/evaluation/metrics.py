"""
Evaluation metrics for comparing baseline vs enhanced RAG pipelines.
Computes: Retrieval Recall@k, MRR, Answer Accuracy (keyword overlap), Faithfulness.
"""

import re
from typing import List, Dict
from langchain_core.documents import Document


def recall_at_k(retrieved_docs: List[Document], relevant_keywords: List[str], k: int = 5) -> float:
    """
    Measures what fraction of relevant keywords appear in the top-k retrieved docs.
    Proxy for retrieval recall when ground-truth doc IDs are unavailable.
    """
    if not relevant_keywords:
        return 0.0

    top_k_text = " ".join(d.page_content.lower() for d in retrieved_docs[:k])
    hits = sum(1 for kw in relevant_keywords if kw.lower() in top_k_text)
    return hits / len(relevant_keywords)


def reciprocal_rank(retrieved_docs: List[Document], relevant_keywords: List[str]) -> float:
    """
    Mean Reciprocal Rank: returns 1/rank of the first doc containing a relevant keyword.
    """
    for rank, doc in enumerate(retrieved_docs, start=1):
        text = doc.page_content.lower()
        if any(kw.lower() in text for kw in relevant_keywords):
            return 1.0 / rank
    return 0.0


def answer_keyword_overlap(answer: str, ground_truth: str) -> float:
    """
    Simple keyword overlap between generated answer and ground truth.
    Extracts meaningful words (length > 4) and computes Jaccard similarity.
    """
    def tokenize(text):
        words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
        return set(words)

    pred_tokens = tokenize(answer)
    truth_tokens = tokenize(ground_truth)

    if not truth_tokens:
        return 0.0

    intersection = pred_tokens & truth_tokens
    union = pred_tokens | truth_tokens
    return len(intersection) / len(union)


def faithfulness_score(answer: str, retrieved_docs: List[Document]) -> float:
    """
    Checks what fraction of sentences in the answer are grounded in retrieved docs.
    Simple heuristic: checks if key terms from each sentence appear in context.
    For production use, replace with RAGAS faithfulness metric.
    """
    context = " ".join(d.page_content.lower() for d in retrieved_docs)
    sentences = [s.strip() for s in answer.split(".") if len(s.strip()) > 20]

    if not sentences:
        return 0.0

    grounded = 0
    for sentence in sentences:
        words = re.findall(r'\b[a-zA-Z]{5,}\b', sentence.lower())
        if not words:
            continue
        hits = sum(1 for w in words if w in context)
        if hits / len(words) >= 0.5:
            grounded += 1

    return grounded / len(sentences)


def evaluate_result(result: Dict, ground_truth: Dict) -> Dict:
    """
    Runs all metrics on a single RAG result against its ground truth.
    """
    retrieved_docs = result["retrieved_docs"]
    relevant_keywords = ground_truth.get("relevant_doc_keywords", [])
    ground_truth_answer = ground_truth.get("ground_truth_answer", "")

    return {
        "query_id": ground_truth.get("id"),
        "query": result["query"],
        "category": ground_truth.get("category"),
        "pipeline": result["pipeline"],
        "reformulated_query": result.get("reformulated_query"),
        "recall_at_k": recall_at_k(retrieved_docs, relevant_keywords),
        "mrr": reciprocal_rank(retrieved_docs, relevant_keywords),
        "answer_overlap": answer_keyword_overlap(result["answer"], ground_truth_answer),
        "faithfulness": faithfulness_score(result["answer"], retrieved_docs),
    }
