from fastapi import FastAPI, File, HTTPException, UploadFile

from backend.document import extract_text
from backend.research_service import (
    extract_topics,
    search_related_papers
)


app = FastAPI(
    title="ScholarSphere Research API"
)


MAX_FILE_SIZE = 4 * 1024 * 1024


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