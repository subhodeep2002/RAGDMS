"""
Run this script once to build the vector store from all data sources.

Usage:
    python ingest.py

Sources used:
    1. MITRE ATT&CK  (requires: git clone https://github.com/mitre/cti.git data/raw/cti)
    2. NVD CVEs       (downloaded automatically via API)
    3. CISA KEV       (downloaded automatically)
"""

import sys
from src.ingestion.mitre_loader import load_mitre_attack
from src.ingestion.nvd_loader import fetch_nvd_cves
from src.ingestion.cisa_loader import load_cisa_kev
from src.ingestion.chunker import chunk_documents
from src.vectorstore.store import build_vectorstore


def main():
    all_docs = []

    # --- MITRE ATT&CK ---
    try:
        mitre_docs = load_mitre_attack("./data/raw/cti")
        all_docs.extend(mitre_docs)
    except FileNotFoundError as e:
        print(f"[WARN] Skipping MITRE: {e}")

    # --- NVD CVEs (security-relevant keywords) ---
    try:
        nvd_docs = fetch_nvd_cves(
            max_cves=500,
            keyword_search="network intrusion privilege escalation remote code execution",
            save_path="./data/raw/nvd_cves.json",
        )
        all_docs.extend(nvd_docs)
    except Exception as e:
        print(f"[WARN] Skipping NVD: {e}")

    # --- CISA KEV ---
    try:
        cisa_docs = load_cisa_kev("./data/raw/cisa_kev.json")
        all_docs.extend(cisa_docs)
    except Exception as e:
        print(f"[WARN] Skipping CISA: {e}")

    if not all_docs:
        print("[ERROR] No documents loaded. Check data sources.")
        sys.exit(1)

    print(f"\n[Ingest] Total documents loaded: {len(all_docs)}")

    # Chunk and embed
    chunks = chunk_documents(all_docs)
    build_vectorstore(chunks)

    print("\n[Ingest] Done! Vector store is ready.")
    print("Next step: python benchmark.py")


if __name__ == "__main__":
    main()
