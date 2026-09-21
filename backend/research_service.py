from functools import lru_cache

import requests
from keybert import KeyBERT


@lru_cache(maxsize=1)
def get_keyword_model():

    return KeyBERT(
        model="all-MiniLM-L6-v2"
    )


def extract_topics(text: str):

    model = get_keyword_model()

    text = text[:12000]

    keywords = model.extract_keywords(
        text,
        keyphrase_ngram_range=(2, 3),
        use_mmr=True,
        diversity=0.7,
        stop_words="english",
        top_n=8
    )

    return [
        phrase
        for phrase, score in keywords
    ]


def search_related_papers(topics):

    papers = []

    for topic in topics:

        params = {
            "query": topic,
            "limit": 3,
            "fields": "title,authors,year,url"
        }

        try:

            response = requests.get(
                "https://api.semanticscholar.org/"
                "graph/v1/paper/search",
                params=params,
                timeout=10
            )

            if not response.ok:
                continue

            data = response.json()

            for paper in data.get(
                "data",
                []
            ):

                authors = ", ".join(
                    author.get(
                        "name",
                        ""
                    )
                    for author in paper.get(
                        "authors",
                        []
                    )[:3]
                )

                papers.append({
                    "topic": topic,
                    "title": paper.get(
                        "title",
                        "No title"
                    ),
                    "year": paper.get(
                        "year"
                    ),
                    "url": paper.get(
                        "url",
                        ""
                    ),
                    "authors": authors
                })

        except requests.RequestException:

            continue

    return papers