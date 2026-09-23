# ScholarSphere: Complete Architectural & Technical Documentation

---

## 1. Executive Summary & Project Overview

### 1.1 What is ScholarSphere?
**ScholarSphere** is an end-to-end, AI-powered academic research assistant and document intelligence platform. It transforms how students, researchers, professors, and industry analysts interact with dense academic literature, research papers, technical reports, and multi-document corpuses.

Reading modern scientific publications is notoriously demanding: a single paper often spans 15 to 50 pages of dense terminology, complex methodologies, and citations. Researchers routinely struggle with:
1. **Information Overload**: Processing dozens of papers to identify core contributions and novel findings.
2. **Cross-Document Comparative Analysis**: Determining topical convergence, redundancy, or divergence between multiple papers or literature reviews.
3. **Comprehension & Knowledge Retention Assessment**: Verifying whether students or research teams have mastered complex findings.
4. **Literature Search Disconnect**: Bridging the gap between a document's internal conceptual content and external peer-reviewed literature indexed globally.

ScholarSphere solves these challenges by combining:
- **Abstractive Document Summarization** powered by sequence-to-sequence transformer architectures (`sshleifer/distilbart-cnn-6-6`).
- **High-Dimensional Semantic Document Similarity** utilizing dense vector embeddings (`all-MiniLM-L6-v2`) and cosine distance metrics.
- **Automated MCQ Assessment & Smart Distractor Generation** integrating conditional text generation (`mrm8488/t5-base-finetuned-question-generation-ap`), extractive reading comprehension (`distilbert-base-cased-distilled-squad`), WordNet lexical synsets, and semantic embedding contrast.
- **Context-Aware Topic Extraction & Academic Discovery** leveraging KeyBERT with Maximal Marginal Relevance (MMR) and the Semantic Scholar Academic Graph REST API.

---

## 2. System Architecture & Topology

ScholarSphere employs a **decoupled modern web architecture** consisting of a React Single-Page Application (SPA) frontend served via a high-performance Content Delivery Network (CDN) and a unified Python FastAPI backend running as serverless lambdas on Vercel.

