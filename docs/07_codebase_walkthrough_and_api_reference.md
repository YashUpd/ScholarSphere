# 07. Codebase Walkthrough & API Reference

---

## 1. Structure of Source Files

The core logic of ScholarSphere is encapsulated in two Python source files:
* **`app.py`:** Deployment wrapper and path resolver.
* **`app_main.py`:** Primary operational codebase containing data pipelines, deep learning model hooks, and Streamlit user interface components.

---

## 2. Walkthrough: `app.py`

```python
# Hugging Face Spaces entry point
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname("app_main.py"))

# Import and run main app
from app_main import main

if __name__ == "__main__":
    main()
```

### Detailed Explanation:
1. **`sys.path.append(...)`:** Ensures that Python's module resolver includes the root workspace directory, allowing imports to resolve seamlessly on local operating systems and cloud runtime environments alike.
2. **`from app_main import main`:** Imports the primary application entrypoint.
3. **`if __name__ == "__main__": main()`:** Standard execution guard ensuring that launching `streamlit run app.py` starts the complete interface.

---

## 3. Detailed Walkthrough: `app_main.py`

### 3.1 Caching & Persistence Subsystem

#### `get_file_hash(file_bytes: bytes) -> str`
* **Purpose:** Computes the MD5 checksum of raw uploaded file bytes to create a deterministic, content-addressable cache key.
* **Returns:** 32-character hexadecimal string.

#### `load_cached_data(file_hash: str, data_type: str) -> Optional[object]`
* **Purpose:** Locates and deserializes binary pickle files stored under `cache_embeddings/<file_hash>_<data_type>.pkl`.
* **Error Handling:** Returns `None` and issues a non-blocking warning (`st.warning`) if file reading or unpickling fails.

#### `save_cached_data(file_hash: str, data_type: str, data: object) -> None`
* **Purpose:** Serializes Python data structures (e.g., summary text strings, NumPy embedding arrays) to disk.

#### `clear_cache() -> None`
* **Purpose:** Iterates through the `cache_embeddings/` directory and removes all cached `.pkl` files via `os.unlink()`.

---

### 3.2 Text Extraction & Chunking Utilities

#### `extract_text(file) -> Tuple[Optional[str], Optional[bytes]]`
* **Parameters:** `file` (Streamlit `UploadedFile` object).
* **Execution Flow:**
  1. Reads raw bytes via `file.getvalue()` or `file.read()`, then resets the stream pointer via `file.seek(0)`.
  2. If file is `.pdf`: Uses `PyPDF2.PdfReader` to extract and join text across all pages.
  3. If file is `.docx`: Uses `docx.Document` to extract and join text from all paragraphs.
  4. If file is `.txt`: Decodes byte stream using UTF-8.
* **Returns:** `(text_string, raw_bytes)` or `(None, None)` if an error occurs.

#### `chunk_text(text: str, tokenizer, max_tokens: int = 1024) -> List[str]`
* **Purpose:** Partitions large text passages into token-budgeted chunks to avoid exceeding transformer context windows.
* **Mechanism:**
  - Tokenizes sentence-by-sentence (`. ` split).
  - Accumulates sentences until the encoded token length reaches `max_tokens` ($900$ default in practice).
  - Emits the accumulated chunk and starts a new buffer.
* **Returns:** `List[str]` of bounded text chunks.

---

### 3.3 Deep Learning Model Loading

#### `@st.cache_resource(show_spinner=False) def load_models(use_gpu: bool)`
* **Purpose:** Loads all transformer pipelines and model weights into memory once at application launch.
* **Device Resolution:** Checks `torch.cuda.is_available()`. Sets `device_idx = 0` if `use_gpu=True` and CUDA is available, otherwise `-1` for CPU.
* **Models Instantiated:**
  1. `summarizer`: Hugging Face pipeline for `facebook/bart-large-cnn`.
  2. `tokenizer`: `AutoTokenizer.from_pretrained("facebook/bart-large-cnn")`.
  3. `similarity_model`: `SentenceTransformer('all-MiniLM-L6-v2')`.
  4. `quiz_model`: `T5ForConditionalGeneration.from_pretrained("mrm8488/t5-base-finetuned-question-generation-ap")`.
  5. `quiz_tokenizer`: `T5Tokenizer.from_pretrained(...)`.
  6. `qa_pipeline`: Hugging Face pipeline for `"question-answering"`.
