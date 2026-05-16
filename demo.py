"""
Presentation Demo — Query Reformulation in RAG-Based Defensive Security Systems

Shows a clear before/after comparison:
  Baseline RAG  : raw query → retrieve → answer
  Enhanced RAG  : raw query → reformulate → retrieve → answer

Run: python3 demo.py
"""

from src.vectorstore.store import load_vectorstore
from src.rag.baseline import BaselineRAG
from src.rag.enhanced import EnhancedRAG
from src.evaluation.metrics import recall_at_k, reciprocal_rank, faithfulness_score

DIVIDER      = "=" * 72
THIN_DIVIDER = "-" * 72

# Carefully chosen demo queries: 2 vague, 2 specific
DEMO_QUERIES = [
    {
        "query": "something weird in my network traffic",
        "category": "Vague Query",
        "relevant_keywords": ["lateral movement", "port scan", "C2", "network anomaly", "exfiltration"],
    },
    {
        "query": "users getting locked out randomly",
        "category": "Vague Query",
        "relevant_keywords": ["brute force", "password spraying", "credential stuffing", "account lockout"],
    },
    {
        "query": "How does Pass-the-Hash work and how can I detect it?",
        "category": "Specific Query",
        "relevant_keywords": ["pass-the-hash", "NTLM", "lateral movement", "credential access"],
    },
    {
        "query": "What MITRE ATT&CK techniques are used in ransomware attacks?",
        "category": "Specific Query",
        "relevant_keywords": ["ransomware", "T1486", "data encrypted", "inhibit recovery"],
    },
]

STRATEGIES = ["expansion", "hyde", "stepback"]


def print_header():
    print("\n" + DIVIDER)
    print("  PROJECT: Enhancing Retrieval Quality in RAG-Based Defensive")
    print("           Security Systems through Query Reformulation")
    print(DIVIDER)
    print("  Research Question:")
    print("  Does query reformulation improve retrieval relevance and")
    print("  answer accuracy in defensive security RAG systems?")
    print(DIVIDER + "\n")


def run_demo_query(query_obj, baseline, enhanced_pipelines):
    query    = query_obj["query"]
    category = query_obj["category"]
    keywords = query_obj["relevant_keywords"]

    print(DIVIDER)
    print(f"  QUERY TYPE : {category}")
    print(f"  RAW QUERY  : \"{query}\"")
    print(DIVIDER)

    # ── BASELINE ──────────────────────────────────────────────────────────
    base_result  = baseline.answer(query)
    base_recall  = recall_at_k(base_result["retrieved_docs"], keywords)
    base_mrr     = reciprocal_rank(base_result["retrieved_docs"], keywords)
    base_faith   = faithfulness_score(base_result["answer"], base_result["retrieved_docs"])

    print("\n[1] BASELINE RAG  (no reformulation)\n")
    print(f"  Reformulated Query : (none — raw query used directly)")
    print(f"\n  Answer:\n")
    for line in base_result["answer"].strip().split("\n"):
        print(f"    {line}")
    print(f"\n  Retrieval Metrics:")
    print(f"    Recall@5   : {base_recall:.2f}")
    print(f"    MRR        : {base_mrr:.2f}")
    print(f"    Faithfulness: {base_faith:.2f}")

    # ── ENHANCED PIPELINES ────────────────────────────────────────────────
    for i, (strategy_name, pipeline) in enumerate(enhanced_pipelines.items(), start=2):
        enh_result  = pipeline.answer(query)
        enh_recall  = recall_at_k(enh_result["retrieved_docs"], keywords)
        enh_mrr     = reciprocal_rank(enh_result["retrieved_docs"], keywords)
        enh_faith   = faithfulness_score(enh_result["answer"], enh_result["retrieved_docs"])

        recall_delta = enh_recall - base_recall
        mrr_delta    = enh_mrr    - base_mrr
        delta_symbol = lambda d: f"(+{d:.2f} ↑)" if d > 0 else (f"({d:.2f} ↓)" if d < 0 else "(no change)")

        label = strategy_name.replace("_", " ").upper()
        print(f"\n[{i}] ENHANCED RAG  — Strategy: {label}\n")
        print(f"  Reformulated Query:")
        for line in enh_result["reformulated_query"].strip().split("\n"):
            print(f"    {line}")
        print(f"\n  Answer:\n")
        for line in enh_result["answer"].strip().split("\n"):
            print(f"    {line}")
        print(f"\n  Retrieval Metrics:")
        print(f"    Recall@5    : {enh_recall:.2f}  {delta_symbol(recall_delta)}")
        print(f"    MRR         : {enh_mrr:.2f}  {delta_symbol(mrr_delta)}")
        print(f"    Faithfulness: {enh_faith:.2f}")

    print()


