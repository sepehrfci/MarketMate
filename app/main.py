from fastapi import FastAPI

app = FastAPI(title="MarketMate")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/status")
def status():
    return {"app": "MarketMate", "status": "running"}
