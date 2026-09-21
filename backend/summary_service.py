import os
from functools import lru_cache
from typing import List, Tuple

from transformers import pipeline


SUMMARY_MODEL = os.getenv(
    "SUMMARY_MODEL",
    "sshleifer/distilbart-cnn-6-6"
)


@lru_cache(maxsize=1)
def get_summarizer():
    """
    Load the summarization model once per warm Vercel instance.
    """

    summarizer = pipeline(
        "summarization",
        model=SUMMARY_MODEL,
        device=-1
    )

    tokenizer = summarizer.tokenizer

    return summarizer, tokenizer


def chunk_text(
    text: str,
    tokenizer,
    max_tokens: int = 850
) -> List[str]:

    sentences = [
        sentence.strip()
        for sentence in text.split(". ")
        if sentence.strip()
    ]

    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:

        sentence_tokens = len(
            tokenizer.encode(
                sentence,
                add_special_tokens=True
            )
        )

        if current_tokens + sentence_tokens <= max_tokens:

            current_chunk.append(sentence)
            current_tokens += sentence_tokens

        else:

            if current_chunk:
                chunks.append(
                    ". ".join(current_chunk).strip() + "."
                )

            current_chunk = [sentence]
            current_tokens = sentence_tokens

    if current_chunk:

        chunks.append(
            ". ".join(current_chunk).strip() + "."
        )

    return chunks


def generate_summary(
    text: str,
    max_length: int = 150,
    min_length: int = 50
) -> str:

    summarizer, tokenizer = get_summarizer()

    text = " ".join(text.split())

    if not text:
        return ""

    if min_length >= max_length:
        min_length = max(10, max_length // 2)

    chunks = chunk_text(
        text,
        tokenizer,
        max_tokens=850
    )

    summaries = []

    for chunk in chunks:

        token_count = len(
            tokenizer.encode(
                chunk,
                add_special_tokens=True
            )
        )

        if token_count < 30:
            summaries.append(chunk)
            continue

        chunk_max_length = min(
            max_length,
            max(
                min_length + 10,
                int(token_count * 0.35)
            )
        )

        chunk_min_length = min(
            min_length,
            max(10, chunk_max_length - 10)
        )

        result = summarizer(
            chunk,
            max_length=chunk_max_length,
            min_length=chunk_min_length,
            do_sample=False,
            truncation=True
        )

        if result:

            summaries.append(
                result[0]["summary_text"].strip()
            )

    return " ".join(summaries).strip()


def summarize_documents(
    documents: List[Tuple[str, bytes]],
    max_length: int = 150,
    min_length: int = 50
):

    results = []
    full_texts = []

    for filename, file_bytes in documents:

        text = __import__(
            "backend.document",
            fromlist=["extract_text"]
        ).extract_text(
            filename,
            file_bytes
        )

        summary = generate_summary(
            text,
            max_length=max_length,
            min_length=min_length
        )

        results.append({
            "filename": filename,
            "summary": summary
        })

        full_texts.append(text)

    combined_text = "\n\n".join(full_texts)

    combined_summary = generate_summary(
        combined_text,
        max_length=max_length,
        min_length=min_length
    )

    return {
        "results": results,
        "combined_summary": combined_summary
    }