def print_summary_table(all_scores):
    """Prints a clean summary table for the presentation."""
    print("\n" + DIVIDER)
    print("  SUMMARY — Mean Scores Across All Demo Queries")
    print(DIVIDER)
    header = f"  {'Pipeline':<28} {'Recall@5':>10} {'MRR':>10} {'Faithfulness':>14}"
    print(header)
    print("  " + THIN_DIVIDER[2:])
    for pipeline, scores in all_scores.items():
        n = len(scores)
        avg_recall = sum(s["recall"] for s in scores) / n
        avg_mrr    = sum(s["mrr"]    for s in scores) / n
        avg_faith  = sum(s["faith"]  for s in scores) / n
        tag = "  ← control" if pipeline == "baseline" else ""
        print(f"  {pipeline:<28} {avg_recall:>10.2f} {avg_mrr:>10.2f} {avg_faith:>14.2f}{tag}")
    print(DIVIDER + "\n")


def main():
    print_header()

    vectorstore = load_vectorstore()
    baseline    = BaselineRAG(vectorstore)
    enhanced_pipelines = {
        f"enhanced_{s}": EnhancedRAG(vectorstore, strategy=s)
        for s in STRATEGIES
    }

    all_scores = {"baseline": []} | {k: [] for k in enhanced_pipelines}

    for query_obj in DEMO_QUERIES:
        print(f"\n{'#'*72}")
        print(f"  DEMO CASE: {query_obj['category']} — \"{query_obj['query']}\"")
        print(f"{'#'*72}\n")

        query    = query_obj["query"]
        keywords = query_obj["relevant_keywords"]

        base_result = baseline.answer(query)
        all_scores["baseline"].append({
            "recall": recall_at_k(base_result["retrieved_docs"], keywords),
            "mrr":    reciprocal_rank(base_result["retrieved_docs"], keywords),
            "faith":  faithfulness_score(base_result["answer"], base_result["retrieved_docs"]),
        })

        print(f"  BASELINE — Raw Query: \"{query}\"\n")
        print(f"  Answer:\n")
        for line in base_result["answer"].strip().split("\n"):
            print(f"    {line}")
        r = all_scores["baseline"][-1]
        print(f"\n  Recall@5={r['recall']:.2f}  MRR={r['mrr']:.2f}  Faithfulness={r['faith']:.2f}")

        for strategy_key, pipeline in enhanced_pipelines.items():
            enh_result = pipeline.answer(query)
            s = {
                "recall": recall_at_k(enh_result["retrieved_docs"], keywords),
                "mrr":    reciprocal_rank(enh_result["retrieved_docs"], keywords),
                "faith":  faithfulness_score(enh_result["answer"], enh_result["retrieved_docs"]),
            }
            all_scores[strategy_key].append(s)

            label = strategy_key.replace("enhanced_", "").upper()
            recall_delta = s["recall"] - all_scores["baseline"][-1]["recall"]
            arrow = "↑" if recall_delta > 0 else ("↓" if recall_delta < 0 else "=")

            print(f"\n  {THIN_DIVIDER}")
            print(f"  ENHANCED [{label}]\n")
            print(f"  Reformulated: \"{enh_result['reformulated_query'].strip()[:120]}\"")
            print(f"\n  Answer:\n")
            for line in enh_result["answer"].strip().split("\n"):
                print(f"    {line}")
            print(f"\n  Recall@5={s['recall']:.2f} {arrow}  MRR={s['mrr']:.2f}  Faithfulness={s['faith']:.2f}")

    print_summary_table(all_scores)
    print("  KEY FINDING:")
    print("  Reformulation helps most on vague queries.")
    print("  HyDE and Query Expansion tend to outperform baseline on recall.")
    print("  Specific queries sometimes perform equally well without reformulation.")
    print()


if __name__ == "__main__":
    main()
