from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from backend.document import extract_text
from backend.summary_service import summarize_documents
from backend.similarity_service import analyze_similarity
from backend.quiz_service import generate_quiz
from backend.research_service import (
    extract_topics,
    search_related_papers,
)


app = FastAPI(
    title="ScholarSphere API"
)


MAX_FILE_SIZE = 4 * 1024 * 1024


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "service": "ScholarSphere API"
    }


# ============================================================
# SUMMARIZATION
# ============================================================

@app.post("/api/summarize")
async def summarize(
    files: List[UploadFile] = File(...),
    max_length: int = Form(150),
    min_length: int = Form(50)
):

    if not files:

        raise HTTPException(
            status_code=400,
            detail="No files uploaded."
        )

    if max_length < 50 or max_length > 300:

        raise HTTPException(
            status_code=400,
            detail="max_length must be between 50 and 300."
        )

    if min_length < 10 or min_length >= max_length:

        raise HTTPException(
            status_code=400,
            detail="Invalid summary length settings."
        )

    documents = []

    for file in files:

        file_bytes = await file.read()

        if len(file_bytes) > MAX_FILE_SIZE:

            raise HTTPException(
                status_code=413,
                detail=(
                    f"{file.filename} is larger than 4 MB."
                    " Vercel Functions have a 4.5 MB request limit."
                )
            )

        documents.append(
            (
                file.filename or "document",
                file_bytes
            )
        )

    try:

        return summarize_documents(
            documents,
            max_length=max_length,
            min_length=min_length
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ============================================================
# SIMILARITY
# ============================================================

@app.post("/api/similarity")
async def similarity(
    files: List[UploadFile] = File(...)
):

    if len(files) < 2:

        raise HTTPException(
            status_code=400,
            detail="Upload at least two documents."
        )

    documents = []

    for file in files:

        file_bytes = await file.read()

        if len(file_bytes) > MAX_FILE_SIZE:

            raise HTTPException(
                status_code=413,
                detail=(
                    f"{file.filename} is larger than 4 MB."
                )
            )

        documents.append(
            (
                file.filename or "document",
                file_bytes
            )
        )

    try:

        return analyze_similarity(
            documents
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# ============================================================
# QUIZ
# ============================================================

@app.post("/api/quiz")
async def quiz(
    files: List[UploadFile] = File(...),
    num_questions: int = Form(3)
):

    if num_questions < 1 or num_questions > 10:

        raise HTTPException(
            status_code=400,
            detail="Number of questions must be between 1 and 10."
        )

    all_questions = []

    for file in files:

        file_bytes = await file.read()

        if len(file_bytes) > MAX_FILE_SIZE:

            raise HTTPException(
                status_code=413,
                detail=(
                    f"{file.filename} is larger than 4 MB."
                )
            )

        try:

            text = extract_text(
                file.filename or "document.txt",
                file_bytes
            )

            questions = generate_quiz(
                text,
                num_questions=num_questions
            )

            for question in questions:

                question["filename"] = (
                    file.filename
                    or "document"
                )

            all_questions.extend(
                questions
            )

        except Exception:

            continue

    return {
        "questions": all_questions
    }


# ============================================================
# RESEARCH EXPLORER
# ============================================================

@app.post("/api/research")
async def research(
    file: UploadFile = File(...)
):

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=413,
            detail="File is larger than 4 MB."
        )

    try:

        text = extract_text(
            file.filename or "document.txt",
            file_bytes
        )

        topics = extract_topics(
            text
        )

        papers = search_related_papers(
            topics
        )

        return {
            "topics": topics,
            "papers": papers
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )