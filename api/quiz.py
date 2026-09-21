from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from backend.document import extract_text
from backend.quiz_service import generate_quiz


app = FastAPI(
    title="ScholarSphere Quiz API"
)


MAX_FILE_SIZE = 4 * 1024 * 1024


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