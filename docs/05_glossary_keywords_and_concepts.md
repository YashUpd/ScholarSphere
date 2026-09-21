# 05. Glossary, Keywords & Concepts

---

## 📖 Alphabetical Encyclopedia of Terms & Concepts

### A

* **Abstractive Summarization:** A natural language generation technique where an AI model reads source text and generates a summary using new words, phrases, and restructured sentences that were not present in the original document (e.g., BART).
* **Attention Mechanism (Self-Attention):** A core mathematical algorithm in Transformer architectures allowing the model to dynamically weigh the importance of different words in a sentence regardless of their positional distance.
* **AutoTokenizer:** A Hugging Face utility that automatically inspects a pre-trained model name or path and instantiates the correct tokenizer class (e.g., BPE, WordPiece, SentencePiece).
* **Autoregressive Generation:** A process where a model generates output token-by-token, using its previously generated tokens as inputs for predicting the next token.

---

### B

* **BART (Bidirectional and Auto-Regressive Transformers):** A sequence-to-sequence model introduced by Facebook AI combining a bidirectional encoder (like BERT) with an autoregressive decoder (like GPT). Fine-tuned in ScholarSphere for abstractive text summarization.
* **Beam Search:** A heuristic search algorithm used during text generation that explores a graph by expanding the most promising nodes in a limited set (the "beam width"), producing more coherent and accurate text than greedy selection.
* **BPE (Byte-Pair Encoding):** A subword tokenization algorithm that iteratively merges the most frequent pairs of characters or bytes, allowing tokenizers to handle out-of-vocabulary words smoothly.

---

### C

* **Cache Invalidation:** The computational process of clearing or evicting stored cache data (e.g., MD5-hashed summaries) when fresh data or explicit manual resets are requested.
* **Chunking (Token-Budget Chunking):** The technique of partitioning lengthy documents into smaller, manageable token blocks (e.g., $\le 900$ tokens) to ensure they fit within transformer context bounds without crashing or truncating critical information.
* **Context Window:** The maximum number of tokens a transformer model can accept and process in a single forward pass ($1024$ for BART-large-CNN, $512$ for MiniLM/T5).
* **Cosine Similarity:** A mathematical metric calculating the cosine of the angle between two non-zero vectors in multi-dimensional space, measuring directional and semantic alignment on a normalized scale from $-1.0$ to $+1.0$.
* **CUDA (Compute Unified Device Architecture):** Nvidia's parallel computing platform allowing PyTorch and Deep Learning models to execute matrix calculations directly on Nvidia GPUs.

---

### D

* **Distractor:** An incorrect answer option in a multiple-choice question designed to be plausible and contextually consistent, challenging the test-taker's genuine understanding.
* **DistilBERT:** A smaller, faster, distilled version of BERT that retains $97\%$ of BERT’s language understanding capabilities while using $40\%$ fewer parameters and running $60\%$ faster.
* **Dot Product (Inner Product):** The sum of the products of the corresponding components of two vectors. In normalized unit vectors, the dot product directly equals the cosine similarity.

---

### E

* **Embeddings (Dense Vector Embeddings):** Numerical vector representations of words, sentences, or documents where semantically related concepts are positioned close to one another in geometric vector space.
* **Encoder-Decoder Architecture:** A dual-network deep learning architecture where the *encoder* transforms input text into contextual hidden state vectors, and the *decoder* generates target text from those representations.
* **Extractive Question Answering:** An NLP task where a model identifies and extracts the exact contiguous character span (start and end indices) within a reference context that factually answers a query.

---

### F

* **Fine-Tuning:** The process of taking a foundational model pre-trained on massive generalized corpora and training it further on a specialized domain or task dataset (e.g., CNN/DailyMail for BART, SQuAD for QA).

---

### G

* **Greedy Search:** A text generation decoding strategy that selects the token with the highest probability at each individual step ($do\_sample = False$).

---

### H

* **Hash / MD5 Checksum:** A cryptographic hash function that converts arbitrary byte streams (e.g., uploaded PDF files) into fixed 32-character hexadecimal strings, used by ScholarSphere as unique cache keys.
* **Heatmap:** A 2D graphical representation of data where individual values contained in a matrix are represented as colors, utilized in ScholarSphere for document-to-document similarity comparisons.
* **Hugging Face Hub:** An open-source platform and repository hosting thousands of pre-trained machine learning models, datasets, and spaces.

---

### K

* **KeyBERT:** A keyphrase extraction algorithm that uses BERT embeddings to find keywords and n-gram phrases that are most similar to the overall document.

---

### L

* **Lemma / Lemmatization:** The algorithmic process of reducing words to their base dictionary form (e.g., "running", "ran", "runs" $\rightarrow$ "run").
* **Logits:** Raw, unnormalized prediction scores output by the final linear layer of a neural network before being transformed into probabilities via Softmax.

---

### M

* **Maximal Marginal Relevance (MMR):** An optimization algorithm that balances topical relevance with diversity to minimize redundancy when selecting keyphrases or search results.
* **MiniLM:** A distilled, high-efficiency transformer architecture developed by Microsoft and adapted by SentenceTransformers for low-latency dense semantic search.

---

### N

* **N-gram:** A contiguous sequence of $n$ items (words or characters) extracted from a given sample of text (e.g., bigrams $n=2$, trigrams $n=3$).
* **NLTK (Natural Language Toolkit):** A leading Python library for symbolic and statistical natural language processing.

---

### P

* **Pickle (`.pkl`):** Python's native binary object serialization format, used in ScholarSphere to store computed embeddings and summaries to disk.
* **Pipeline (Hugging Face):** A high-level abstraction that connects tokenization, model forward pass, and output decoding into a single unified callable object.
* **PyTorch:** An open-source machine learning library primarily developed by Meta AI, providing multidimensional tensors and automatic differentiation.

---

### Q

* **Question Generation (QG):** The automated generation of coherent, grammatically sound questions from textual context using text-to-text generative models.

---

### R

* **REST API:** Representational State Transfer Application Programming Interface; a stateless architectural style used to query external web services like the Semantic Scholar Graph API.

---

### S

* **SentenceTransformer (SBERT):** A Python framework for state-of-the-art sentence, text, and image embeddings that uses Siamese neural networks.
* **SentencePiece:** An unsupervised text tokenizer that treats input as a raw stream and learns subword vocabularies without language-specific pre-tokenization.
* **SQuAD (Stanford Question Answering Dataset):** A benchmark reading comprehension dataset consisting of questions posed on Wikipedia articles, where the answer to every question is a segment of text from the reading passage.
* **Stop Words:** Common words (such as "the", "is", "at", "which") filtered out during keyphrase extraction to focus exclusively on meaningful domain vocabulary.
* **Streamlit:** An open-source Python framework that turns data scripts into shareable, reactive web applications.
* **Synset (Synonym Set):** In Princeton's WordNet lexical database, a grouping of synonymous words that express the same underlying semantic concept.

---

### T

* **T5 (Text-to-Text Transfer Transformer):** An encoder-decoder model introduced by Google that frames all NLP tasks (summarization, translation, QG, classification) as text-to-text problems.
* **Temperature:** A hyperparameter used to scale logits during generation; lower temperature produces deterministic, repetitive text, while higher temperature ($>0.7$) encourages creative vocabulary variation.
* **Token:** The basic unit of text processed by a language model, corresponding to words, subwords, or punctuation characters.
* **Truncation:** The process of discarding tokens that exceed a model's maximum allowed input sequence length.

---

### V

* **Vector Space Model:** An algebraic model for representing textual data as vectors of identifiers, allowing geometric calculations of similarity and relevance.

---

### W

* **WordNet:** A large lexical database of English where nouns, verbs, adjectives, and adverbs are grouped into sets of cognitive synonyms (synsets), each expressing a distinct concept.
