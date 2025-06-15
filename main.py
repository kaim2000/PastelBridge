from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import uvicorn
from config import settings
from routers import health, invoices, customers, delivery_addresses, history_lines
import time
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pastel_bridge.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pastel Bridge API",
    description="Bridge API for Pastel Partner integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_ips_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log detailed information about each request and response"""
    start_time = time.time()
    
    # Get request details
    client_ip = request.client.host
    method = request.method
    url = str(request.url)
    path = request.url.path
    query_params = dict(request.query_params)
    headers = dict(request.headers)
    
    # Remove sensitive headers from logging
    safe_headers = {k: v for k, v in headers.items() if k.lower() not in ['x-api-key', 'authorization']}
    safe_headers['x-api-key'] = '***' if 'x-api-key' in headers else 'missing'
    
    # Log incoming request
    logger.info(f"Incoming request: {method} {path} from {client_ip}")
    logger.debug(f"Query params: {json.dumps(query_params)}")
    logger.debug(f"Headers: {json.dumps(safe_headers)}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(f"Response: {method} {path} - Status: {response.status_code} - IP: {client_ip} - Time: {process_time:.3f}s")
    
    # Log additional details for errors
    if response.status_code >= 400:
        logger.warning(f"Error response {response.status_code} for {method} {path} from {client_ip}")
        if response.status_code == 403:
            logger.warning(f"IP {client_ip} blocked - not in whitelist: {settings.allowed_ips_list}")
        elif response.status_code == 401:
            logger.warning(f"Invalid API key from {client_ip}")
        elif response.status_code == 422:
            logger.warning(f"Invalid parameters from {client_ip}: {json.dumps(query_params)}")
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# IP whitelist middleware
@app.middleware("http")
async def validate_ip(request: Request, call_next):
    client_ip = request.client.host
    path = request.url.path
    
    # Log IP check
    logger.debug(f"IP validation: {client_ip} accessing {path}")
    
    if settings.allowed_ips_list and client_ip not in settings.allowed_ips_list:
        logger.warning(f"Blocked IP {client_ip} - not in whitelist. Allowed IPs: {settings.allowed_ips_list}")
        return JSONResponse(
            status_code=403,
            content={"detail": "Access forbidden"}
        )
    return await call_next(request)

# API key validation
@app.middleware("http")
async def validate_api_key(request: Request, call_next):
    if request.url.path == "/docs" or request.url.path == "/openapi.json":
        return await call_next(request)
        
    api_key = request.headers.get("X-API-Key")
    if api_key != settings.api_key:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid API key"}
        )
    return await call_next(request)

# Rate limiting middleware with inter-request delay
from collections import defaultdict
import asyncio

request_counts = defaultdict(list)
last_request_time = defaultdict(float)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()
    
    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip] 
        if now - req_time < 60
    ]
    
    # Check rate limit (configurable requests per minute)
    if len(request_counts[client_ip]) >= settings.rate_limit_per_minute:
        logger.warning(f"Rate limit exceeded for {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={"X-Retry-After": "60"}
        )
    
    # Enforce minimum interval between requests
    last_request = last_request_time.get(client_ip, 0)
    time_since_last = (now - last_request) * 1000  # Convert to ms
    
    if time_since_last < settings.min_request_interval_ms:
        delay_ms = settings.min_request_interval_ms - time_since_last
        logger.debug(f"Delaying request from {client_ip} by {delay_ms:.0f}ms")
        await asyncio.sleep(delay_ms / 1000)
    
    request_counts[client_ip].append(now)
    last_request_time[client_ip] = time.time()
    
    return await call_next(request)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(invoices.router, prefix="/api", tags=["invoices"])
app.include_router(customers.router, prefix="/api", tags=["customers"])
app.include_router(delivery_addresses.router, prefix="/api", tags=["delivery-addresses"])
app.include_router(history_lines.router, prefix="/api", tags=["history-lines"])

@app.get("/")
async def root():
    return {"message": "Pastel Bridge API", "timestamp": datetime.now()}

if __name__ == "__main__":
    ssl_config = {}
    if settings.ssl_cert_file and settings.ssl_key_file:
        ssl_config = {
            "ssl_keyfile": settings.ssl_key_file,
            "ssl_certfile": settings.ssl_cert_file
        }
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        **ssl_config
    )