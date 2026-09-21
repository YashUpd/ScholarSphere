# 02. Architecture & Data Flow

---

## 1. High-Level System Architecture

ScholarSphere is architected around a layered, modular structure comprising four distinct operational planes:
1. **User Presentation & Interaction Layer (Streamlit UI)**
2. **Document Ingestion & Text Extraction Plane**
3. **Deep Learning & NLP Inference Engine**
4. **Caching, Persistence & External Service Layer**

```mermaid
graph TB
    subgraph UI_Layer["1. Presentation Layer (Streamlit)"]
        UI_Sidebar["Sidebar (Settings, Cache Clear, GPU Toggle)"]
        Tab_Summary["Tab 1: Summarization"]
        Tab_Similarity["Tab 2: Similarity Analysis"]
        Tab_Quiz["Tab 3: Quizzer"]
        Tab_Research["Tab 4: Research Explorer"]
    end

    subgraph Ingestion_Layer["2. Ingestion & Preprocessing"]
        File_Uploader["File Uploader (PDF, DOCX, TXT)"]
        Extractor["extract_text() / PyPDF2 / python-docx"]
        Hasher["get_file_hash() / MD5 Checksum"]
        Chunker["chunk_text() / Token Budgeting"]
    end

    subgraph Cache_Layer["3. Caching & Persistence Subsystem"]
        RAM_Cache["In-Memory Model Cache (@st.cache_resource)"]
        Disk_Cache["Disk Pickle Cache (cache_embeddings/*.pkl)"]
    end

    subgraph Inference_Layer["4. AI & NLP Inference Engine"]
        BART_Engine["facebook/bart-large-cnn (Summarizer)"]
        MiniLM_Engine["sentence-transformers/all-MiniLM-L6-v2 (Embedder)"]
        T5_Engine["mrm8488/t5-base-finetuned-question-generation (QG)"]
        QA_Engine["distilbert-base-cased-distilled-squad (Extractive QA)"]
        Distractor_Gen["Lexical (WordNet) + Semantic Vector Filter"]
        KeyBERT_Engine["KeyBERT + MMR Topic Extractor"]
    end

    subgraph External_Services["5. External APIs & Output Bundlers"]
        S2_API["Semantic Scholar Graph API"]
        ZIP_Bundler["ZipFile In-Memory Packager"]
        Plotter["Matplotlib / Seaborn Heatmap Renderer"]
    end

    %% Connections
    UI_Sidebar --> RAM_Cache
    Tab_Summary & Tab_Similarity & Tab_Quiz & Tab_Research --> File_Uploader
    File_Uploader --> Extractor
    Extractor --> Hasher
    Hasher --> Disk_Cache
    Extractor --> Chunker

    Chunker --> BART_Engine
    BART_Engine --> Tab_Summary
    Tab_Summary --> ZIP_Bundler

    BART_Engine --> MiniLM_Engine
    MiniLM_Engine --> Plotter
    Plotter --> Tab_Similarity
    MiniLM_Engine --> ZIP_Bundler

    Chunker --> T5_Engine
    T5_Engine --> QA_Engine
    QA_Engine --> Distractor_Gen
    Distractor_Gen --> Tab_Quiz

    Extractor --> KeyBERT_Engine
    KeyBERT_Engine --> S2_API
    S2_API --> Tab_Research
```

---

## 2. Core Execution Lifecycles & Data Flows

### A. Document Ingestion & Text Preprocessing Flow

When a user selects files through the Streamlit upload widget, the data flow follows these steps:

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Streamlit as Streamlit Frontend
    participant Ingestion as extract_text()
    participant Hash as get_file_hash()
    participant Disk as cache_embeddings/

    User->>Streamlit: Upload (.pdf, .docx, or .txt)
    Streamlit->>Ingestion: Pass UploadedFile object
    Ingestion->>Ingestion: Inspect file extension
    alt Extension is .pdf
        Ingestion->>Ingestion: PyPDF2.PdfReader extracts page strings
    else Extension is .docx
        Ingestion->>Ingestion: docx.Document parses paragraph texts
    else Extension is .txt
        Ingestion->>Ingestion: Raw UTF-8 bytes decoding
    end
    Ingestion->>Hash: Compute MD5 of raw file bytes
    Hash-->>Disk: Check if <hash>_summary.pkl or <hash>_embedding.pkl exists
    Disk-->>Streamlit: Return cached object OR flag for computation
