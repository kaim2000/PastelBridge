from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import db_pool
from config import settings
import logging
from models import Invoice, InvoiceResponse, PaginationMetadata
from datetime import datetime, date
import base64
import re

# Define the router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/invoices", response_model=InvoiceResponse)
async def get_invoices(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    from_date: Optional[date] = Query(None, description="Filter by start date"),
    to_date: Optional[date] = Query(None, description="Filter by end date"),
    customer_code: Optional[str] = Query(None, description="Filter by customer code"),
    document_type: Optional[int] = Query(None, description="Filter by document type"),
    document_number: Optional[str] = Query(None, description="Filter by document number")
):
    """Get a paginated list of invoices from HistoryHeader"""
    logger.info(f"Invoice request: cursor={cursor}, limit={limit}, from_date={from_date}, to_date={to_date}, customer_code={customer_code}, document_type={document_type}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor_obj = conn.cursor()
            
            # Build the field list - MUST match exact database column names
            fields = [
                "DocumentType", "DocumentNumber", "CustomerCode", "DocumentDate",
                "OrderNumber", "SalesmanCode", "UserID", "ExclIncl",
                "Message01", "Message02", "Message03",
                "DelAddress01", "DelAddress02", "DelAddress03", "DelAddress04", "DelAddress05",
                "Terms", "ExtraCosts", "CostCode", "PPeriod", "ClosingDate",
                "Telephone", "Fax", "Contact",
                "CurrencyCode", "ExchangeRate", "DiscountPercent",
                "Total", "FCurrTotal", "TotalTax", "FCurrTotalTax", "TotalCost",
                "InvDeleted", "InvPrintStatus", "Onhold", "GRNMisc", "Paid",
                "Freight01", "Ship", "IsTMBDoc", "Spare",
                "Exported", "ExportRef", "ExportNum", "Emailed"
            ]
            
            # Build query - single line to avoid ODBC truncation issues
            field_list = ", ".join(fields)
            query = f"SELECT TOP {limit + 1} {field_list} FROM HistoryHeader WHERE 1=1"
            params = []
            
            # Add filters
            if from_date:
                query += " AND DocumentDate >= ?"
                params.append(from_date)
            
            if to_date:
                query += " AND DocumentDate <= ?"
                params.append(to_date)
            
            if customer_code:
                query += " AND CustomerCode = ?"
                params.append(customer_code)
            
            if document_type is not None:
                query += " AND DocumentType = ?"
                params.append(document_type)
            
            if document_number:
                query += " AND DocumentNumber = ?"
                params.append(document_number)
            
            # Add cursor for pagination
            if cursor:
                decoded_cursor = base64.b64decode(cursor).decode('utf-8')
                # Decode as DocumentType:DocumentNumber
                parts = decoded_cursor.split(':', 1)
                if len(parts) == 2:
                    query += " AND (DocumentType > ? OR (DocumentType = ? AND DocumentNumber > ?))"
                    params.extend([int(parts[0]), int(parts[0]), parts[1]])
            
            # Order by primary keys
            query += " ORDER BY DocumentType, DocumentNumber"
            
            logger.debug(f"Executing query with {len(params)} parameters")
            cursor_obj.execute(query, params)
            
            invoices = []
            rows = cursor_obj.fetchall()
            
            # Process up to limit rows
            for i, row in enumerate(rows[:limit]):
                invoice_data = {}
                for j, field in enumerate(fields):
                    # Convert field name to snake_case for the model
                    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', field)
                    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
                    s3 = re.sub(r'([a-zA-Z])(\d)', r'\1_\2', s2)
                    snake_case_field = s3.lower()
                    value = row[j]
                    
                    # Handle different data types
                    if field in ['DocumentDate', 'ClosingDate'] and value:
                        # Date field handling
                        if isinstance(value, str):
                            try:
                                if '/' in value:
                                    invoice_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y').date()
                                else:
                                    invoice_data[snake_case_field] = datetime.fromisoformat(value).date()
                            except:
                                invoice_data[snake_case_field] = None
                        else:
                            invoice_data[snake_case_field] = value
                    elif isinstance(value, str):
                        # Trim string values
                        invoice_data[snake_case_field] = value.strip()
                    else:
                        invoice_data[snake_case_field] = value
                
                invoices.append(Invoice(**invoice_data))
            
            # Determine if there are more results
            has_more = len(rows) > limit
            next_cursor = None
            if has_more and invoices:
                # Use composite cursor: DocumentType:DocumentNumber
                last_invoice = invoices[-1]
                cursor_value = f"{last_invoice.document_type}:{last_invoice.document_number}"
                next_cursor = base64.b64encode(cursor_value.encode('utf-8')).decode('utf-8')
            
            logger.info(f"Retrieved {len(invoices)} invoices")
            
            # Build response
            metadata = PaginationMetadata(
                page_size=limit,
                cursor=cursor,
                next_cursor=next_cursor,
                has_more=has_more,
                timestamp=datetime.now()
            )
            
            return InvoiceResponse(data=invoices, metadata=metadata)
            
    except Exception as e:
        logger.error(f"Error fetching invoices: {e}")
        logger.error(f"Query parameters: cursor={cursor}, limit={limit}, from_date={from_date}, to_date={to_date}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")

# Single invoice endpoint
@router.get("/invoices/{document_type}/{document_number}", response_model=Invoice)
async def get_invoice(document_type: int, document_number: str):
    """Get a single invoice by document type and number"""
    logger.info(f"Invoice detail request: document_type={document_type}, document_number={document_number}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all fields
            fields = [
                "DocumentType", "DocumentNumber", "CustomerCode", "DocumentDate",
                "OrderNumber", "SalesmanCode", "UserID", "ExclIncl",
                "Message01", "Message02", "Message03",
                "DelAddress01", "DelAddress02", "DelAddress03", "DelAddress04", "DelAddress05",
                "Terms", "ExtraCosts", "CostCode", "PPeriod", "ClosingDate",
                "Telephone", "Fax", "Contact",
                "CurrencyCode", "ExchangeRate", "DiscountPercent",
                "Total", "FCurrTotal", "TotalTax", "FCurrTotalTax", "TotalCost",
                "InvDeleted", "InvPrintStatus", "Onhold", "GRNMisc", "Paid",
                "Freight01", "Ship", "IsTMBDoc", "Spare",
                "Exported", "ExportRef", "ExportNum", "Emailed"
            ]
            
            # Single line query to avoid ODBC truncation
            field_list = ", ".join(fields)
            query = f"SELECT {field_list} FROM HistoryHeader WHERE DocumentType = ? AND DocumentNumber = ?"
            
            cursor.execute(query, [document_type, document_number])
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Invoice not found: {document_type}/{document_number}")
            
            # Build invoice object
            invoice_data = {}
            for j, field in enumerate(fields):
                # Convert field name to snake_case
                s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', field)
                s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
                s3 = re.sub(r'([a-zA-Z])(\d)', r'\1_\2', s2)
                snake_case_field = s3.lower()
                value = row[j]
                
                # Handle data types
                if field in ['DocumentDate', 'ClosingDate'] and value:
                    if isinstance(value, str):
                        try:
                            if '/' in value:
                                invoice_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y').date()
                            else:
                                invoice_data[snake_case_field] = datetime.fromisoformat(value).date()
                        except:
                            invoice_data[snake_case_field] = None
                    else:
                        invoice_data[snake_case_field] = value
                elif isinstance(value, str):
                    invoice_data[snake_case_field] = value.strip()
                else:
                    invoice_data[snake_case_field] = value
            
            invoice = Invoice(**invoice_data)
            logger.info(f"Retrieved invoice: {document_type}/{document_number}")
            
            return invoice
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching invoice {document_type}/{document_number}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoice: {str(e)}")

# Get invoices by customer
@router.get("/customers/{customer_code}/invoices", response_model=InvoiceResponse)
async def get_customer_invoices(
    customer_code: str,
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    from_date: Optional[date] = Query(None, description="Filter by start date"),
    to_date: Optional[date] = Query(None, description="Filter by end date")
):
    """Get all invoices for a specific customer"""
    logger.info(f"Customer invoices request: customer_code={customer_code}, cursor={cursor}, limit={limit}")
    
    # Reuse the main get_invoices function with customer_code filter
    return await get_invoices(
        cursor=cursor,
        limit=limit,
        from_date=from_date,
        to_date=to_date,
        customer_code=customer_code,
        document_type=None,
        document_number=None
    )