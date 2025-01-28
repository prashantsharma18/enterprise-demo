from fastapi import FastAPI, Request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

# Initialize metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
SUCCESS_COUNT = Counter('http_success_total', 'Successful HTTP requests', ['endpoint'])

app = FastAPI(
    title="Enterprise Demo App",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
async def root():
    REQUEST_COUNT.labels(method='GET', endpoint='/', status='200').inc()
    SUCCESS_COUNT.labels(endpoint='/').inc()
    return {
        "message": "Welcome to Enterprise Demo App",
        "version": "1.0.0",
        "environment": "production"
    }

@app.get("/health")
async def health_check():
    REQUEST_COUNT.labels(method='GET', endpoint='/health', status='200').inc()
    SUCCESS_COUNT.labels(endpoint='/health').inc()
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    REQUEST_COUNT.labels(method='GET', endpoint='/ready', status='200').inc()
    SUCCESS_COUNT.labels(endpoint='/ready').inc()
    return {"status": "ready"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