```

---

### B. Summarization & Multi-Document Integration Flow

The summarization pipeline handles token length constraints and produces both granular and synthesized summaries:

```mermaid
flowchart TD
    Start([Raw Extracted Text]) --> Normalize[Text Cleaning: remove extra whitespace, normalize dots]
    Normalize --> TokenCheck{Total Tokens < min_length?}
    
    TokenCheck -- Yes --> ReturnRaw[Return Original Text as Summary]
    TokenCheck -- No --> ParagraphSplit[Split by Paragraphs '\n\n']
    
    ParagraphSplit --> ChunkEval{Paragraph Tokens > 900?}
    ChunkEval -- Yes --> SentenceChunk[Split into Sentence-Level Chunks <= 900 tokens]
    ChunkEval -- No --> Accumulate[Accumulate into Batch Chunk <= 900 tokens]
    
    SentenceChunk & Accumulate --> BARTInference[Run BART-Large-CNN Inference]
    BARTInference --> Stitch[Join Chunk Summaries with Period Normalization]
    Stitch --> SaveCache[Persist to cache_embeddings/hash_summary.pkl]
    SaveCache --> SingleDisplay[Render Individual File Summary]
    
    SingleDisplay --> CombineTrigger{Multiple Files Uploaded?}
    CombineTrigger -- Yes --> JoinAll[Concatenate all full texts with '\n\n']
    JoinAll --> GlobalBART[Run BART Multi-Doc Synthesis]
    GlobalBART --> RenderZip[Package all TXT files + Combined into ZIP]
    CombineTrigger -- No --> End([Complete])
    RenderZip --> End
```

---

### C. Similarity Calculation & Heatmap Generation Flow

The similarity analysis pipeline transforms text summaries into geometric points in high-dimensional vector space:

```mermaid
flowchart LR
    subgraph Step1["1. Embedding Computation"]
        Sum1[Summary 1] --> SBERT[SentenceTransformer all-MiniLM-L6-v2] --> Vec1["Vector 1 (384-d)"]
        SumN[Summary N] --> SBERT --> VecN["Vector N (384-d)"]
    end

    subgraph Step2["2. Metric Computation"]
        Vec1 & VecN --> SklearnCosine["sklearn cosine_similarity(X, Y)"]
        SklearnCosine --> Matrix["NxN Symmetric Similarity Matrix"]
    end

    subgraph Step3["3. Visualization & Output"]
        Matrix --> DF[Pandas DataFrame with YlOrRd Heat Gradient]
        Matrix --> Seaborn[Seaborn ax.heatmap 300 DPI figure]
        Matrix --> Exporter[ZipFile Bundle: CSV + PNG + TXT]
    end
