from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

# Initialize metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Add response time histogram
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

# Add application status gauge
APP_STATUS = Gauge(
    'application_status',
    'Current application status (1 = up, 0 = down)'
)

# Add info metric for version tracking
APP_INFO = Gauge(
    'application_info',
    'Application information',
    ['version', 'environment']
)

app = FastAPI(
    title="Enterprise Demo App",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    # Set application status to up
    APP_STATUS.set(1)
    # Set application info
    APP_INFO.labels(version="1.0.0", environment="production").set(1)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Use contextmanager for timing
    method = request.method
    path = request.url.path
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        
        # Record request count and latency
        REQUEST_COUNT.labels(
            method=method,
            endpoint=path,
            status=status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=method,
            endpoint=path
        ).observe(time.time() - start_time)
        
        response.headers["X-Process-Time"] = str(time.time() - start_time)
        return response
        
    except Exception as e:
        # Record failed requests
        REQUEST_COUNT.labels(
            method=method,
            endpoint=path,
            status=500
        ).inc()
        raise e

@app.get("/")
async def root():
    return {
        "message": "Welcome to Enterprise Demo App",
        "version": "1.0.0",
        "environment": "production"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)