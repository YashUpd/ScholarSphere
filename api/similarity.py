from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile

from backend.similarity_service import analyze_similarity


app = FastAPI(
    title="ScholarSphere Similarity API"
)


MAX_FILE_SIZE = 4 * 1024 * 1024


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