from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from backend.summary_service import summarize_documents


app = FastAPI(
    title="ScholarSphere Summarization API"
)


MAX_FILE_SIZE = 4 * 1024 * 1024


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
                    f"{file.filename} is larger than 4 MB. "
                    "Vercel Functions have a 4.5 MB request limit."
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