# 04. AI/NLP Models & Algorithms

---

## 1. Machine Learning & Deep Learning Model Catalog

ScholarSphere leverages four specialized pre-trained transformer models, each optimized for a distinct natural language task:

```
+------------------------------------------------------------------------------------+
|                                AI MODEL PORTFOLIO                                  |
+------------------------------------+-----------------------+-----------------------+
| Model Identifier                   | Primary Function      | Architecture          |
+------------------------------------+-----------------------+-----------------------+
| facebook/bart-large-cnn            | Abstractive Summary   | Seq2Seq Transformer   |
| sentence-transformers/all-MiniLM   | Vector Embeddings     | Siamese BERT (6-layer)|
| mrm8488/t5-base-question-gen       | Question Generation   | Text-to-Text Trans.   |
| distilbert-base-cased-squad        | Extractive QA         | DistilBERT Encoder    |
+------------------------------------+-----------------------+-----------------------+
```

---

## 2. Deep Dive into Model Architectures

### 2.1 Abstractive Summarization: `facebook/bart-large-cnn`

* **Architecture:** Sequence-to-Sequence (Seq2Seq) Bidirectional and Auto-Regressive Transformer.
* **Parameter Count:** ~406 Million Parameters.
* **Pre-training Strategy:** Corrupted text reconstruction (denoising autoencoder using token masking, token deletion, document rotation, and text infilling).
* **Fine-Tuning Domain:** Fine-tuned on the CNN/DailyMail dataset for abstractive text summarization.
* **Token Budget & Chunking Strategy:**
  - Standard max token capacity is $1024$ tokens.
  - To prevent truncation artifacts and out-of-memory overhead, ScholarSphere uses a safe threshold of **$900$ tokens per chunk**.
  - Paragraphs longer than 900 tokens are split at sentence boundaries (`. `), dynamically summarized, and re-stitched.
* **Inference Settings:**
  - `do_sample=False` (Greedy / deterministic beam search for high factual consistency).
  - `truncation=True` (Enforces hard token bounds).
  - Dynamic `max_length` and `min_length` configured via UI sliders.

---

### 2.2 Semantic Vector Embeddings: `sentence-transformers/all-MiniLM-L6-v2`

* **Architecture:** 6-layer distilled MiniLM with a hidden dimension of $384$.
* **Parameter Count:** ~22.7 Million Parameters (ultra-fast, lightweight).
* **Embedding Output:** Produces a dense vector $\mathbf{v} \in \mathbb{R}^{384}$ for any input sentence or document summary.
* **Pooling Strategy:** Mean Pooling over token contextual states with attention mask normalization.
* **Training Objective:** Contrastive learning over 1 billion sentence pairs using cosine similarity loss.
* **Role in ScholarSphere:**
  1. Computes document-level embeddings for pairwise document similarity analysis.
  2. Encodes candidate distractor sentences for quiz distractor filtering.
  3. Powers KeyBERT keyphrase and document semantic alignment.

---

### 2.3 Question Generation: `mrm8488/t5-base-finetuned-question-generation-ap`

* **Architecture:** T5 (Text-to-Text Transfer Transformer) Base architecture.
* **Parameter Count:** ~220 Million Parameters.
* **Task Formulation:** Takes an instructional prompt prefix:
  $$\text{Input: } \texttt{"generate questions: "} + \text{Context Text}$$
* **Generation Hyperparameters in Code:**
  ```python
  outputs = quiz_model.generate(
      **inputs,
      max_length=128,
      num_return_sequences=num_questions,
      do_sample=True,
      temperature=0.7
  )
  ```
  - `temperature=0.7`: Injects controlled creativity to yield diverse linguistic questions.
  - `num_return_sequences`: Directly generates multiple unique question candidates in a single forward pass.

---

### 2.4 Extractive Question Answering: `distilbert-base-cased-distilled-squad`

* **Architecture:** 6-layer DistilBERT encoder fine-tuned on the SQuAD (Stanford Question Answering Dataset).
* **Mechanism:** Given a context document $C$ and a query question $Q$, the model computes start-token and end-token probability logits:
  $$P_{\text{start}}(i) = \frac{\exp(S \cdot h_i)}{\sum_j \exp(S \cdot h_j)}, \quad P_{\text{end}}(j) = \frac{\exp(E \cdot h_j)}{\sum_k \exp(E \cdot h_k)}$$
* **Role in ScholarSphere:** Once T5 generates a candidate question, the QA pipeline evaluates the document text to extract the exact substring span that factually answers that question.

