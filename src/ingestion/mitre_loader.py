"""
Loads MITRE ATT&CK data from the local CTI repo or directly from GitHub.
Clone first: git clone https://github.com/mitre/cti.git data/raw/cti
"""

import json
import os
from pathlib import Path
from typing import List
from langchain_core.documents import Document


def load_mitre_attack(cti_path: str = "./data/raw/cti") -> List[Document]:
    """
    Parses MITRE ATT&CK Enterprise STIX bundles into LangChain Documents.
    Each technique becomes one document with metadata.
    """
    enterprise_path = Path(cti_path) / "enterprise-attack" / "enterprise-attack.json"

    if not enterprise_path.exists():
        raise FileNotFoundError(
            f"MITRE CTI repo not found at {enterprise_path}.\n"
            "Run: git clone https://github.com/mitre/cti.git data/raw/cti"
        )

    with open(enterprise_path, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    documents = []
    for obj in bundle.get("objects", []):
        if obj.get("type") != "attack-pattern":
            continue

        name = obj.get("name", "Unknown Technique")
        description = obj.get("description", "")
        technique_id = _extract_technique_id(obj)
        tactics = [p["phase_name"] for p in obj.get("kill_chain_phases", [])]
        platforms = obj.get("x_mitre_platforms", [])

        if not description:
            continue

        content = (
            f"Technique: {name}\n"
            f"ID: {technique_id}\n"
            f"Tactics: {', '.join(tactics)}\n"
            f"Platforms: {', '.join(platforms)}\n\n"
            f"{description}"
        )

        documents.append(Document(
            page_content=content,
            metadata={
                "source": "mitre_attack",
                "technique_id": technique_id,
                "technique_name": name,
                "tactics": tactics,
                "platforms": platforms,
            }
        ))

    print(f"[MITRE] Loaded {len(documents)} ATT&CK techniques.")
    return documents


def _extract_technique_id(obj: dict) -> str:
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id", "Unknown")
    return "Unknown"
