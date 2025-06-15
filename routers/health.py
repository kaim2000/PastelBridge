from fastapi import APIRouter, HTTPException
from database import db_pool, circuit_breaker
from config import settings
import pyodbc
from datetime import datetime
import time

router = APIRouter()

@router.get("/ping")
async def health_check():
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # For Actian PSQL, we'll just do a simple query to verify connection
            # Instead of getting version, let's just count tables or do a simple SELECT
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            # Try to get some database info if possible
            try:
                # Get table count as a health indicator
                cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_type = 'BASE TABLE'")
                table_count = cursor.fetchone()[0]
            except:
                table_count = "unknown"
            
            return {
                "status": "healthy",
                "database": "connected",
                "connection_test": result[0],
                "table_count": table_count,
                "dsn": settings.dsn_name
            }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@router.get("/health")
async def detailed_health_check():
    """Detailed health check endpoint as per API documentation"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": None,  # Would need to track app start time
        "checks": {
            "database": {
                "status": "healthy",
                "latency_ms": None,
                "details": {}
            },
            "api": {
                "status": "healthy",
                "response_time_ms": None
            }
        }
    }
    
    # Check database health
    try:
        start_time = time.time()
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            db_latency = (time.time() - start_time) * 1000  # Convert to ms
            health_status["checks"]["database"]["latency_ms"] = round(db_latency, 2)
            
            # Check circuit breaker status
            if circuit_breaker.is_open:
                health_status["checks"]["database"]["status"] = "degraded"
                health_status["checks"]["database"]["details"]["circuit_breaker"] = "open"
                health_status["checks"]["database"]["details"]["failure_count"] = circuit_breaker.failure_count
                health_status["status"] = "degraded"
            else:
                health_status["checks"]["database"]["details"]["circuit_breaker"] = "closed"
                
    except Exception as e:
        health_status["checks"]["database"]["status"] = "unhealthy"
        health_status["checks"]["database"]["details"]["error"] = str(e)
        health_status["status"] = "unhealthy"
    
    # Overall API response time (simulated)
    health_status["checks"]["api"]["response_time_ms"] = round((time.time() - time.time()) * 1000, 2)
    
    # Return appropriate status code based on health
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    elif health_status["status"] == "degraded":
        return health_status  # 200 with degraded status
    else:
        return health_status