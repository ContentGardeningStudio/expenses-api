from fastapi import FastAPI

app = FastAPI(title="Expenses API")


@app.get("/health")
def health():
    return {"status": "ok"}
