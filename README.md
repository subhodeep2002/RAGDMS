# Enhancing Retrieval Quality in RAG-Based Defensive Security Systems through Query Reformulation

**Group No. 29** — Agentic AI Project

**Author:** Subhodeep Sarkar - 253000118 |  Nitish Kumar Bind - 253000112 |  Anurag Kumar Sahu - 253000104

---

## What This Project Does

This project builds a **Retrieval-Augmented Generation (RAG)** system for defensive cybersecurity and tests whether **rewriting user queries before searching** improves the quality of retrieved documents and generated answers.

Security analysts often ask vague questions like *"something weird in my network traffic"* while the knowledge base contains precise technical documents using terms like *"lateral movement"*, *"C2 beaconing"*, or *"T1046 Network Service Discovery"*. This gap causes poor retrieval. Query reformulation agents bridge this gap.

---

## Research Question

> *Does query reformulation using LLM-based agents improve retrieval relevance and final answer accuracy in defensive security RAG systems?*

---

## Project Structure

```
RAGDMS/
│
├── src/
│   ├── ingestion/
│   │   ├── mitre_loader.py        # Loads MITRE ATT&CK techniques
│   │   ├── nvd_loader.py          # Fetches NVD CVE records
│   │   ├── cisa_loader.py         # Downloads CISA KEV catalog
│   │   └── chunker.py             # Splits documents for embedding
│   │
│   ├── vectorstore/
│   │   └── store.py               # Builds and loads ChromaDB vector store
│   │
│   ├── rag/
│   │   ├── baseline.py            # Baseline RAG pipeline (no reformulation)
│   │   └── enhanced.py            # Enhanced RAG pipeline (with reformulation)
│   │
│   ├── reformulation/
│   │   ├── query_expansion.py     # Strategy 1: adds security terminology
│   │   ├── hyde.py                # Strategy 2: generates hypothetical document
│   │   ├── stepback.py            # Strategy 3: generalizes the query
│   │   └── decomposition.py       # Strategy 4: breaks query into sub-questions
│   │
│   └── evaluation/
│       ├── metrics.py             # Recall@k, MRR, Answer Overlap, Faithfulness
│       └── benchmark.py           # Runs all pipelines and saves results
│
├── data/
│   ├── raw/                       # Downloaded raw data (MITRE, NVD, CISA)
│   ├── chroma_db/                 # Persistent ChromaDB vector store
│   ├── queries/
│   │   └── test_queries.json      # 15 benchmark queries with ground truth
│   └── results.csv                # Benchmark output (generated after running)
│
├── images/                        # Screenshots from demo runs
├── notebooks/
│   └── analysis.ipynb             # Jupyter notebook for results visualisation
├── tests/
│   └── test_pipelines.py          # Unit tests for evaluation metrics
│
├── ingest.py                      # STEP 1 — Build the knowledge base
├── benchmark.py                   # STEP 2 — Run the full evaluation
├── demo.py                        # Presentation demo (clean formatted output)
├── query.py                       # Interactive CLI for manual querying
├── generate_paper.js              # Generates IEEE research paper (.docx)
├── config.py                      # All configuration settings
├── .env                           # Environment variables (LLM, embedding config)
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## Knowledge Base Sources

| Source | What it contains | Size |
|---|---|---|
| MITRE ATT&CK | Adversary techniques, tactics, detection guidance | ~778 techniques |
| NVD CVE Feed | Vulnerability records with CVSS scores | ~500 CVEs |
| CISA KEV Catalog | Actively exploited vulnerabilities | ~1,119 entries |
| **Total** | **Chunked into vector store** | **~6,300+ chunks** |

---

## The 5 Pipelines

| Pipeline | What it does |
|---|---|
| **Baseline** | Uses the raw user query directly for retrieval — no rewriting |
| **Query Expansion** | Rewrites the query by adding cybersecurity terminology |
| **HyDE** | Generates a fake answer first, then searches using that |
| **Step-Back** | Generalises the query to a broader concept before searching |
| **Decomposition** | Breaks the query into 2–4 sub-questions and merges results |

---

## Tech Stack

| Component | Tool Used |
|---|---|
| LLM (generation + reformulation) | Llama 3.2 via Ollama (local, no API key) |
| Embedding model | nomic-embed-text via Ollama |
| Vector store | ChromaDB (persistent, local) |
| Framework | LangChain 0.3.25 |
| Evaluation | Custom metrics (Recall@k, MRR, Faithfulness) |
| Paper generation | Node.js + docx library |

---

## How to Run — Step by Step

### Prerequisites

```bash
# 1. Install Ollama from https://ollama.com and pull models
ollama pull llama3.2
ollama pull nomic-embed-text

