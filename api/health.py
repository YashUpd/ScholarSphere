from fastapi import FastAPI


app = FastAPI(
    title="ScholarSphere API"
)


@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "service": "ScholarSphere API"
    }