---

## 3. Mathematical Formulations & Algorithmic Workflows

### 3.1 Cosine Similarity Formulation

To determine the semantic proximity between document summaries, ScholarSphere constructs an $N \times N$ pairwise similarity matrix using Scikit-Learn's `cosine_similarity`.

Given two dense embedding vectors $\mathbf{u}, \mathbf{v} \in \mathbb{R}^{384}$:

$$\text{Similarity}(\mathbf{u}, \mathbf{v}) = \cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \frac{\sum_{i=1}^{384} u_i v_i}{\sqrt{\sum_{i=1}^{384} u_i^2} \sqrt{\sum_{i=1}^{384} v_i^2}}$$

#### Geometric Interpretation:
* $\cos(\theta) = 1.0 \implies \theta = 0^\circ$ (Vectors are parallel; texts are semantically identical).
* $\cos(\theta) = 0.0 \implies \theta = 90^\circ$ (Vectors are orthogonal; zero topical overlap).
* $\cos(\theta) = -1.0 \implies \theta = 180^\circ$ (Diametrically opposed concepts).

```
Document 1 (AI Healthcare)  ───► [ 0.21, -0.45, 0.89, ... ] (384-d)
                                            │
                                            ▼  Cosine Similarity = 0.82
                                            ▲  (High Semantic Overlap)
                                            │
Document 2 (Medical Vision)  ───► [ 0.19, -0.41, 0.91, ... ] (384-d)
```

---

### 3.2 3-Tier Distractor Generation Algorithm

A challenging multiple-choice question requires plausible, grammatically consistent **distractors** (false answers). ScholarSphere implements an intelligent 3-stage distractor pipeline:

```mermaid
flowchart TD
    Ans[Extracted Correct Answer 'ans'] --> S1[Stage 1: Lexical WordNet Exploration]
    S1 --> Synsets[Query wordnet.synsets(ans)]
    Synsets --> LemmaFilter[Extract lemmas where lemma != ans]
    LemmaFilter --> SynList[Store up to 2 Synonyms]

    DocContext[Document Context] --> S2[Stage 2: Context Sentence Vector Filtering]
    DocContext --> SplitSent[Split document into sentences s > 20 chars]
    SplitSent --> FilterAns[Remove sentences containing ans]
    FilterAns --> EmbedBoth[Compute SBERT Embeddings of ans and candidate sentences]
    EmbedBoth --> SimCalc[Calculate Cosine Similarity between ans and sentences]
    SimCalc --> Bandpass[Select sentences with 0.3 < Similarity < 0.6]
    Bandpass --> CtxList[Store In-Context Distractors]

    SynList & CtxList --> S3[Stage 3: Assembly & Fallback]
    S3 --> CountCheck{Distractors Count == 3?}
    CountCheck -- No --> RandomFill[Sample random context sentences]
    CountCheck -- Yes --> FinalSet[Assemble 1 True Answer + 3 Distractors]
    RandomFill --> FinalSet
    FinalSet --> Shuffle[random.shuffle options]
```

#### Why the $0.3 < \text{sim} < 0.6$ Threshold?
* $\text{sim} > 0.6$: The sentence is **too similar** to the answer and risks being another valid answer (causing ambiguity).
* $\text{sim} < 0.3$: The sentence is **completely unrelated** and makes the distractor obviously fake.
* $0.3 < \text{sim} < 0.6$: The **optimal zone**—contextually relevant to the subject matter, but factually distinct.

---

### 3.3 Keyphrase Extraction via KeyBERT & Maximal Marginal Relevance (MMR)

In the Research Explorer tab, topics are extracted using KeyBERT with **Maximal Marginal Relevance (MMR)**:

$$\text{MMR}(D, Q) = \operatorname*{argmax}_{d_i \in R \setminus S} \left[ \lambda \cdot \text{Sim}_1(d_i, Q) - (1 - \lambda) \cdot \max_{d_j \in S} \text{Sim}_2(d_i, d_j) \right]$$

Where:
* $Q$: Overall document embedding.
* $d_i$: Candidate keyphrase n-gram embedding (2–3 words).
* $S$: Set of keyphrases already selected.
* $R \setminus S$: Remaining unselected candidate phrases.
* $\lambda = 0.3$ ($\text{diversity} = 1 - \lambda = 0.7$): Heavily penalizes redundant keyphrases, ensuring diverse topic extraction across distinct sections of the document.
