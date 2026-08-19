# ScholarSphere

ScholarSphere is a Streamlit-based academic assistant for summarization, document similarity analysis, quiz generation, and research topic exploration.

## Features

- **Document Summarization**: Generate concise summaries from PDFs, DOCX, and TXT files
- **Similarity Analysis**: Compare documents and visualize relationships
- **Quiz Generator**: Create multiple-choice questions from documents with options and answer keys
- **Research Explorer**: Extract key topics and find related papers

## Tech Stack

- Python (3.11.9 recommended)
- Streamlit
- Hugging Face Transformers (BART/T5)
- SentenceTransformers + scikit-learn
- KeyBERT + NLTK WordNet
- Semantic Scholar API for research paper recommendations

## Project Structure

- `app.py`: main entry point (loads `app_main.py`)
- `app12.py`: latest full implementation
- `testingFiles/`: sample input documents
- `cache_embeddings/`: local cache generated at runtime

## Quick Start

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the app

```bash
streamlit run app.py
```

## Notes

- First run may take time to download NLP models.
- `cache_embeddings/` is generated automatically and should not be committed.
- Research suggestions use Semantic Scholar public API.