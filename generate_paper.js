const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  ImageRun,
  AlignmentType,
  BorderStyle,
  WidthType,
  ShadingType,
  VerticalAlign,
  SectionType,
} = require("docx");
const fs = require("fs");
const path = require("path");

const TNR = "Times New Roman";
const OUT_PATH = path.join(__dirname, "research_paper_IEEE.docx");
const IMG_DIR = path.join(__dirname, "images");
const imageFiles = fs
  .readdirSync(IMG_DIR)
  .filter((name) => /\.(png|jpg|jpeg)$/i.test(name))
  .sort();

// A4 with IEEE-like margins
const PAGE_W = 11906;
const PAGE_H = 16838;
const MARGIN = { top: 1080, bottom: 1080, left: 900, right: 900 };
const CONTENT_W = PAGE_W - MARGIN.left - MARGIN.right;  // 10106 DXA — full single-column width
const COL_GAP = 360;
const COL_W = Math.floor((CONTENT_W - COL_GAP) / 2);   // 4873 DXA — each two-column width

const JUST = AlignmentType.JUSTIFIED;
const CTR = AlignmentType.CENTER;
const LEFT = AlignmentType.LEFT;

const run = (text, opts = {}) =>
  new TextRun({ text, font: TNR, size: 20, color: "000000", ...opts });
const bold = (text, opts = {}) => run(text, { bold: true, ...opts });
const ital = (text, opts = {}) => run(text, { italics: true, ...opts });
const bital = (text, opts = {}) => run(text, { bold: true, italics: true, ...opts });

const body = (text, opts = {}) =>
  new Paragraph({
    children: [run(text)],
    alignment: JUST,
    spacing: { line: 240, after: 80 },
    indent: { firstLine: 360 },
    ...opts,
  });

const bodyRuns = (children, opts = {}) =>
  new Paragraph({
    children,
    alignment: JUST,
    spacing: { line: 240, after: 80 },
    indent: { firstLine: 360 },
    ...opts,
  });

const sectionHeading = (roman, title) =>
  new Paragraph({
    children: [bold(roman ? `${roman}. ${title}` : title, { allCaps: true })],
    alignment: CTR,
    spacing: { before: 160, after: 120, line: 240 },
  });

const subHeading = (label, title) =>
  new Paragraph({
    children: [bital(`${label}. ${title}`)],
    alignment: LEFT,
    spacing: { before: 120, after: 60, line: 240 },
  });

const smallGap = () => new Paragraph({ children: [run("")], spacing: { after: 120 } });

const THIN = { style: BorderStyle.SINGLE, size: 4, color: "999999" };
const BORDER_SET = { top: THIN, bottom: THIN, left: THIN, right: THIN };

const cell = (text, opts = {}) =>
  new TableCell({
    children: [
      new Paragraph({
        children: [run(text, { size: 18, bold: !!opts.bold, color: opts.color || "000000" })],
        alignment: opts.align || LEFT,
        spacing: { after: 0, line: 220 },
      }),
    ],
    shading: { fill: opts.fill || "FFFFFF", type: ShadingType.CLEAR },
    borders: BORDER_SET,
    margins: { top: 70, bottom: 70, left: 100, right: 100 },
    verticalAlign: VerticalAlign.CENTER,
  });

// Greyscale palette
// Header:  #2B2B2B (dark grey) with white text
// Alt row: #EBEBEB (light grey)
// Highlight: #D0D0D0 (mid grey)
const headerCell = (text) =>
  new TableCell({
    children: [
      new Paragraph({
        children: [run(text, { size: 18, bold: true, color: "FFFFFF" })],
        alignment: CTR,
        spacing: { after: 0, line: 220 },
      }),
    ],
    shading: { fill: "2B2B2B", type: ShadingType.CLEAR },
    borders: BORDER_SET,
    margins: { top: 70, bottom: 70, left: 100, right: 100 },
    verticalAlign: VerticalAlign.CENTER,
  });

