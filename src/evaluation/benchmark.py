"""
Runs the full benchmark: baseline vs all enhanced pipelines.
Saves results to CSV and prints a summary table.
"""

import os
import sys
import json
import pandas as pd
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
import config
from src.vectorstore.store import load_vectorstore
from src.rag.baseline import BaselineRAG
from src.rag.enhanced import EnhancedRAG
from src.evaluation.metrics import evaluate_result


def run_benchmark(
    queries_path: str = "./data/queries/test_queries.json",
    strategies: List[str] = ["expansion", "hyde", "stepback", "decomposition"],
    output_csv: str = "./data/results.csv",
) -> pd.DataFrame:

    with open(queries_path, "r") as f:
        test_queries = json.load(f)

    vectorstore = load_vectorstore()

    pipelines = {"baseline": BaselineRAG(vectorstore)}
    for strategy in strategies:
        pipelines[f"enhanced_{strategy}"] = EnhancedRAG(vectorstore, strategy=strategy)

    all_results = []

    for ground_truth in test_queries:
        query = ground_truth["query"]
        print(f"\n[Benchmark] Query: {query[:60]}...")

        for pipeline_name, pipeline in pipelines.items():
            print(f"  → Running {pipeline_name}")
            try:
                result = pipeline.answer(query)
                metrics = evaluate_result(result, ground_truth)
                all_results.append(metrics)
            except Exception as e:
                print(f"  [ERROR] {pipeline_name} failed: {e}")

    df = pd.DataFrame(all_results)
    df.to_csv(output_csv, index=False)
    print(f"\n[Benchmark] Results saved to {output_csv}")
    print_summary(df)
    return df


def print_summary(df: pd.DataFrame):
    """Prints mean metrics grouped by pipeline."""
    numeric_cols = ["recall_at_k", "mrr", "answer_overlap", "faithfulness"]
    summary = df.groupby("pipeline")[numeric_cols].mean().round(3)
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY — Mean Scores by Pipeline")
    print("=" * 60)
    print(summary.to_string())
    print("=" * 60)

    # Show category breakdown (vague vs specific)
    if "category" in df.columns:
        cat_summary = df.groupby(["pipeline", "category"])[numeric_cols].mean().round(3)
        print("\nBreakdown by Query Category:")
        print(cat_summary.to_string())


if __name__ == "__main__":
    run_benchmark()