* **Returns:** `(summarizer, tokenizer, similarity_model, (quiz_model, quiz_tokenizer, qa_pipeline))`.

---

### 3.4 Summary Generation Logic

#### `generate_summary(text: str, summarizer, tokenizer, max_length: int = 150, min_length: int = 40) -> str`
* **Execution Steps:**
  1. Cleans and collapses extraneous whitespace and double periods.
  2. If `len(tokenizer.encode(text)) < min_length`, returns the raw text directly.
  3. Divides text into paragraph chunks $\le 900$ tokens.
  4. Runs the BART summarizer on each chunk with `do_sample=False` and `truncation=True`.
  5. Dynamically scales `chunk_max = min(max_length, max(int(chunk_length * 0.7), min_length))`.
  6. Joins all sub-summaries into a coherent narrative.

#### `generate_summary_with_cache(...)` & `generate_embedding_with_cache(...)`
* **Purpose:** Checks disk cache using `load_cached_data()`. If present, returns immediately and displays a status toast (`💾 Using cached data...`). Otherwise, computes fresh data and persists it to disk.

---

### 3.5 Similarity & Heatmap Engine

#### `create_similarity_visualization(similarity_matrix: np.ndarray, filenames: List[str]) -> plt.Figure`
* **Parameters:** $N \times N$ similarity matrix and a list of filenames.
* **Execution Flow:**
  - Truncates filenames to 15 characters with an ellipsis (`...`) for clean axis labels.
  - Constructs a `pandas.DataFrame`.
  - Invokes `seaborn.heatmap()` with `cmap="YlOrRd"`, `annot=True`, `vmin=0`, `vmax=1`, and `fmt=".2f"`.
  - Configures 45-degree x-axis label rotation and tight layout.
* **Returns:** Matplotlib `Figure` instance.

#### `create_similarity_zip(similarity_matrix, filenames, summaries, fig) -> io.BytesIO`
* **Purpose:** Builds an in-memory ZIP archive containing:
  1. `similarity_matrix.csv` (tabular CSV)
  2. `similarity_heatmap.png` (300 DPI figure)
  3. `summaries/<filename>_summary.txt` (text files for each document)
  4. `README.txt` (summary report descriptor)

---

### 3.6 Automated Quiz Engine

#### `generate_quiz(text: str, quiz_components, similarity_model, num_questions=5) -> List[Dict]`
* **Parameters:** Source text, quiz models tuple, sentence similarity model, and target question count.
* **Algorithm Steps:**
  1. Prepares prompt `generate questions: {text[:5000]}`.
  2. Runs `quiz_model.generate()` with `temperature=0.7` to yield questions.
  3. Evaluates each question with `qa_pipeline(question=q, context=text)` to extract the factual `ans`.
  4. Stage 1 Distractors: Queries `wordnet.synsets(ans)` for up to 2 synonyms.
  5. Stage 2 Distractors: Splits context into sentences, encodes with `similarity_model`, and filters sentences with cosine similarity $0.3 < \text{sim} < 0.6$.
  6. Stage 3 Distractors: Fills any remaining slots with random context sentences.
  7. Combines answer and 3 distractors, applies `random.shuffle()`, and appends to the quiz questions list.
* **Returns:**
  ```python
  [
      {
          "question": "What is the primary greenhouse gas mentioned?",
          "options": ["Methane", "Carbon Dioxide", "Argon", "Nitrous Oxide"],
          "answer": "Carbon Dioxide"
      },
      ...
  ]
  ```

---

### 3.7 Research Explorer & Semantic Scholar Integration

#### `research_tab()`
* **Execution Steps:**
  1. Extracts text from the uploaded document.
  2. Instantiates `KeyBERT(model="all-MiniLM-L6-v2")`.
  3. Calls `extract_keywords(keyphrase_ngram_range=(2,3), use_mmr=True, diversity=0.7, top_n=8)`.
  4. For each topic, submits an HTTP GET request to `https://api.semanticscholar.org/graph/v1/paper/search?query={topic}&limit=3&fields=title,authors,year,url`.
  5. Renders formatted bibliographic links:
     `[Paper Title](url) (Year) • Author1, Author2`
