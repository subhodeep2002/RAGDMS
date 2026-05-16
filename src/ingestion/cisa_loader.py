"""
Loads CISA Known Exploited Vulnerabilities (KEV) catalog.
Downloads the official JSON feed — no scraping needed.
"""

import json
import os
import requests
from pathlib import Path
from typing import List
from langchain_core.documents import Document


CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


def load_cisa_kev(save_path: str = "./data/raw/cisa_kev.json") -> List[Document]:
    """
    Downloads and parses the CISA KEV catalog.
    Each entry = one document describing an actively exploited vulnerability.
    """
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    if not os.path.exists(save_path):
        print("[CISA] Downloading KEV catalog...")
        response = requests.get(CISA_KEV_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        with open(save_path, "w") as f:
            json.dump(data, f)
        print(f"[CISA] Saved to {save_path}")
    else:
        print(f"[CISA] Loading cached KEV catalog from {save_path}")
        with open(save_path, "r") as f:
            data = json.load(f)

    vulnerabilities = data.get("vulnerabilities", [])
    documents = []

    for vuln in vulnerabilities:
        cve_id = vuln.get("cveID", "Unknown")
        vendor = vuln.get("vendorProject", "")
        product = vuln.get("product", "")
        vuln_name = vuln.get("vulnerabilityName", "")
        description = vuln.get("shortDescription", "")
        action = vuln.get("requiredAction", "")
        date_added = vuln.get("dateAdded", "")
        due_date = vuln.get("dueDate", "")

        content = (
            f"CVE ID: {cve_id}\n"
            f"Vulnerability: {vuln_name}\n"
            f"Vendor/Product: {vendor} / {product}\n"
            f"Date Added to KEV: {date_added}\n"
            f"Remediation Due: {due_date}\n\n"
            f"Description: {description}\n\n"
            f"Required Action: {action}"
        )

        documents.append(Document(
            page_content=content,
            metadata={
                "source": "cisa_kev",
                "cve_id": cve_id,
                "vendor": vendor,
                "product": product,
                "date_added": date_added,
            }
        ))

    print(f"[CISA] Loaded {len(documents)} KEV entries.")
    return documents