const figByIndex = (index, width, height, num, caption) => {
  if (!imageFiles[index]) return [];
  const data = fs.readFileSync(path.join(IMG_DIR, imageFiles[index]));
  return [
    new Paragraph({
      children: [
        new ImageRun({
          data,
          transformation: { width, height },
          type: "png",
        }),
      ],
      alignment: CTR,
      spacing: { before: 120, after: 40 },
    }),
    new Paragraph({
      children: [ital(`Fig. ${num}. ${caption}`, { size: 18 })],
      alignment: CTR,
      spacing: { after: 120 },
    }),
  ];
};

const refs = [
  "[1] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Kuhn, V. Stoyanov, W. Yih, T. Rocktaschel, S. Riedel, and D. Kiela, “Retrieval-augmented generation for knowledge-intensive NLP tasks,” in Proc. NeurIPS, 2020.",
  "[2] Y. Gao, Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, Y. Dai, J. Sun, and H. Wang, “Retrieval-augmented generation for large language models: A survey,” arXiv:2312.10997, 2023.",
  "[3] L. Gao, X. Ma, J. Lin, and J. Callan, “Precise zero-shot dense retrieval without relevance labels,” in Proc. ACL, 2023.",
  "[4] H. Zheng, Z. Feng, Z. Xie, and J. Zhou, “Take a step back: Evoking reasoning via abstraction in large language models,” arXiv:2310.06117, 2023.",
  "[5] MITRE, “ATT&CK knowledge base,” 2026. [Online]. Available: https://attack.mitre.org",
  "[6] NIST, “National vulnerability database,” 2026. [Online]. Available: https://nvd.nist.gov",
  "[7] CISA, “Known exploited vulnerabilities catalog,” 2026. [Online]. Available: https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
];

const singleColumn = [
  new Paragraph({
    children: [
      bold(
        "Enhancing Retrieval Quality in RAG-Based Defensive Security Systems through Query Reformulation",
        { size: 30 }
      ),
    ],
    alignment: CTR,
    spacing: { before: 220, after: 140 },
  }),
  new Paragraph({
    children: [bold("Subhodeep Sarkar", { size: 22 })],
    alignment: CTR,
    spacing: { after: 30 },
  }),
  new Paragraph({
    children: [ital("Independent Student Research Project", { size: 18 })],
    alignment: CTR,
    spacing: { after: 30 },
  }),
  new Paragraph({
    children: [run("RAGDMS Experimental Study on Security-Oriented Retrieval-Augmented Generation", { size: 18 })],
    alignment: CTR,
    spacing: { after: 200 },
  }),
  new Paragraph({
    children: [bital("Abstract—", { size: 20 })],
    alignment: JUST,
    spacing: { after: 0, line: 240 },
    indent: { left: 360, right: 360 },
  }),
  new Paragraph({
    children: [
      ital(
        `This paper investigates whether large-language-model-based query reformulation can improve retrieval quality in defensive security retrieval-augmented generation systems. The project targets analyst-facing cybersecurity scenarios where users often ask vague questions such as 'something weird in my network traffic' while the underlying corpus contains structured terminology from MITRE ATT&CK, NVD CVE records, and CISA advisories. We build a baseline RAG pipeline and four reformulation pipelines: query expansion, hypothetical document embedding (HyDE), step-back prompting, and sub-query decomposition. The system is implemented locally with Ollama using Llama 3.2 for generation and nomic-embed-text for embeddings, with ChromaDB as the persistent vector store. Evaluation over 15 security queries -- 8 vague and 7 specific -- shows that no single pipeline dominates all metrics. HyDE achieves the best overall Recall@5 (0.259) and MRR (0.600), while Decomposition produces the most grounded answers with the highest Faithfulness (0.529). Critically, the best pipeline depends on query type: Expansion performs best on vague queries (Recall@5 = 0.150) while HyDE dominates specific queries (Recall@5 = 0.419, MRR = 0.857). Step-Back prompting is consistently the weakest strategy. The findings support a selective routing policy for real-world security systems.`
      ),
    ],
    alignment: JUST,
    spacing: { after: 100, line: 240 },
    indent: { left: 360, right: 360 },
  }),
  new Paragraph({
    children: [
      bital("Keywords—", { size: 20 }),
      ital(
        "retrieval-augmented generation, cybersecurity, query reformulation, defensive security, MITRE ATT&CK, vector search, Ollama",
        { size: 20 }
      ),
    ],
    alignment: JUST,
    spacing: { after: 180 },
    indent: { left: 360, right: 360 },
  }),
];

