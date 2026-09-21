# 06. Installation, Deployment & Operations

---

## 1. System Requirements

### Hardware Recommendations

| Component | Minimum Specification (CPU Only) | Recommended Specification (GPU Accelerated) |
| :--- | :--- | :--- |
| **Processor (CPU)** | Quad-Core 2.5 GHz x86_64 / ARM64 | 8+ Cores Intel Core i7/i9 or AMD Ryzen 7/9 |
| **RAM** | 8 GB System Memory | 16 GB+ High-Speed DDR4/DDR5 |
| **Dedicated GPU** | None (Runs on CPU with `-1` device) | NVIDIA GPU with 6 GB+ VRAM (CUDA 11.8 / 12.1+) |
| **Storage** | 10 GB Free Disk Space (for model weights & cache) | NVMe SSD with 20 GB+ Free Disk Space |
| **Network** | Broadband internet (required for first-time model downloads) | Stable Broadband connection |

### Operating System & Environment
* **OS:** Windows 10/11, macOS 12+ (Monterey, Ventura, Sonoma), Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+).
* **Python Runtime:** Python `3.11.9` (recommended and declared in `runtime.txt`).

---

## 2. Step-by-Step Local Setup

### Step 1: Clone the Repository & Open Directory
```bash
git clone https://github.com/SampurnGupta/ScholarSphere.git
cd ScholarSphere
```

### Step 2: Create & Activate a Python Virtual Environment

* **Windows PowerShell:**
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```

* **Windows Command Prompt (CMD):**
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate.bat
  ```

* **Linux / macOS (Bash / Zsh):**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

---

### Step 3: Install Package Dependencies

Install the pinned dependencies from `requirements.txt`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Optional: Dedicated PyTorch CUDA Installation (For NVIDIA GPU Users)
If you have an NVIDIA GPU, install the CUDA-enabled build of PyTorch:
```bash
# Example for CUDA 12.1
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

---

### Step 4: Hugging Face Authentication (Optional / Recommended)

To ensure smooth access to public Hugging Face repositories:
```bash
huggingface-cli login
```
*(Enter your Hugging Face User Access Token when prompted).*

---

### Step 5: Run the Streamlit Application

Start the web application locally:
```bash
streamlit run app.py
```

Upon launching, Streamlit will display the local access URLs:
* **Local URL:** `http://localhost:8501`
* **Network URL:** `http://<your-local-ip>:8501`

---

## 3. Hugging Face Spaces Cloud Deployment

ScholarSphere is pre-configured for one-click deployment on **Hugging Face Spaces** using the Streamlit SDK.

```
Hugging Face Space
├── app.py                   <-- Root Entrypoint recognized by Spaces
├── app_main.py              <-- Complete Application Logic
├── requirements.txt         <-- Automatically read and installed by Spaces build engine
├── runtime.txt              <-- Enforces Python 3.11.9 execution
├── .streamlit/
│   └── config.toml          <-- Server settings (fileWatcherType = "none")
```

### Key Deployment Files Explained:

1. **`app.py`:** A clean wrapper that adds the current working directory to `sys.path` and executes `main()` from `app_main.py`.
2. **`runtime.txt`:** Specifies `python-3.11.9`, ensuring consistent dependencies and preventing compiler mismatches.
3. **`.streamlit/config.toml`:**
   ```toml
   [server]
   fileWatcherType = "none"
   ```
   *Disables filesystem polling to avoid excessive CPU usage in headless container environments.*

---

## 4. Cache Operations & Storage Maintenance

### Storage Architecture of `cache_embeddings/`
* Whenever a document is analyzed, two files are created:
  - `cache_embeddings/<file_md5_hash>_summary.pkl`
  - `cache_embeddings/<file_md5_hash>_embedding.pkl`
* **Disk Usage:** Each summary file is approximately $1 - 5\text{ KB}$. Each 384-dimensional embedding file is approximately $3\text{ KB}$.

### Clearing Cache:
1. **Via UI:** Open the left sidebar and click **"🔄 Clear All Cached Data"**.
2. **Via Terminal:**
   ```bash
   # Linux/macOS
   rm -rf cache_embeddings/*.pkl

   # Windows PowerShell
   Remove-Item -Path "cache_embeddings\*.pkl" -Force
   ```

---

## 5. Operational Troubleshooting & Diagnostics

### Issue 1: `SentencePiece not installed → quiz disabled`
* **Root Cause:** The T5 Tokenizer requires `sentencepiece` for subword segmentation.
* **Resolution:** Run `pip install sentencepiece` and restart Streamlit.

---

### Issue 2: `CUDA Out of Memory (OOM)`
* **Root Cause:** Processing very large documents simultaneously with GPU mode enabled exceeds available VRAM.
* **Resolution:**
  - Uncheck **"Use GPU if available"** in the sidebar to fallback to CPU mode.
  - Or process documents in smaller batches (2–3 files at a time).

---

### Issue 3: `No model was supplied, defaulted to distilbert...` Terminal Warning
* **Root Cause:** Hugging Face's pipeline is called without specifying the `model` argument on line 107.
* **Resolution:** This is a non-blocking informational warning. The pipeline defaults to `distilbert-base-cased-distilled-squad` and functions as intended.

---

### Issue 4: Semantic Scholar Request Failure / Timeout
* **Root Cause:** Public API rate limits ($100$ requests per $5$ minutes) or network latency.
* **Resolution:** ScholarSphere wraps requests in a `try...except requests.RequestException` block with a 10-second timeout, ensuring the app remains responsive even during network outages.