# 2. Install Python dependencies
pip3 install -r requirements.txt

# 3. Install Node.js dependencies (for paper generation only)
export PATH="/opt/homebrew/bin:$PATH"
npm install
```

### Step 1 — Build the Knowledge Base

```bash
# Downloads MITRE ATT&CK data first
git clone https://github.com/mitre/cti.git data/raw/cti

# Ingests all sources and builds the vector store (~10-15 min)
python3 ingest.py
```

### Step 2 — Run the Benchmark

```bash
# Runs all 15 queries × 5 pipelines = 75 LLM calls (~35-50 min)
python3 benchmark.py
```

Results saved to `data/results.csv`

### Step 3 — Run the Presentation Demo

```bash
python3 demo.py
```

### Step 4 — Interactive Querying

```bash
# Choose any strategy
python3 query.py --strategy baseline
python3 query.py --strategy expansion
python3 query.py --strategy hyde
python3 query.py --strategy stepback
python3 query.py --strategy decomposition
```

## Key Results

### Overall Mean Scores (15 queries)

| Pipeline | Recall@5 | MRR | Faithfulness |
|---|---|---|---|
| Baseline | 0.177 | 0.400 | 0.302 |
| Expansion | 0.167 | 0.417 | 0.338 |
| **HyDE** | **0.259** | **0.600** | 0.375 |
| Step-Back | 0.114 | 0.300 | 0.206 |
| Decomposition | 0.172 | 0.372 | **0.529** |

### By Query Type

| Query Type | Best Pipeline | Recall@5 |
|---|---|---|
| Vague queries | **Expansion** | 0.150 (vs baseline 0.056) |
| Specific queries | **HyDE** | 0.419, MRR = 0.857 |
| Most grounded answers | **Decomposition** | Faithfulness = 0.529 |
| Consistently worst | **Step-Back** | All metrics lowest |

---

## Key Findings

1. **No single pipeline wins everything** — the best choice depends on query type and optimisation goal
2. **Baseline completely fails on vague queries** (Recall@5 = 0.056 ≈ near zero)
3. **Expansion is best for vague queries** — adds missing security terminology
4. **HyDE is best for specific queries** — generates a domain-appropriate hypothetical document
5. **Decomposition produces the most grounded answers** — highest faithfulness (0.529)
6. **Step-Back is consistently the worst** — over-generalises, loses retrieval precision

### Practical Recommendation

> A real-world security system should **classify the query type first**, then route vague queries to Expansion and specific queries to HyDE — rather than applying one reformulation strategy to all queries blindly.

---

## Evaluation Metrics Explained

| Metric | What it measures |
|---|---|
| **Recall@5** | What fraction of relevant keywords appear in the top-5 retrieved documents (0 = nothing relevant found, 1.0 = all relevant) |
| **MRR** | Was the most relevant document ranked first? (1.0 = yes, first result; 0.5 = second result) |
| **Answer Overlap** | Keyword similarity between generated answer and ground-truth answer |
| **Faithfulness** | What fraction of the answer is grounded in retrieved documents vs. model memory |

---

## Benchmark Dataset

15 manually crafted security queries with ground-truth answers and keyword sets:
- **8 vague queries** — symptom-based, informal analyst language
- **7 specific queries** — precise technical questions using security terminology

Located at: `data/queries/test_queries.json`

---

## Deliverables

| Deliverable | File |
|---|---|
| Working RAG system | `src/` directory |
| Benchmark results | `data/results.csv` |
| IEEE Research Paper | `Group-29.pdf` |
| Presentation | `RAGDMS_Project_Presentation.pptx` |
| Analysis notebook | `notebooks/analysis.ipynb` |
| Unit tests | `tests/test_pipelines.py` |

---

## References

1. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," NeurIPS 2020
2. Gao et al., "RAG for Large Language Models: A Survey," arXiv:2312.10997, 2023
3. Gao et al., "Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE)," ACL 2023
4. Zheng et al., "Take a Step Back: Evoking Reasoning via Abstraction in LLMs," arXiv:2310.06117, 2023
5. MITRE Corporation, ATT&CK Knowledge Base — https://attack.mitre.org
6. NIST, National Vulnerability Database — https://nvd.nist.gov
7. CISA, Known Exploited Vulnerabilities Catalog — https://www.cisa.gov/known-exploited-vulnerabilities-catalog
