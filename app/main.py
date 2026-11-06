import os

from fastapi import FastAPI

app = FastAPI(title="MarketMate")
app_name = os.getenv("APP_NAME", "MarketMate")
app_env = os.getenv("APP_ENV", "development")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/status")
def status():
    return {"app": app_name, "environment": app_env, "status": "running"}
