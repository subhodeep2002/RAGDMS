"""
Interactive CLI to query the RAG system.

Usage:
    python query.py                         # baseline
    python query.py --strategy expansion    # with query expansion
    python query.py --strategy hyde
    python query.py --strategy stepback
    python query.py --strategy decomposition
"""

import argparse
from src.vectorstore.store import load_vectorstore
from src.rag.baseline import BaselineRAG
from src.rag.enhanced import EnhancedRAG


def main():
    parser = argparse.ArgumentParser(description="Query the security RAG system")
    parser.add_argument(
        "--strategy",
        choices=["baseline", "expansion", "hyde", "stepback", "decomposition"],
        default="baseline",
        help="Query reformulation strategy to use",
    )
    args = parser.parse_args()

    vectorstore = load_vectorstore()

    if args.strategy == "baseline":
        pipeline = BaselineRAG(vectorstore)
    else:
        pipeline = EnhancedRAG(vectorstore, strategy=args.strategy)

    print(f"\nRAG System ready | Strategy: {args.strategy}")
    print("Type your security query (Ctrl+C to exit)\n")

    while True:
        try:
            query = input("Query: ").strip()
            if not query:
                continue
            # Strip accidental "Query:" prefix if user types it
            if query.lower().startswith("query:"):
                query = query[6:].strip()

            result = pipeline.answer(query)

            if result["reformulated_query"]:
                print(f"\nReformulated: {result['reformulated_query']}")

            print(f"\nAnswer:\n{result['answer']}")
            print(f"\n[Retrieved {len(result['retrieved_docs'])} docs]")
            print("-" * 60)

        except KeyboardInterrupt:
            print("\nGoodbye.")
            break


if __name__ == "__main__":
    main()
