import random
from functools import lru_cache
from typing import Dict, List

from nltk.corpus import wordnet
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer,
    pipeline
)


QUIZ_MODEL_NAME = (
    "mrm8488/"
    "t5-base-finetuned-question-generation-ap"
)


@lru_cache(maxsize=1)
def get_quiz_models():

    tokenizer = T5Tokenizer.from_pretrained(
        QUIZ_MODEL_NAME
    )

    model = T5ForConditionalGeneration.from_pretrained(
        QUIZ_MODEL_NAME
    )

    model.to("cpu")

    qa_pipeline = pipeline(
        "question-answering",
        model="distilbert-base-cased-distilled-squad",
        device=-1
    )

    similarity_model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    return (
        model,
        tokenizer,
        qa_pipeline,
        similarity_model
    )


def get_synonyms(answer: str):

    synonyms = set()

    try:

        for synset in wordnet.synsets(answer):

            for lemma in synset.lemmas():

                word = lemma.name().replace(
                    "_",
                    " "
                )

                if word.lower() != answer.lower():

                    synonyms.add(word)

            if len(synonyms) >= 3:
                break

    except LookupError:
        pass

    return list(synonyms)


def generate_quiz(
    text: str,
    num_questions: int = 3
) -> List[Dict]:

    (
        model,
        tokenizer,
        qa_pipeline,
        similarity_model
    ) = get_quiz_models()

    text = " ".join(text.split())

    if len(text) < 100:
        return []

    question_input = tokenizer(
        f"generate questions: {text[:5000]}",
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    outputs = model.generate(
        **question_input,
        max_length=128,
        num_return_sequences=num_questions,
        do_sample=True,
        temperature=0.7
    )

    questions = []

    sentences = [
        sentence.strip()
        for sentence in text.split(". ")
        if len(sentence.strip()) > 20
    ]

    sentences = sentences[:100]

    for output in outputs:

        question = tokenizer.decode(
            output,
            skip_special_tokens=True
        ).strip()

        if not question:
            continue

        if not question.endswith("?"):
            question += "?"

        try:

            answer = qa_pipeline(
                question=question,
                context=text
            )["answer"]

        except Exception:

            continue

        if not answer:
            continue

        distractors = get_synonyms(
            answer
        )[:2]

        candidate_sentences = [
            sentence
            for sentence in sentences
            if answer.lower()
            not in sentence.lower()
        ]

        if candidate_sentences:

            try:

                answer_embedding = (
                    similarity_model.encode(
                        answer
                    )
                )

                sentence_embeddings = (
                    similarity_model.encode(
                        candidate_sentences
                    )
                )

                similarities = cosine_similarity(
                    [answer_embedding],
                    sentence_embeddings
                )[0]

                ranked = sorted(
                    range(len(similarities)),
                    key=lambda i: similarities[i]
                )

                for index in ranked:

                    if len(distractors) >= 3:
                        break

                    candidate = candidate_sentences[index]

                    if candidate not in distractors:
                        distractors.append(
                            candidate
                        )

            except Exception:
                pass

        while len(distractors) < 3:

            if candidate_sentences:

                distractors.append(
                    random.choice(
                        candidate_sentences
                    )
                )

            else:

                distractors.append(
                    answer[::-1]
                )

        options = [
            answer
        ] + distractors[:3]

        random.shuffle(
            options
        )

        questions.append({
            "question": question,
            "options": options,
            "answer": answer
        })

    return questions