### 2.1 Architectural Diagram

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT TIER                                       |
|                                                                                   |
|   +---------------------------------------------------------------------------+   |
|   |                  React 19 + Vite 8 SPA (Client Browser)                   |   |
|   |                                                                           |   |
|   |  * Document Upload (PDF, DOCX, TXT with Drag-and-Drop & Size Validation)  |   |
|   |  * Tab Navigation: Summarize | Similarity | Quiz | Research Explorer      |   |
|   |  * Export Utilities: JSON Downloader, Raw Text Viewer, Dynamic Heatmap    |   |
|   +---------------------------------------------------------------------------+   |
+------------------------------------------+----------------------------------------+
                                           |
                                           | HTTP REST Requests (/api/*)
                                           v
+-----------------------------------------------------------------------------------+
|                        VERCEL SERVERLESS EDGE INFRASTRUCTURE                      |
|                                                                                   |
|   +---------------------------------------------------------------------------+   |
|   |                      Vercel Routing & Edge Middleware                     |   |
|   |                                                                           |   |
|   |  * Static Assets: index.html, dist/assets/*, favicon.svg, logo.svg        |   |
|   |  * Edge Rewrites: /api/(.*)  --->  api/index.py                           |   |
|   |  * Runtime Engine: Large Functions (Fluid Compute, up to 5 GB bundle)     |   |
|   |  * Interpreter: CPython 3.12 managed via uv.lock                          |   |
|   +---------------------------------------------------------------------------+   |
|                                          |                                        |
|                                          v                                        |
|   +---------------------------------------------------------------------------+   |
|   |                   Unified FastAPI Application (api/index.py)              |   |
|   |                                                                           |   |
|   |   GET  /api/health       -> System Health & Availability Monitor          |   |
|   |   POST /api/summarize    -> Multi-Document Abstractive Summarization      |   |
|   |   POST /api/similarity   -> Pairwise Cross-Document Semantic Matrix       |   |
|   |   POST /api/quiz         -> Automated Contextual MCQ Generation           |   |
|   |   POST /api/research     -> MMR Keyword Extraction & Semantic Scholar API |   |
|   +--------------------------------------+------------------------------------+   |
+------------------------------------------|----------------------------------------+
                                           | Internal Module Calls
                                           v
+-----------------------------------------------------------------------------------+
|                                BACKEND SERVICE LAYER                              |
|                                                                                   |
|  +--------------------+  +---------------------+  +----------------------------+  |
|  | backend/document.py|  | backend/summary.py  |  | backend/similarity_service |  |
|  | * PyPDF2 Reader    |  | * DistilBART Pipeline| | * SentenceTransformer      |  |
|  | * python-docx      |  | * Overlapping Chunks|  | * Dense Embeddings (384-d) |  |
|  | * Text Normalizer  |  | * Recursive Merge   |  | * Scikit-Learn Cosine Sim  |  |
|  +--------------------+  +---------------------+  +----------------------------+  |
|                                                                                   |
|  +-------------------------------------+  +------------------------------------+  |
|  |      backend/quiz_service.py        |  |     backend/research_service.py    |  |
|  | * T5 Question Generation            |  | * KeyBERT (all-MiniLM-L6-v2)       |  |
|  | * DistilBERT SQuAD Answer Extractor |  | * Maximal Marginal Relevance (MMR) |  |
|  | * WordNet Synonyms + Distractors    |  | * Semantic Scholar Graph API       |  |
|  +-------------------------------------+  +------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 3. Technology Stack: Analysis, Justifications & Alternatives

| Layer | Selected Technology | Alternative Evaluated | Why Chosen | Why Alternative Rejected | Trade-Offs Accepted |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Frontend Framework** | **React 19** | **Streamlit** (Original) | Clean state isolation, modular UI components, full DOM control, asynchronous user feedback, reactive client-side validation. | Streamlit re-executes the entire script on every user interaction, causing massive server state thrashing, laggy UI updates, and tight coupling of computation and UI. | Requires client build step (`vite build`) and separate backend API management. |
| **Frontend Tooling** | **Vite 8** | **Webpack / Create React App** | Sub-second Hot Module Replacement (HMR), instant development server start via native ES modules, optimized Rollup production bundling. | Webpack / CRA suffer from slow bundle rebuilds, complex configuration overhead, and deprecated toolchains. | ESM compatibility constraints on legacy third-party dependencies. |
| **Styling** | **Vanilla CSS3** (Curated Tokens) | **Tailwind CSS / MUI** | Zero runtime overhead, complete styling independence, direct access to CSS variables, fluid glassmorphism, responsive CSS Grid/Flexbox without extra build dependencies. | Tailwind adds utility class bloat, complex post-processing plugins, and vendor lock-in. Component libraries (MUI, Chakra) inflate JavaScript bundle size (>300KB). | Requires deliberate manual naming conventions and stylesheet organization. |
| **Backend Framework** | **FastAPI 0.117** | **Flask / Django** | Native ASGI async/await concurrency, automatic OpenAPI/Swagger documentation, Pydantic type validation, high throughput. | Flask lacks native async I/O and modern typing validation. Django is a monolithic MVC framework with an unnecessary relational ORM. | ASGI lifecycle nuances on serverless cold starts. |
| **Python Package Manager** | **uv 0.10+** | **pip / pipenv / poetry** | 10x-100x faster resolution and installation written in Rust, deterministic lockfiles (`uv.lock`), direct PEP-508 index routing for CPU PyTorch wheels. | `pip` has slow resolution and defaults to enormous PyPI CUDA packages. `pipenv` is slow and has complex virtualenv lock steps. | Newer ecosystem tooling with rapidly evolving CLI flags. |
| **Deep Learning Framework** | **PyTorch CPU (`+cpu`)** | **PyTorch CUDA (Standard PyPI)** | Linux CPU wheels weigh ~180MB to 400MB unzipped, eliminating 4.5 GB of unused NVIDIA CUDA 12 binaries (`nvidia-cudnn`, `cublas`, `nccl`). | Standard PyPI wheels package full GPU runtimes exceeding cloud serverless function limits (>500MB). | Inference execution on CPU rather than GPU (offset by choosing lightweight distilled models). |
| **Summarization Model** | **DistilBART-CNN-6-6** | **Full BART-Large / GPT-4 API** | Retains ~95% of BART's summarization performance at 50% the parameter count; runs offline within serverless memory without external token fees. | BART-Large is >1.6 GB and causes function timeouts. Commercial APIs (OpenAI/Anthropic) incur high token costs and latency for large uploads. | Requires chunking pipelines for texts exceeding the 1024 token position embedding limit. |
| **Embedding Engine** | **SentenceTransformers (all-MiniLM-L6-v2)** | **OpenAI text-embedding-ada-002** | 384-dimensional dense vectors, lightweight (~80MB), fast sub-100ms CPU inference, completely private and self-contained. | Cloud embedding APIs introduce network hops, rate limits, latency overhead, and external API cost. | Lower context window (512 tokens) compared to large commercial models. |
| **Hosting Platform** | **Vercel Serverless (Fluid Compute)** | **AWS EC2 / Render / Heroku** | Seamless frontend static CDN distribution, automatic SSL, zero idle server cost, scale-to-zero economics, Vercel Large Functions (up to 5GB bundle). | Dedicated EC2 or Render instances incur 24/7 hosting charges even when idle, requiring manual OS patching, reverse proxies, and scaling groups. | Cold start initialization overhead when downloading models on a fresh instance. |

---

## 4. Repository Structure & Directory Anatomy

Below is the directory map of the ScholarSphere repository with the role of every component:

```
ScholarSphere-main/
│
├── .env.local                    # Local environment variables (OIDC, API base URLs, secrets)
├── .gitignore                    # Git ignore specifications (build artifacts, virtualenvs, cache)
├── .python-version               # Pinned Python version (3.12) for local uv/pyenv tooling
├── .vercelignore                 # Production exclusion manifest for lean Vercel deployment bundles
│
├── api/                          # Serverless API Layer (Vercel Entrypoint)
│   ├── .python-version           # Vercel entrypoint Python version pin (3.12)
│   └── index.py                  # Unified FastAPI Application (Health, Summarize, Similarity, Quiz, Research)
│
├── backend/                      # Pure Business Logic & Machine Learning Services
│   ├── __init__.py               # Python package initialization
│   ├── document.py               # Text extraction and sanitization (PDF, DOCX, TXT)
│   ├── summary_service.py        # DistilBART summarization, chunking, and merging
│   ├── similarity_service.py     # SentenceTransformer embeddings and Cosine Similarity matrix
│   ├── quiz_service.py           # T5 Question Generation + DistilBERT QA + WordNet Distractors
│   └── research_service.py       # KeyBERT MMR Topic Extraction + Semantic Scholar Graph Search
│
├── dist/                         # Compiled frontend distribution generated by Vite (static assets)
│
├── Docs/                         # Complete Project Documentation & Architecture
│   └── PROJECT_DOCUMENTATION.md  # Exhaustive technical reference & design manual
│
├── public/                       # Static Assets served at root by Vite and Vercel
│   ├── favicon.svg               # Scalable high-DPI vector icon
│   ├── favicon.ico               # Multi-resolution fallback ICO (16x16, 32x32, 48x48)
│   ├── favicon.png               # High-resolution 192x192 PNG (PWA / Apple Touch)
│   ├── favicon-32x32.png         # Standard browser tab PNG
│   └── logo.svg                  # Vector application emblem used in Header, Hero, and Footer
│
├── src/                          # React Frontend Source Code
│   ├── App.jsx                   # Main React SPA component (state, tabs, uploads, rendering)
│   ├── main.jsx                  # React DOM root bootstrapping
│   └── styles.css                # Global design system, glassmorphism tokens, and responsive layout
│
├── index.html                    # Single Page Application HTML root template & metadata
├── package.json                  # Frontend dependencies and npm scripts
├── package-lock.json             # Locked npm dependency tree
├── pyproject.toml                # Authoritative Python project definition, dependencies & uv CPU index
├── uv.lock                       # Deterministic Python dependency graph for reproducible builds
├── vercel.json                   # Vercel deployment configuration, build envs, rewrites, and lambda settings
├── vite.config.js                # Vite build and development proxy configuration
└── README.md                     # High-level repository overview
```

---

## 5. Machine Learning & NLP Deep Dive: Algorithms & Concepts

### 5.1 Abstractive Summarization Pipeline (`backend/summary_service.py`)

#### 5.1.1 The Challenge
Academic papers contain complex discourse structures, technical terminology, and long text passages that easily exceed standard transformer context windows. The baseline BART model has a hard positional embedding limit of 1024 tokens. Passing a 10,000-word document directly to a transformer model results in an immediate `IndexError` or truncation of 90% of the content.

#### 5.1.2 Algorithmic Solution: Sentence-Boundary Windowed Chunking
ScholarSphere implements an overlapping, sentence-aware chunking algorithm:
1. **Sentence Tokenization**: The raw document text is tokenized into discrete sentence units preserving punctuation boundaries (`. ` split with whitespace normalization).
2. **Token-Budget Accumulation**: Sentences are accumulated sequentially. At each sentence, the tokenizer encodes the candidate sentence and evaluates whether `current_tokens + sentence_tokens <= max_tokens` (calibrated at 850 tokens to guarantee headroom for special tokens like `<s>` and `</s>`).
3. **Chunk Boundary Dispatch**: Once adding a sentence would exceed 850 tokens, the accumulated sentences are joined into a cohesive paragraph chunk, and a new chunk begins.
4. **Adaptive Length Calculation**: For each chunk, maximum and minimum generation lengths are dynamically scaled based on the chunk's actual token count:
   $$\text{chunk\_max\_length} = \min\left(\text{max\_length}, \max\left(\text{min\_length} + 10, \lfloor \text{token\_count} \times 0.35 \rfloor\right)\right)$$
5. **Inference with Beam Search**:
   The chunk is passed through the `pipeline("summarization", model="sshleifer/distilbart-cnn-6-6", device=-1)`. Generation utilizes deterministic beam decoding (`do_sample=False`, `truncation=True`) to minimize hallucinations.
6. **Hierarchical Recursive Merge**:
   For multi-document uploads, individual document summaries are generated first, followed by a second-pass combined synthesis summarizing the concatenated summaries into an executive briefing.

---

### 5.2 Semantic Similarity & High-Dimensional Geometry (`backend/similarity_service.py`)

#### 5.2.1 Embedding Representation
Traditional keyword-based similarity algorithms (TF-IDF, BM25) rely on exact lexical overlap. If Paper A discusses *"neural network regularization techniques"* and Paper B discusses *"preventing overfitting in deep learning models"*, TF-IDF reports near-zero similarity despite identical semantic meaning.

ScholarSphere resolves this through dense vector embeddings via **Sentence-BERT (`all-MiniLM-L6-v2`)**:
- Maps variable-length text into a fixed 384-dimensional Euclidean vector space ($\mathbb{R}^{384}$).
- Captures latent conceptual, topical, and contextual semantic features.

#### 5.2.2 Mathematical Formulation
Given $N$ documents, the system first generates a focused semantic summary for each document to eliminate noise (acknowledgments, citations, boilerplate headers). The summary text is encoded into an embedding vector $\mathbf{v}_i \in \mathbb{R}^{384}$.

For every pair of documents $(i, j)$, the pairwise **Cosine Similarity** is computed:

$$\text{Cosine Similarity}(\mathbf{v}_i, \mathbf{v}_j) = \frac{\mathbf{v}_i \cdot \mathbf{v}_j}{\|\mathbf{v}_i\|_2 \|\mathbf{v}_j\|_2} = \frac{\sum_{k=1}^{384} v_{i,k} v_{j,k}}{\sqrt{\sum_{k=1}^{384} v_{i,k}^2} \sqrt{\sum_{k=1}^{384} v_{j,k}^2}}$$

This yields an $N \times N$ symmetric similarity matrix $\mathbf{S}$ where:
- $S_{i,i} = 1.0$ (perfect self-similarity).
- $S_{i,j} \in [-1, 1]$ represents semantic alignment (typically between $0.2$ and $0.95$ for academic texts).
- Rendered in the React frontend as an interactive, color-coded similarity matrix with dynamic percentage badges.

---

### 5.3 Contextual Quiz & Adversarial Distractor Generation (`backend/quiz_service.py`)

Generating valid, challenging multiple-choice questions from unstructured text requires solving two distinct problems:
1. **Generating a grammatically sound, context-relevant question and extracting the true answer**.
2. **Generating plausible false options (distractors)** that test comprehension rather than obvious trivia.

#### 5.3.1 Question-Answer Pair Synthesis
1. The text is passed to a conditional sequence-to-sequence model: `mrm8488/t5-base-finetuned-question-generation-ap`.
   - Prompt format: `"generate questions: <context>"`.
   - Generation parameters: Temperature $T = 0.7$, `max_length = 128`, producing diverse interrogative sentences.
2. The generated question is fed into an extractive reading comprehension model: `distilbert-base-cased-distilled-squad`.
   - Context: Original document text.
   - Output: Precise character span representing the ground-truth answer.

#### 5.3.2 Two-Stage Distractor Pipeline
To avoid naive or nonsensical false options, ScholarSphere uses a hybrid lexical and semantic similarity approach:
- **Stage 1 (Lexical Synonyms via WordNet)**:
  Queries WordNet synsets (`nltk.corpus.wordnet`) for the answer entity to extract related lemmas, providing candidate distractors in the same grammatical category.
- **Stage 2 (Semantic Embedding Contrast)**:
  Candidate sentences from the document that do *not* contain the true answer are embedded using `all-MiniLM-L6-v2`. The cosine similarity between the true answer and candidate sentences is calculated. The system ranks sentences to find those that are *topically related yet factually distinct*, ensuring options appear plausible to someone who has not read carefully.
- **Stage 3 (Shuffling & Formatting)**:
  Options are aggregated into a 4-choice set ($\{ \text{Answer}, \text{Distractor}_1, \text{Distractor}_2, \text{Distractor}_3 \}$), randomized using Fisher-Yates shuffling, and returned with the ground-truth key.

---

### 5.4 Semantic Topic Discovery & Literature Linkage (`backend/research_service.py`)

#### 5.4.1 KeyBERT with Maximal Marginal Relevance (MMR)
Rather than simple frequency-based n-grams, KeyBERT uses BERT embeddings to identify phrases that are most representative of the entire document:
1. Candidate n-grams (ranges 2-3 words) are extracted.
2. Document and candidate phrases are embedded into the shared vector space.
3. **Maximal Marginal Relevance (MMR)** balances two competing objectives:
   - **Relevance**: Maximizing similarity between the candidate phrase and the document.
   - **Diversity**: Penalizing candidate phrases that are too similar to already selected keywords.

$$\text{MMR} = \arg\max_{d_i \in R \setminus S} \left[ \lambda \cdot \text{Sim}(d_i, D) - (1 - \lambda) \max_{d_j \in S} \text{Sim}(d_i, d_j) \right]$$

ScholarSphere configures $\lambda = 0.3$ (diversity factor 0.7), ensuring that extracted topics span distinct conceptual dimensions of the paper (e.g., extracting both *"adversarial training"* and *"computational complexity"* rather than two variations of the same phrase).

#### 5.4.2 Semantic Scholar Academic Graph Integration
The extracted key topics are formatted into targeted queries against the **Semantic Scholar Academic Graph API**:
- Endpoint: `https://api.semanticscholar.org/graph/v1/paper/search`
- Query parameters: `fields=title,authors,year,url`, `limit=3`.
- Returns peer-reviewed publications, author attributions, publication years, and direct DOI/paper links directly related to the user's uploaded work.

---

## 6. End-to-End Request Lifecycles & Flowcharts

### 6.1 Summarization Request Lifecycle

```
[Browser / User]
       |
       | 1. Selects PDF/DOCX (e.g. 2.4 MB)
       v
[src/App.jsx (validateFiles)]
       |
       | 2. Validates: Extension in [pdf, docx, txt], Size < 4 MB
       | 3. POST /api/summarize (multipart/form-data)
       v
[Vercel Edge Gateway]
       |
       | 4. Evaluates vercel.json rewrite: /api/summarize -> api/index.py
       v
[FastAPI Serverless Function (api/index.py)]
       |
       | 5. Reads file bytes, validates parameters
       v
[backend/document.py (extract_text)]
       |
       | 6. Detects .pdf -> PyPDF2 PdfReader parses binary stream
       | 7. Extracts text across all pages, normalizes whitespace
       v
[backend/summary_service.py (summarize_documents)]
       |
       | 8. chunk_text() divides text into <= 850 token windows
       | 9. get_summarizer() loads cached pipeline (distilbart-cnn-6-6)
       | 10. Iterates over chunks -> generates abstractive summaries
       | 11. Merges chunks into cohesive summary string
       v
[FastAPI JSON Response]
       |
       | 12. HTTP 200 OK: { results: [...], combined_summary: "..." }
       v
[src/App.jsx]
       |
       | 13. Renders summary card, character metrics, and JSON download button
```

---

## 7. Migration Retrospective: From Streamlit to React + FastAPI

The ScholarSphere codebase originally began as a Python Streamlit application (`app.py`, `app_main.py`). While Streamlit enables rapid prototyping for simple ML scripts, it presented severe architectural bottlenecks as the project matured:

| Dimension | Legacy Streamlit Implementation | Modern React + FastAPI Architecture |
| :--- | :--- | :--- |
| **Execution Model** | Monolithic: Every click, dropdown change, or slider adjustment re-executes the entire Python script from top to bottom. | Decoupled: Frontend runs entirely in the client's browser; backend computation executes only on targeted REST calls. |
| **User Interface** | Rigid, constrained widget layout; difficult to implement custom CSS, responsive grids, or fluid dark mode themes. | Full DOM control with modern CSS, glassmorphism, responsive navigation tabs, and micro-animations. |
| **State Management** | Flaky `st.session_state` that clears unexpectedly on reconnects or tab reloads. | Explicit React state hooks (`useState`, `useEffect`) providing predictable, isolated component lifecycles. |
| **Concurrency & Latency** | Single-threaded script blocking; concurrent requests compete for the same Python process memory. | Asynchronous ASGI server (FastAPI + Uvicorn) capable of handling concurrent non-blocking requests. |
| **Deployment Efficiency** | Requires persistent, always-on VM server (e.g. EC2, Streamlit Cloud) consuming continuous memory even with zero active users. | Serverless deployment on Vercel: zero idle cost, instant scale-to-zero, separate edge CDN caching for static assets. |

---

## 8. Deployment Blueprint & Vercel Optimization

### 8.1 The Serverless Challenge with Machine Learning
Deploying Python machine learning applications to serverless environments (AWS Lambda, Vercel Functions, Google Cloud Run) introduces strict resource constraints:
1. **Uncompressed Bundle Size Limits**: Standard serverless function bundles are capped at **250 MB** (Node.js) or **500 MB** (Python).
2. **PyPI CUDA Bloat**: The standard `torch` package on PyPI includes pre-compiled NVIDIA CUDA runtimes (`libcudnn`, `libcublas`, `libnccl`, etc.) totaling **over 4.5 GB** on disk.
3. **Python Runtime Version Conflicts**: Cloud environments evolve defaults rapidly. Vercel's latest build environment defaults to CPython 3.14, whereas older ML wheels (such as `tokenizers 0.15.2` and PyTorch CPU) require CPython 3.12 ABI tags (`cp312`).

### 8.2 The Multi-Stage Resolution

#### 8.2.1 Enforcing Python 3.12 Everywhere
To prevent the build runner from defaulting to CPython 3.14:
- In `pyproject.toml`: Configured `requires-python = ">=3.12, <3.13"`.
- In `api/.python-version` and `.python-version`: Pinned `3.12`.
- In `vercel.json`: Added `build.env` with `UV_PYTHON = "3.12"` and `PYTHON_VERSION = "3.12"`.
- In Vercel Project Environment: Configured `UV_PYTHON="3.12"`.
- **Eliminated `requirements.txt`**: Removing `requirements.txt` forced Vercel to use `uv sync` against `uv.lock` rather than invoking `uv pip install -r requirements.txt` against the system interpreter.

#### 8.2.2 Routing PyTorch Exclusively to CPU Wheels
In `pyproject.toml`, PyTorch is routed explicitly to the official PyTorch CPU wheel repository:

```toml
[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cpu" }
```

This ensures `uv` queries PyPI exclusively for general packages (`fastapi`, `transformers`, `scikit-learn`), but downloads `torch` exclusively from `download.pytorch.org/whl/cpu`. All 4+ GB of NVIDIA CUDA binaries are eliminated, reducing the PyTorch footprint to ~400 MB.

#### 8.2.3 Enabling Vercel Large Functions & Bundle Trimming
Even with CPU wheels, PyTorch (~440 MB) + SciPy (~110 MB) + Transformers (~70 MB) + Scikit-Learn (~40 MB) total ~900 MB uncompressed, exceeding Vercel's standard 500 MB ceiling.
- **Solution**: Enabled **Vercel Large Functions** (Fluid Compute beta supporting up to **5 GB** bundles) via `VERCEL_SUPPORT_LARGE_FUNCTIONS = "1"` in both project environment variables and `vercel.json`.
- **Lambda Trimming**: Configured `excludeFiles` in `vercel.json` to exclude `node_modules/**`, `dist/**`, `src/**`, `public/**`, and `package-lock.json` from the Python lambda package, ensuring the serverless bundle contains only backend code and Python dependencies.

---

## 9. Security, Validation & Reliability

1. **Request Payload Guardrails**:
   - Vercel functions enforce a hard 4.5 MB request body ceiling.
   - ScholarSphere implements client-side validation (`validateFiles` in `App.jsx`) and server-side validation (`MAX_FILE_SIZE = 4 * 1024 * 1024` in `api/index.py`), immediately rejecting files $> 4\text{ MB}$ with HTTP 413 to prevent memory exhaustion.
2. **File Type Whitelisting**:
   - Whitelist restricted to `.pdf`, `.docx`, and `.txt`.
   - File extensions are validated both client-side and server-side using `Path(filename).suffix.lower()`.
3. **Resilient JSON Decoding**:
   - The frontend API wrapper (`apiRequest` in `App.jsx`) guards against non-JSON server errors (such as Vercel timeout HTML pages or gateway errors), inspecting `Content-Type` headers before parsing to prevent `Unexpected token < in JSON` runtime crashes.
4. **Model Caching with LRU**:
   - Backend pipelines are decorated with `@lru_cache(maxsize=1)` (e.g. `get_summarizer()`, `get_similarity_model()`, `get_quiz_models()`, `get_keyword_model()`).
   - On warm Vercel serverless lambda instances, models remain loaded in RAM across consecutive requests, eliminating repeated cold-start loading penalties.

---

## 10. Local Development & Setup Guide

### Prerequisites
- **Node.js**: v18.0.0 or higher
- **Python**: 3.12.x
- **uv**: (Recommended) Fast Python package manager (`pip install uv`)

### Step-by-Step Installation

```bash
# 1. Clone repository
git clone https://github.com/YashUpd/ScholarSphere.git
cd ScholarSphere-main

# 2. Install Frontend Dependencies
npm install

# 3. Create and Activate Python Virtual Environment
uv venv .venv --python 3.12
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Synchronize Python Dependencies from uv.lock
uv sync

# 5. Start Backend Server (Terminal 1)
uvicorn api.index:app --host 127.0.0.1 --port 8000 --reload

# 6. Start Frontend Development Server (Terminal 2)
npm run dev
```

Visit `http://localhost:5173` to access the application locally.

---

## 11. Maintenance, Future Roadmap & Extensibility

1. **ONNX Runtime Quantization**:
   - Quantizing PyTorch weights to 8-bit ONNX models (`int8`) will reduce the total lambda footprint from ~900 MB down to < 250 MB, accelerating cold-start initialization by up to 300%.
2. **Vector Database Integration (RAG Pipeline)**:
   - For long books or dissertations (> 100 pages), integrating an embedded vector store (ChromaDB or FAISS) will enable retrieval-augmented question answering directly over multi-chapter documents.
3. **LaTeX / BibTeX Parser**:
   - Adding native `.tex` and `.bib` ingestion to `backend/document.py` will allow academic authors to upload paper preprints directly with structured mathematical formula preservation.
4. **Streaming Responses via Server-Sent Events (SSE)**:
   - Migrating summary generation to streaming token chunks will provide instant user feedback as tokens are generated rather than waiting for full completion.
