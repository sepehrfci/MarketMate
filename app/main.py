import os

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

app = FastAPI(title="MarketMate")
app_name = os.getenv("APP_NAME", "MarketMate")
app_env = os.getenv("APP_ENV", "development")
http_requests = Counter(
    "marketmate_http_requests",
    "Number of HTTP requests handled by MarketMate",
    ["method", "path"],
)


@app.middleware("http")
async def count_requests(request: Request, call_next):
    response = await call_next(request)
    http_requests.labels(request.method, request.url.path).inc()
    return response


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/status")
def status():
    return {"app": app_name, "environment": app_env, "status": "running"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
