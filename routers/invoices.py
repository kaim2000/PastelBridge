from fastapi import APIRouter, HTTPException, Query
from datetime import date
from typing import List, Optional
from models import Invoice, InvoiceQuery
from database import db_pool
from config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/invoices", response_model=List[Invoice])
async def get_invoices(
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    account_code: Optional[str] = None,
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size)
):
    # Log request parameters
    logger.info(f"Invoice request: from={from_date}, to={to_date}, account_code={account_code}, limit={limit}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # PSQL uses TOP instead of LIMIT
            # Using NOLOCK to reduce lock contention
            query = f"""
                SELECT TOP {limit}
                    DocumentNumber,
                    DocumentDate,
                    CustomerCode
                FROM HistoryHeader
                WHERE DocumentDate >= ? AND DocumentDate <= ?
            """
            params = [from_date, to_date]
            
            if account_code:
                query += " AND CustomerCode = ?"
                params.append(account_code)
                
            query += " ORDER BY DocumentDate DESC"
            
            # Log the query being executed
            logger.debug(f"Executing query: {query}")
            logger.debug(f"Parameters: {params}")
            
            cursor.execute(query, params)
            
            invoices = []
            row_count = 0
            for row in cursor.fetchall():
                row_count += 1
                invoices.append(Invoice(
                    document_number=row.DocumentNumber,
                    document_date=row.DocumentDate,
                    account_code=row.CustomerCode
                ))
            
            logger.info(f"Retrieved {row_count} invoices for date range {from_date} to {to_date}")
            
            return invoices
            
    except Exception as e:
        logger.error(f"Error fetching invoices: {e}")
        logger.error(f"Query parameters: from={from_date}, to={to_date}, account_code={account_code}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")