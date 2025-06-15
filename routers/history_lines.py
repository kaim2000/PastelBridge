from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import db_pool
from config import settings
import logging
from models import HistoryLine, HistoryLineResponse, PaginationMetadata
from datetime import datetime, date
import base64
import re

# Define the router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/history-lines", response_model=HistoryLineResponse)
async def get_history_lines(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    document_type: Optional[int] = Query(None, description="Filter by document type"),
    document_number: Optional[str] = Query(None, description="Filter by document number"),
    customer_code: Optional[str] = Query(None, description="Filter by customer code"),
    item_code: Optional[str] = Query(None, description="Filter by item code")
):
    """Get a paginated list of history lines"""
    logger.info(f"History lines request: cursor={cursor}, limit={limit}, document_type={document_type}, document_number={document_number}, customer_code={customer_code}, item_code={item_code}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor_obj = conn.cursor()
            
            # Build the field list - MUST match exact database column names
            fields = [
                "UserId", "DocumentType", "DocumentNumber", "ItemCode",
                "CustomerCode", "SalesmanCode", "SearchType", "PPeriod",
                "DDate", "UnitUsed", "TaxType", "DiscountType",
                "DiscountPercentage", "Description", "CostPrice", "Qty",
                "UnitPrice", "InclusivePrice", "FCurrUnitPrice", "FCurrInclPrice",
                "TaxAmt", "FCurrTaxAmount", "DiscountAmount", "FCDiscountAmount",
                "CostCode", "DateTime", "Physical", "Fixed", "ShowQty",
                "LinkNum", "LinkedNum", "GRNQty", "LinkID", "MultiStore",
                "IsTMBLine", "LinkDocumentType", "LinkDocumentNumber",
                "Exported", "ExportRef", "ExportNum", "QtyLeft",
                "CaseLotCode", "CaseLotQty", "CaseLotRatio", "CostSyncDone"
            ]
            
            # Build query - single line to avoid ODBC truncation issues
            field_list = ", ".join(fields)
            query = f"SELECT TOP {limit + 1} {field_list} FROM HistoryLines WHERE 1=1"
            params = []
            
            # Add filters
            if document_type is not None:
                query += " AND DocumentType = ?"
                params.append(document_type)
            
            if document_number:
                query += " AND DocumentNumber = ?"
                params.append(document_number)
            
            if customer_code:
                query += " AND CustomerCode = ?"
                params.append(customer_code)
            
            if item_code:
                query += " AND ItemCode = ?"
                params.append(item_code)
            
            # Add cursor for pagination
            if cursor:
                decoded_cursor = base64.b64decode(cursor).decode('utf-8')
                # Decode as DocumentType:DocumentNumber:LinkNum
                parts = decoded_cursor.split(':', 2)
                if len(parts) == 3:
                    query += " AND (DocumentType > ? OR (DocumentType = ? AND DocumentNumber > ?) OR (DocumentType = ? AND DocumentNumber = ? AND LinkNum > ?))"
                    params.extend([int(parts[0]), int(parts[0]), parts[1], int(parts[0]), parts[1], int(parts[2])])
            
            # Order by primary keys
            query += " ORDER BY DocumentType, DocumentNumber, LinkNum"
            
            logger.debug(f"Executing query with {len(params)} parameters")
            cursor_obj.execute(query, params)
            
            history_lines = []
            rows = cursor_obj.fetchall()
            
            # Process up to limit rows
            for i, row in enumerate(rows[:limit]):
                line_data = {}
                for j, field in enumerate(fields):
                    # Convert field name to snake_case for the model
                    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', field)
                    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
                    s3 = re.sub(r'([a-zA-Z])(\d)', r'\1_\2', s2)
                    snake_case_field = s3.lower()
                    value = row[j]
                    
                    # Handle different data types
                    if field == 'DDate' and value:
                        # Date field handling
                        if isinstance(value, str):
                            try:
                                if '/' in value:
                                    line_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y').date()
                                else:
                                    line_data[snake_case_field] = datetime.fromisoformat(value).date()
                            except:
                                line_data[snake_case_field] = None
                        else:
                            line_data[snake_case_field] = value
                    elif field == 'DateTime' and value:
                        # DateTime field handling
                        if isinstance(value, str):
                            try:
                                line_data[snake_case_field] = datetime.fromisoformat(value)
                            except:
                                line_data[snake_case_field] = None
                        else:
                            line_data[snake_case_field] = value
                    elif isinstance(value, str):
                        # Trim string values
                        line_data[snake_case_field] = value.strip()
                    else:
                        line_data[snake_case_field] = value
                
                history_lines.append(HistoryLine(**line_data))
            
            # Determine if there are more results
            has_more = len(rows) > limit
            next_cursor = None
            if has_more and history_lines:
                # Use composite cursor: DocumentType:DocumentNumber:LinkNum
                last_line = history_lines[-1]
                cursor_value = f"{last_line.document_type}:{last_line.document_number}:{last_line.link_num}"
                next_cursor = base64.b64encode(cursor_value.encode('utf-8')).decode('utf-8')
            
            logger.info(f"Retrieved {len(history_lines)} history lines")
            
            # Build response
            metadata = PaginationMetadata(
                page_size=limit,
                cursor=cursor,
                next_cursor=next_cursor,
                has_more=has_more,
                timestamp=datetime.now()
            )
            
            return HistoryLineResponse(data=history_lines, metadata=metadata)
            
    except Exception as e:
        logger.error(f"Error fetching history lines: {e}")
        logger.error(f"Query parameters: cursor={cursor}, limit={limit}, document_type={document_type}, document_number={document_number}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch history lines: {str(e)}")

# Single history line endpoint
@router.get("/history-lines/{document_type}/{document_number}/{link_num}", response_model=HistoryLine)
async def get_history_line(document_type: int, document_number: str, link_num: int):
    """Get a single history line by document type, number and link number"""
    logger.info(f"History line detail request: document_type={document_type}, document_number={document_number}, link_num={link_num}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all fields
            fields = [
                "UserId", "DocumentType", "DocumentNumber", "ItemCode",
                "CustomerCode", "SalesmanCode", "SearchType", "PPeriod",
                "DDate", "UnitUsed", "TaxType", "DiscountType",
                "DiscountPercentage", "Description", "CostPrice", "Qty",
                "UnitPrice", "InclusivePrice", "FCurrUnitPrice", "FCurrInclPrice",
                "TaxAmt", "FCurrTaxAmount", "DiscountAmount", "FCDiscountAmount",
                "CostCode", "DateTime", "Physical", "Fixed", "ShowQty",
                "LinkNum", "LinkedNum", "GRNQty", "LinkID", "MultiStore",
                "IsTMBLine", "LinkDocumentType", "LinkDocumentNumber",
                "Exported", "ExportRef", "ExportNum", "QtyLeft",
                "CaseLotCode", "CaseLotQty", "CaseLotRatio", "CostSyncDone"
            ]
            
            # Single line query to avoid ODBC truncation
            field_list = ", ".join(fields)
            query = f"SELECT {field_list} FROM HistoryLines WHERE DocumentType = ? AND DocumentNumber = ? AND LinkNum = ?"
            
            cursor.execute(query, [document_type, document_number, link_num])
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"History line not found: {document_type}/{document_number}/{link_num}")
            
            # Build history line object
            line_data = {}
            for j, field in enumerate(fields):
                # Convert field name to snake_case
                s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', field)
                s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
                s3 = re.sub(r'([a-zA-Z])(\d)', r'\1_\2', s2)
                snake_case_field = s3.lower()
                value = row[j]
                
                # Handle data types
                if field == 'DDate' and value:
                    if isinstance(value, str):
                        try:
                            if '/' in value:
                                line_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y').date()
                            else:
                                line_data[snake_case_field] = datetime.fromisoformat(value).date()
                        except:
                            line_data[snake_case_field] = None
                    else:
                        line_data[snake_case_field] = value
                elif field == 'DateTime' and value:
                    if isinstance(value, str):
                        try:
                            line_data[snake_case_field] = datetime.fromisoformat(value)
                        except:
                            line_data[snake_case_field] = None
                    else:
                        line_data[snake_case_field] = value
                elif isinstance(value, str):
                    line_data[snake_case_field] = value.strip()
                else:
                    line_data[snake_case_field] = value
            
            history_line = HistoryLine(**line_data)
            logger.info(f"Retrieved history line: {document_type}/{document_number}/{link_num}")
            
            return history_line
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching history line {document_type}/{document_number}/{link_num}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch history line: {str(e)}")

# Get history lines for a specific invoice
@router.get("/invoices/{document_type}/{document_number}/lines", response_model=HistoryLineResponse)
async def get_invoice_lines(
    document_type: int,
    document_number: str,
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size)
):
    """Get all history lines for a specific invoice"""
    logger.info(f"Invoice lines request: document_type={document_type}, document_number={document_number}, cursor={cursor}, limit={limit}")
    
    # Reuse the main get_history_lines function with filters
    return await get_history_lines(
        cursor=cursor,
        limit=limit,
        document_type=document_type,
        document_number=document_number,
        customer_code=None,
        item_code=None
    ) 