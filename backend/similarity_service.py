from functools import lru_cache
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from backend.document import extract_text
from backend.summary_service import generate_summary


@lru_cache(maxsize=1)
def get_similarity_model():

    return SentenceTransformer(
        "all-MiniLM-L6-v2"
    )


def analyze_similarity(
    documents: List[Tuple[str, bytes]]
):

    if len(documents) < 2:

        raise ValueError(
            "Please upload at least two documents."
        )

    model = get_similarity_model()

    embeddings = []
    summaries = []
    filenames = []

    for filename, file_bytes in documents:

        text = extract_text(
            filename,
            file_bytes
        )

        summary = generate_summary(
            text,
            max_length=200,
            min_length=70
        )

        embedding = model.encode(
            summary,
            convert_to_numpy=True
        )

        embeddings.append(
            embedding
        )

        summaries.append(
            summary
        )

        filenames.append(
            filename
        )

    embedding_matrix = np.array(
        embeddings
    )

    similarity_matrix = cosine_similarity(
        embedding_matrix
    )

    return {
        "filenames": filenames,
        "summaries": summaries,
        "matrix": similarity_matrix.tolist()
    }