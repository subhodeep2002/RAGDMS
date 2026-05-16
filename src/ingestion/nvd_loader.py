"""
Downloads and parses NVD CVE JSON feeds.
Uses the NVD 2.0 API (no API key needed for low-rate requests).
"""

import json
import os
import time
import requests
from pathlib import Path
from typing import List
from langchain_core.documents import Document


NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def fetch_nvd_cves(
    results_per_page: int = 200,
    max_cves: int = 500,
    keyword_search: str = None,
    save_path: str = "./data/raw/nvd_cves.json",
) -> List[Document]:
    """
    Fetches CVEs from the NVD 2.0 API and returns LangChain Documents.
    Optionally filter by keyword (e.g. "network intrusion", "privilege escalation").
    """
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    # Use cached data if available
    if os.path.exists(save_path):
        print(f"[NVD] Loading cached CVEs from {save_path}")
        with open(save_path, "r") as f:
            raw_items = json.load(f)
        return _parse_cve_items(raw_items)

    all_items = []
    start_index = 0

    print(f"[NVD] Fetching up to {max_cves} CVEs from NVD API...")

    while len(all_items) < max_cves:
        params = {
            "resultsPerPage": min(results_per_page, max_cves - len(all_items)),
            "startIndex": start_index,
        }
        if keyword_search:
            params["keywordSearch"] = keyword_search

        response = requests.get(NVD_API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        items = data.get("vulnerabilities", [])
        if not items:
            break

        all_items.extend(items)
        start_index += len(items)

        total_results = data.get("totalResults", 0)
        print(f"[NVD] Fetched {len(all_items)}/{min(max_cves, total_results)} CVEs")

        if start_index >= total_results:
            break

        time.sleep(0.6)  # NVD rate limit: ~5 req/30s without API key

    with open(save_path, "w") as f:
        json.dump(all_items, f)

    return _parse_cve_items(all_items)


def _parse_cve_items(items: list) -> List[Document]:
    documents = []
    for item in items:
        cve = item.get("cve", {})
        cve_id = cve.get("id", "Unknown")

        descriptions = cve.get("descriptions", [])
        description = next(
            (d["value"] for d in descriptions if d.get("lang") == "en"), ""
        )
        if not description:
            continue

        metrics = cve.get("metrics", {})
        cvss_score = _extract_cvss_score(metrics)

        weaknesses = [
            desc["value"]
            for w in cve.get("weaknesses", [])
            for desc in w.get("description", [])
            if desc.get("lang") == "en"
        ]

        content = (
            f"CVE ID: {cve_id}\n"
            f"CVSS Score: {cvss_score}\n"
            f"Weaknesses: {', '.join(weaknesses)}\n\n"
            f"{description}"
        )

        documents.append(Document(
            page_content=content,
            metadata={
                "source": "nvd_cve",
                "cve_id": cve_id,
                "cvss_score": cvss_score,
                "weaknesses": weaknesses,
            }
        ))

    print(f"[NVD] Parsed {len(documents)} CVE documents.")
    return documents


def _extract_cvss_score(metrics: dict) -> str:
    for version in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
        entries = metrics.get(version, [])
        if entries:
            return str(entries[0].get("cvssData", {}).get("baseScore", "N/A"))
    return "N/A"