const twoColumn = [
  sectionHeading("I", "Introduction"),
  body(
    "Modern defensive security operations increasingly depend on fast access to large bodies of structured and semi-structured knowledge, including threat-intelligence reports, MITRE ATT&CK techniques, vulnerability records, and remediation advisories. Retrieval-Augmented Generation (RAG) offers a practical way to combine semantic retrieval with large language model reasoning so that an analyst can ask a natural-language question and receive an answer grounded in supporting evidence."
  ),
  body(
    "The central problem addressed in this project is query-document mismatch. Security analysts and students often phrase questions in vague, operational, or symptom-based language, whereas the indexed corpus is written in precise domain terminology. For example, a user may ask about “weird network traffic,” while the relevant knowledge-base entries use terms such as command-and-control, network service discovery, lateral movement, or exfiltration. When this mismatch occurs, retrieval quality drops and the final answer becomes weak or unsupported."
  ),
  bodyRuns(
    [
      run("This project therefore studies the following research question: "),
      ital("Does query reformulation using LLM-based agents improve retrieval relevance and final answer quality in defensive security RAG systems?"),
    ]
  ),
  body(
    "To answer this question, we designed and evaluated a full local cybersecurity RAG system. The system ingests defensive security knowledge, embeds it into a vector database, supports baseline and reformulated retrieval paths, and measures performance using retrieval and grounding metrics across a mixed benchmark of vague and specific security questions."
  ),

  sectionHeading("II", "Project Goal and System Overview"),
  subHeading("A", "What We Are Trying to Build"),
  body(
    "The project goal is to build an agentic AI assistant for defensive security. A user asks a cybersecurity question, the system retrieves relevant knowledge from a security corpus, and an LLM generates an answer from those retrieved documents. The experimental contribution is the addition of a query reformulation layer that tries to improve the search step before answer generation."
  ),
  subHeading("B", "Knowledge Base and Document Store"),
  body(
    "The knowledge base combines three public cybersecurity sources that are realistic and manageable for a student research project. First, MITRE ATT&CK provides structured adversary techniques, tactics, platforms, and descriptions. Second, the National Vulnerability Database provides CVE records and vulnerability descriptions. Third, the CISA Known Exploited Vulnerabilities catalog provides remediation-oriented entries for vulnerabilities observed in real-world exploitation. These sources were chunked and embedded into a persistent Chroma vector store."
  ),
  subHeading("C", "End-to-End Workflow"),
  body(
    "The full workflow has four stages. Stage 1 ingests and chunks the cybersecurity documents. Stage 2 embeds those chunks and stores them for dense retrieval. Stage 3 runs either the baseline or a reformulation strategy to retrieve top-k evidence. Stage 4 prompts the LLM to answer using the retrieved context, after which benchmark metrics are computed."
  ),

  sectionHeading("III", "Pipeline Design"),
  body(
    "Five pipelines were evaluated in this project. The baseline serves as the control condition, and four enhanced pipelines apply different query-rewriting strategies before retrieval. Table I summarizes their behavior, and the following subsections explain each one clearly."
  ),

  new Paragraph({
    children: [bold("TABLE I", { size: 18, allCaps: true })],
    alignment: CTR,
    spacing: { after: 40 },
  }),
  new Paragraph({
    children: [ital("Pipelines Evaluated in the RAGDMS System", { size: 18 })],
    alignment: CTR,
    spacing: { after: 80 },
  }),
  new Table({
    width: { size: COL_W, type: WidthType.DXA },
    columnWidths: [
      Math.floor(COL_W * 0.28),
      Math.floor(COL_W * 0.72),
    ],
    rows: [
      new TableRow({ children: [headerCell("Pipeline"), headerCell("What It Does")] }),
      new TableRow({
        children: [
          cell("Baseline"),
          cell("Uses the raw user query exactly as typed, retrieves the top security chunks, and generates an answer from those retrieved documents."),
        ],
      }),
      new TableRow({
        children: [
          cell("Expansion"),
          cell("Rewrites the raw query by adding cybersecurity language such as attack behaviors, MITRE-style terms, and detection-oriented wording."),
        ],
      }),
      new TableRow({
        children: [
          cell("HyDE"),
          cell("Generates a hypothetical answer passage first, then embeds that passage as the retrieval query so the search resembles the language of the corpus."),
        ],
      }),
      new TableRow({
        children: [
          cell("Step-Back"),
          cell("Generalizes the question to a broader security concept before retrieval so the model can pull more foundational context."),
        ],
      }),
      new TableRow({
        children: [
          cell("Decomposition"),
          cell("Breaks a complex query into smaller sub-questions, retrieves evidence for each one separately, then merges the evidence for answer generation."),
        ],
      }),
    ],
  }),
  smallGap(),

  subHeading("A", "Baseline Pipeline"),
  body(
    "The baseline pipeline is the simplest control system. A user query is embedded directly with nomic-embed-text, the top retrieved documents are loaded from ChromaDB, and Llama 3.2 answers using that evidence. This pipeline is important because it shows how well a normal RAG system performs without any extra intelligence in the query stage."
  ),
  subHeading("B", "Query Expansion"),
  body(
    "Query expansion attempts to enrich an underspecified query with security terminology. The purpose is to reduce the lexical gap between human phrasing and security documentation. For example, a vague report about unusual logins or network anomalies can be reframed using concepts such as brute force, credential stuffing, lateral movement, beaconing, or exfiltration. The intended benefit is better recall when the user does not know the correct technical phrase."
  ),
  subHeading("C", "Hypothetical Document Embedding (HyDE)"),
  body(
    "HyDE does not merely rewrite the question. Instead, it asks the LLM to generate a short hypothetical answer as though it were already a snippet from a relevant security article. That generated paragraph is then embedded and used for retrieval. The intuition is that a hypothetical article-like passage is often closer to the structure and vocabulary of real indexed documents than a short user query is."
  ),
  subHeading("D", "Step-Back Prompting"),
  body(
    "Step-back prompting transforms a narrow query into a broader conceptual question. The system tries to retrieve more general supporting knowledge that may still help answer the original problem. This can be useful when the original question is too narrow, too sparse, or expressed in a way that does not match exact corpus entries."
  ),
  subHeading("E", "Sub-Query Decomposition"),
  body(
    "Sub-query decomposition is designed for multi-part questions. Instead of sending one broad request to the retriever, the system breaks the query into smaller answerable units. Each sub-query retrieves its own evidence, and the results are merged. In principle, this should improve coverage for compound questions such as detection-plus-response or root-cause-plus-mitigation scenarios."
  ),

  sectionHeading("IV", "Experimental Setup"),
  subHeading("A", "Implementation Stack"),
  new Table({
    width: { size: COL_W, type: WidthType.DXA },
    columnWidths: [Math.floor(COL_W * 0.38), Math.floor(COL_W * 0.62)],
    rows: [
      new TableRow({ children: [headerCell("Component"), headerCell("Configuration Used")] }),
      new TableRow({ children: [cell("LLM"), cell("Llama 3.2 via Ollama")] }),
      new TableRow({ children: [cell("Embedding model"), cell("nomic-embed-text via Ollama")] }),
      new TableRow({ children: [cell("Vector store"), cell("ChromaDB persistent store")] }),
      new TableRow({ children: [cell("Framework"), cell("LangChain-based project structure with custom ingestion and evaluation modules")] }),
      new TableRow({ children: [cell("Corpus sources"), cell("MITRE ATT&CK, NVD CVE data, and CISA KEV advisories")] }),
      new TableRow({ children: [cell("Benchmark queries"), cell("15 total: 8 vague queries and 7 specific queries")] }),
      new TableRow({ children: [cell("Retrieval depth"), cell("Top-5 documents per query")] }),
    ],
  }),
  smallGap(),
  subHeading("B", "Benchmark Dataset"),
  body(
    "The benchmark dataset contains 15 cybersecurity questions with manually written ground-truth answers and keyword sets. Eight questions are vague, symptom-style analyst queries such as “something weird in my network traffic” or “admin account doing things at 3am.” Seven are specific technical questions such as “How does Pass-the-Hash work?” and “How does DMARC protect against email spoofing?” This split allows the paper to study not only whether reformulation helps, but also when it helps."
  ),
  subHeading("C", "Evaluation Metrics"),
  body(
    "Four metrics were used. Recall@5 measures whether the retriever found relevant material within the top five documents. MRR measures how early the first relevant result appears in the ranking. Answer overlap is a lexical proxy for answer accuracy relative to the prepared ground-truth answer. Faithfulness measures whether the generated answer appears grounded in the retrieved context rather than unsupported model memory."
  ),

  sectionHeading("V", "Results"),
  body(
    "Table II reports the mean scores across all 15 benchmark queries. HyDE achieved the highest Recall@5 (0.259) and MRR (0.600), making it the best overall retrieval pipeline. Decomposition achieved the highest Faithfulness (0.529), meaning its answers stay closest to the retrieved documents. Step-Back is consistently the weakest across all metrics. Importantly, no single pipeline wins on every metric — the best choice depends on the query type and what the system optimizes for."
  ),
  new Paragraph({
    children: [bold("TABLE II", { size: 18, allCaps: true })],
    alignment: CTR,
    spacing: { after: 40 },
  }),
  new Paragraph({
    children: [ital("Mean Benchmark Scores Across All 15 Queries", { size: 18 })],
    alignment: CTR,
    spacing: { after: 80 },
  }),
  new Table({
    width: { size: COL_W, type: WidthType.DXA },
    columnWidths: [
      Math.floor(COL_W * 0.30),
      Math.floor(COL_W * 0.17),
      Math.floor(COL_W * 0.17),
      Math.floor(COL_W * 0.18),
      Math.floor(COL_W * 0.18),
    ],
    rows: [
      new TableRow({
        children: [
          headerCell("Pipeline"),
          headerCell("Recall@5"),
          headerCell("MRR"),
          headerCell("Ans. Overlap"),
          headerCell("Faithfulness"),
        ],
      }),
      new TableRow({ children: [cell("Baseline"),      cell("0.177", { align: CTR }),                    cell("0.400", { align: CTR }),                    cell("0.086", { align: CTR }),                    cell("0.302", { align: CTR })] }),
      new TableRow({ children: [cell("Expansion"),     cell("0.167", { align: CTR }),                    cell("0.417", { align: CTR }),                    cell("0.066", { align: CTR }),                    cell("0.338", { align: CTR })] }),
      new TableRow({ children: [cell("HyDE"),          cell("0.259", { align: CTR, fill: "D8D8D8" }),    cell("0.600", { align: CTR, fill: "D8D8D8" }),    cell("0.085", { align: CTR, fill: "D8D8D8" }),    cell("0.375", { align: CTR, fill: "D8D8D8" })] }),
      new TableRow({ children: [cell("Step-Back"),     cell("0.114", { align: CTR }),                    cell("0.300", { align: CTR }),                    cell("0.057", { align: CTR }),                    cell("0.206", { align: CTR })] }),
      new TableRow({ children: [cell("Decomposition"), cell("0.172", { align: CTR }),                    cell("0.372", { align: CTR }),                    cell("0.075", { align: CTR }),                    cell("0.529", { align: CTR, fill: "D8D8D8" })] }),
    ],
  }),
  smallGap(),

  new Paragraph({
    children: [bold("TABLE III", { size: 18, allCaps: true })],
    alignment: CTR,
    spacing: { after: 40 },
  }),
  new Paragraph({
    children: [ital("Recall@5 by Query Category", { size: 18 })],
    alignment: CTR,
    spacing: { after: 80 },
  }),
  new Table({
    width: { size: COL_W, type: WidthType.DXA },
    columnWidths: [
      Math.floor(COL_W * 0.28),
      Math.floor(COL_W * 0.18),
      Math.floor(COL_W * 0.18),
      Math.floor(COL_W * 0.36),
    ],
    rows: [
      new TableRow({ children: [headerCell("Pipeline"), headerCell("Vague Recall@5"), headerCell("Specific Recall@5"), headerCell("Verdict")] }),
      new TableRow({ children: [cell("Baseline"),      cell("0.056 ❌ worst", { align: CTR }),             cell("0.314", { align: CTR }),                       cell("Fails on vague; solid on specific")] }),
      new TableRow({ children: [cell("Expansion"),     cell("0.150 ✓ best",  { align: CTR, fill: "D8D8D8" }), cell("0.186", { align: CTR }),                   cell("Best for vague queries — route here")] }),
      new TableRow({ children: [cell("HyDE"),          cell("0.119", { align: CTR }),                       cell("0.419 ✓ best", { align: CTR, fill: "D8D8D8" }), cell("Best for specific queries — route here")] }),
      new TableRow({ children: [cell("Step-Back"),     cell("0.088", { align: CTR }),                       cell("0.145 ❌ worst", { align: CTR }),              cell("Consistently worst — avoid")] }),
      new TableRow({ children: [cell("Decomposition"), cell("0.119", { align: CTR }),                       cell("0.233", { align: CTR }),                       cell("High faithfulness (0.529) but mid recall")] }),
    ],
  }),
  smallGap(),

  subHeading("A", "What the Results Actually Show"),
  body(
    "The results reveal three distinct findings. First, HyDE is the best overall retrieval pipeline (Recall@5 = 0.259, MRR = 0.600) because its hypothetical passage naturally matches the language of security documents. Second, Decomposition produces the most grounded answers (Faithfulness = 0.529) by retrieving evidence for each sub-question separately before synthesis. Third, Step-Back is consistently the weakest strategy across all metrics, suggesting that over-generalizing security queries removes the precision needed for effective retrieval."
  ),
  body(
    "Table III reveals the most actionable finding: the best pipeline depends entirely on query type. The baseline completely fails on vague queries (Recall@5 = 0.056 — nearly zero), while Expansion rescues vague queries with a Recall@5 of 0.150. For specific technical queries, HyDE dominates with Recall@5 = 0.419 and MRR = 0.857, meaning it almost always ranks the correct document first. This confirms the practical recommendation: a smart security system should classify the query type first and route accordingly."
  ),
  subHeading("B", "Qualitative Examples from the Demo"),
  body(
    "The screenshots captured during the local demonstration illustrate why the quantitative results matter. In some vague cases, reformulation produces a clearer retrieval path and a more security-aware explanation. In other cases, especially when the model invents overly specific or incorrect details, reformulation can push retrieval away from the correct evidence."
  ),
  ...figByIndex(0, 295, 180, 1, "Vague query: 'users getting locked out' — Baseline (Recall=0.25) vs. HyDE (Recall=0.50). HyDE generates a brute-force-oriented passage that matches ATT&CK T1110."),
  ...figByIndex(4, 295, 180, 2, "Specific query: MITRE ATT&CK ransomware techniques — Baseline achieves Recall=0.75, MRR=1.00. HyDE hallucinated wrong technique IDs and scored Recall=0.00."),
  ...figByIndex(6, 295, 110, 3, "Final benchmark summary table from terminal showing mean scores across all 15 queries and 5 pipelines."),

  sectionHeading("VI", "Discussion"),
  subHeading("A", "Why HyDE Worked Best Overall"),
  body(
    "HyDE worked well because the LLM generates a hypothetical answer written in the same style as security knowledge base documents — structured, technical, and terminology-rich. This makes the embedding of the hypothetical passage semantically close to real indexed entries. HyDE is especially effective for specific queries (Recall@5 = 0.419, MRR = 0.857) because precise security questions have well-defined answers that the LLM can approximate faithfully. The risk is hallucination: if the LLM invents incorrect technique IDs, the retrieval fails entirely."
  ),
  subHeading("B", "Why Expansion Wins on Vague Queries"),
  body(
    "Query Expansion is the best strategy for vague, symptom-based queries (Recall@5 = 0.150 vs. baseline 0.056). When a user asks about 'weird network traffic,' expansion adds terms like lateral movement, C2 beaconing, and port scanning — bridging the gap between informal language and security corpus terminology. However, expansion can suffer from prompt drift when the local LLM generates SQL-like or overly structured reformulations, which degraded performance in earlier runs before prompt engineering corrections."
  ),
  subHeading("C", "Why Decomposition Has the Best Faithfulness"),
  body(
    "Decomposition achieves the highest faithfulness (0.529) because it retrieves separate evidence for each sub-question before synthesis. The generated answer is therefore composed from multiple grounded retrieval results rather than relying on model memory. This makes decomposition ideal when answer verifiability is more important than retrieval speed — a relevant trade-off in security audit and compliance scenarios."
  ),
  subHeading("D", "Why Step-Back Consistently Fails"),
  body(
    "Step-Back prompting was the weakest strategy across both vague and specific queries. Generalizing security questions loses the precise terminology needed for effective retrieval. For example, stepping back from 'How does Pass-the-Hash work?' to 'How do attackers use stolen credentials?' retrieves broad credential-related documents rather than the specific NTLM/NTLM lateral movement entries that answer the original question."
  ),
  subHeading("C", "Limitations"),
  body(
    "This is a compact student research benchmark, so several limitations remain. The query set contains 15 examples rather than a large industrial testbed. Answer overlap is only a proxy for full factual correctness. Ground-truth relevance is based on prepared keyword sets rather than expert annotation. Finally, the system uses a local lightweight model through Ollama, so larger models may change the quality of reformulation."
  ),

  sectionHeading("VII", "Conclusion"),
  body(
    "This paper presented a complete defensive security RAG prototype and evaluated whether LLM-based query reformulation improves retrieval quality across five pipelines and 15 benchmark queries. The answer is clear but nuanced: no single pipeline is best for everything. HyDE achieves the highest overall Recall@5 (0.259) and MRR (0.600), Expansion is best for vague queries (Recall@5 = 0.150), HyDE dominates specific queries (Recall@5 = 0.419, MRR = 0.857), Decomposition produces the most grounded answers (Faithfulness = 0.529), and Step-Back is consistently the weakest strategy. To the best of our knowledge, this is among the first studies to evaluate these reformulation strategies specifically on defensive security knowledge bases with vague versus specific analyst queries. The key practical recommendation is a selective routing policy: classify the query type first, then apply the appropriate pipeline rather than applying reformulation blindly."
  ),
  body(
    "Future work can extend this project with a larger labeled benchmark, log-centric datasets, stronger local models, and an adaptive controller that chooses among baseline, HyDE, expansion, or decomposition based on the incoming question."
  ),

  sectionHeading("", "Acknowledgment"),
  body(
    "This paper is based on the implementation, benchmarking, and local demonstration carried out in the RAGDMS project workspace. The work used public security knowledge sources and local Ollama-based inference to preserve an offline experimental workflow."
  ),

  sectionHeading("", "References"),
  ...refs.map(
    (text) =>
      new Paragraph({
        children: [run(text, { size: 18 })],
        alignment: JUST,
        spacing: { line: 220, after: 50 },
        indent: { left: 360, hanging: 360 },
      })
  ),
];

const doc = new Document({
  styles: {
    default: {
      document: {
        run: {
          font: TNR,
          size: 20,
          color: "000000",
        },
      },
    },
  },
  sections: [
    {
      properties: {
        type: SectionType.CONTINUOUS,
        page: { size: { width: PAGE_W, height: PAGE_H }, margin: MARGIN },
      },
      children: singleColumn,
    },
    {
      properties: {
        type: SectionType.CONTINUOUS,
        page: { size: { width: PAGE_W, height: PAGE_H }, margin: MARGIN },
        column: {
          count: 2,
          space: COL_GAP,
          equalWidth: true,
          separate: false,
        },
      },
      children: twoColumn,
    },
  ],
});

Packer.toBuffer(doc)
  .then((buffer) => {
    fs.writeFileSync(OUT_PATH, buffer);
    console.log(`Saved research paper to ${OUT_PATH}`);
    console.log(`Embedded ${imageFiles.length} image(s) from ${IMG_DIR}`);
  })
  .catch((error) => {
    console.error("Failed to generate paper:", error);
    process.exit(1);
  });
