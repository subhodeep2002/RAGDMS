"""
Runs the full benchmark comparing baseline vs all enhanced RAG pipelines.

Usage:
    python benchmark.py

Output:
    data/results.csv  — per-query metrics for all pipelines
    Console summary   — mean scores grouped by pipeline and query category
"""

from src.evaluation.benchmark import run_benchmark

if __name__ == "__main__":
    run_benchmark(
        queries_path="./data/queries/test_queries.json",
        strategies=["expansion", "hyde", "stepback", "decomposition"],
        output_csv="./data/results.csv",
    )
