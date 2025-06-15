from fastapi import APIRouter, HTTPException
from database import db_pool
from config import settings
import pyodbc

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