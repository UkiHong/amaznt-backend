from fastapi import FastAPI

app = FastAPI(title="Amazn't Backend")


@app.get("/")
def read_root():
    return {"message": "Amazn't backend is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