```

---

### D. Automated Quiz & Distractor Assembly Flow

The Quizzer engine coordinates question formulation, answer verification, and a 3-tier distractor pipeline:

```mermaid
flowchart TD
    InputText[Source Text Chunk max 5000 chars] --> T5Gen[T5 Conditional Generator: 'generate questions: ...']
    T5Gen --> RawQuestions[Output Q Strings ending with '?']
    
    RawQuestions --> QAPipe[DistilBERT SQuAD QA Pipeline]
    InputText --> QAPipe
    QAPipe --> GroundTruth[Extract Exact Factual Answer: 'ans']
    
    GroundTruth --> LexicalStage[WordNet Synsets / Lemmas Search]
    LexicalStage --> SynList[Collect up to 2 Synonyms]
    
    InputText --> SentenceSplit[Split Document Sentences]
    SentenceSplit --> SentenceEmbed[Compute Sentence Embeddings via MiniLM]
    GroundTruth --> AnsEmbed[Compute Answer Embedding via MiniLM]
    
    SentenceEmbed & AnsEmbed --> CosineFilter[Filter Sentences with 0.3 < Cosine Similarity < 0.6]
    CosineFilter --> ContextDistractors[Plausible In-Context Distractors]
    
    SynList & ContextDistractors --> Assemble[Combine Synonyms + Context Distractors]
    Assemble --> FallbackCheck{Total Distractors == 3?}
    FallbackCheck -- No --> RandomSample[Sample random context sentence / reverse string]
    FallbackCheck -- Yes --> FinalOptions[Final 4 Options: 1 Answer + 3 Distractors]
    
    FinalOptions --> Shuffle[random.shuffle options]
    Shuffle --> QuestionCard[Render Radio Button Card & JSON/TXT Exporters]
```

---

### E. Research Explorer & Semantic Scholar Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Streamlit as UI Layer
    participant KeyBERT as KeyBERT Topic Engine
    participant S2 as Semantic Scholar Graph API

    User->>Streamlit: Upload document
    Streamlit->>KeyBERT: Extract n-grams (2,3) with MMR & diversity=0.7
    KeyBERT-->>Streamlit: Return top 8 keyphrases
    loop For each topic in topics
        Streamlit->>S2: GET https://api.semanticscholar.org/graph/v1/paper/search?query=topic&limit=3
        alt Status 200 OK
            S2-->>Streamlit: Return JSON with title, authors, year, url
            Streamlit->>Streamlit: Render formatted bibliographic markdown links
        else Network Timeout / Rate Limit
            Streamlit->>Streamlit: Silently ignore and continue next topic
        end
    end
```

---

## 3. Two-Tier Caching Architecture

ScholarSphere employs a multi-level caching hierarchy to guarantee responsiveness and eliminate redundant computation:

```
+-------------------------------------------------------------------------+
| Level 1: In-Memory Model Cache (Streamlit @st.cache_resource)           |
| Stores: BART Summarizer, Tokenizer, MiniLM, T5, QA Pipeline             |
| Scope: Shared across all sessions; loaded once per application start    |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Level 2: Persistent Disk Cache (cache_embeddings/ directory)             |
| Stores: <md5_hash>_summary.pkl & <md5_hash>_embedding.pkl               |
| Key: MD5 Checksum of raw uploaded file bytes                            |
| Format: Python binary pickle serialization                              |
| Invalidation: Explicit manual trigger via sidebar "Clear All Cache"     |
+-------------------------------------------------------------------------+
```

### Disk Cache Eviction Algorithm
When the user clicks **"🔄 Clear All Cached Data"**:
1. `clear_cache()` reads `os.listdir("cache_embeddings")`.
2. Iterates over all files and executes `os.unlink(file_path)`.
3. Displays a confirmation toast (`st.success`).
4. Invokes `st.rerun()` to refresh the application state.

---

## 4. Hardware Allocation & Device Routing

ScholarSphere dynamically adapts to the host runtime environment:

```python
# Hardware Detection Logic in app_main.py
cuda_available = torch.cuda.is_available()
device_idx = 0 if use_gpu and cuda_available else -1
```

* **GPU Mode (`use_gpu=True` AND `cuda_available=True`):**
  - Hugging Face pipelines configure `device=0` (CUDA).
  - T5 PyTorch model calls `quiz_model.to("cuda")`.
  - Dramatically accelerates token generation and transformer matrix multiplications.
* **CPU Mode (`use_gpu=False` OR `cuda_available=False`):**
  - Hugging Face pipelines configure `device=-1` (CPU).
  - T5 PyTorch model calls `quiz_model.to("cpu")`.
  - Prevents CUDA out-of-memory errors on shared cloud instances (e.g., Hugging Face Spaces free tier).
