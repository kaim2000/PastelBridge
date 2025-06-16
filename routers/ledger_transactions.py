from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import db_pool
from config import settings
import logging
from models import LedgerTransaction, LedgerTransactionResponse, PaginationMetadata
from datetime import datetime, date
import base64
import re

# Define the router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/ledger-transactions", response_model=LedgerTransactionResponse)
async def get_ledger_transactions(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    gdc: Optional[str] = Query(None, description="Filter by GDC (G/D/C)"),
    acc_number: Optional[str] = Query(None, description="Filter by account number"),
    p_period: Optional[int] = Query(None, description="Filter by period"),
    from_date: Optional[date] = Query(None, description="Filter transactions from this date"),
    to_date: Optional[date] = Query(None, description="Filter transactions up to this date"),
    e_type: Optional[int] = Query(None, description="Filter by entry type"),
    refrence: Optional[str] = Query(None, description="Filter by reference"),
    min_amount: Optional[float] = Query(None, description="Filter by minimum amount"),
    max_amount: Optional[float] = Query(None, description="Filter by maximum amount"),
    description: Optional[str] = Query(None, description="Filter by description (partial match)"),
    link_id: Optional[int] = Query(None, description="Filter by link ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    transaction_id: Optional[int] = Query(None, description="Filter by transaction ID"),
    link_acc: Optional[str] = Query(None, description="Filter by linked account")
):
    """Get a paginated list of ledger transactions"""
    logger.info(f"Ledger transaction request: cursor={cursor}, limit={limit}, filters: gdc={gdc}, acc_number={acc_number}, p_period={p_period}, from_date={from_date}, to_date={to_date}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor_obj = conn.cursor()
            
            # Build the field list - MUST match exact database column names
            fields = [
                "AutoNumber", "GDC", "AccNumber", "DiscFlag", "CurrCode", 
                "Spare", "PPeriod", "DDate", "EType", "Refrence", 
                "JobCode", "Amount", "TaxAmt", "ThisCurrTaxAmount", 
                "BankTaxAmount", "CurrAmt", "BankCurrAmount", "ReconFlag", 
                "Description", "TaxType", "Country", "Generated", 
                "PayBased", "UserID", "WhichUserRef", "LinkAcc", 
                "UpdateReconFlag", "ChequeFlag", "LinkID", "InInv", 
                "TaxReportDate", "TaxReportPeriod", "BatchID", 
                "TransactionID", "Exported", "ExportRef", "ExportNum", 
                "CostSyncDone"
            ]
            
            # Build query - single line to avoid ODBC truncation issues
            field_list = ", ".join(fields)
            query = f"SELECT TOP {limit + 1} {field_list} FROM LedgerTransactions WHERE 1=1"
            params = []
            
            # Add filters
            if gdc:
                query += " AND GDC = ?"
                params.append(gdc)
            
            if acc_number:
                query += " AND AccNumber = ?"
                params.append(acc_number)
            
            if p_period is not None:
                query += " AND PPeriod = ?"
                params.append(p_period)
            
            if from_date:
                query += " AND DDate >= ?"
                params.append(from_date)
            
            if to_date:
                query += " AND DDate <= ?"
                params.append(to_date)
            
            if e_type is not None:
                query += " AND EType = ?"
                params.append(e_type)
            
            if refrence:
                query += " AND Refrence = ?"
                params.append(refrence)
            
            if min_amount is not None:
                query += " AND Amount >= ?"
                params.append(min_amount)
            
            if max_amount is not None:
                query += " AND Amount <= ?"
                params.append(max_amount)
            
            if description:
                # Partial match for description
                query += " AND Description LIKE ?"
                params.append(f"%{description}%")
            
            if link_id is not None:
                query += " AND LinkID = ?"
                params.append(link_id)
            
            if user_id is not None:
                query += " AND UserID = ?"
                params.append(user_id)
            
            if transaction_id is not None:
                query += " AND TransactionID = ?"
                params.append(transaction_id)
            
            if link_acc:
                query += " AND LinkAcc = ?"
                params.append(link_acc)
            
            # Add cursor for pagination
            if cursor:
                decoded_cursor = base64.b64decode(cursor).decode('utf-8')
                query += " AND AutoNumber > ?"
                params.append(int(decoded_cursor))
            
            # Order by primary key
            query += " ORDER BY AutoNumber"
            
            logger.debug(f"Executing query with {len(params)} parameters")
            cursor_obj.execute(query, params)
            
            transactions = []
            rows = cursor_obj.fetchall()
            
            # Process up to limit rows
            for i, row in enumerate(rows[:limit]):
                transaction_data = {}
                for j, field in enumerate(fields):
                    # Convert field name to snake_case for the model
                    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                    s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                    snake_case_field = s3.lower()
                    value = row[j]
                    
                    # Handle different data types
                    if field in ['DDate', 'TaxReportDate'] and value:
                        # Date field handling
                        if isinstance(value, str):
                            try:
                                if '/' in value:
                                    transaction_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y').date()
                                else:
                                    transaction_data[snake_case_field] = datetime.fromisoformat(value).date()
                            except:
                                transaction_data[snake_case_field] = None
                        else:
                            transaction_data[snake_case_field] = value
                    elif isinstance(value, str):
                        # List of fields that should be integers
                        integer_fields = [
                            'CurrCode', 'PPeriod', 'EType', 'ReconFlag', 'TaxType',
                            'UserID', 'UpdateReconFlag', 'ChequeFlag', 'LinkID',
                            'InInv', 'TaxReportPeriod', 'BatchID', 'TransactionID',
                            'Exported', 'ExportNum'
                        ]
                        
                        # Handle special characters in numeric fields
                        if field in integer_fields and value in ['\x00', '', ' ', None]:
                            transaction_data[snake_case_field] = 0
                        else:
                            # Trim string values
                            transaction_data[snake_case_field] = value.strip()
                    else:
                        transaction_data[snake_case_field] = value
                
                transactions.append(LedgerTransaction(**transaction_data))
            
            # Determine if there are more results
            has_more = len(rows) > limit
            next_cursor = None
            if has_more and transactions:
                next_cursor = base64.b64encode(str(transactions[-1].auto_number).encode('utf-8')).decode('utf-8')
            
            logger.info(f"Retrieved {len(transactions)} ledger transactions")
            
            # Build response
            metadata = PaginationMetadata(
                page_size=limit,
                cursor=cursor,
                next_cursor=next_cursor,
                has_more=has_more,
                timestamp=datetime.now()
            )
            
            return LedgerTransactionResponse(data=transactions, metadata=metadata)
            
    except Exception as e:
        logger.error(f"Error fetching ledger transactions: {e}")
        logger.error(f"Query parameters: cursor={cursor}, limit={limit}, gdc={gdc}, acc_number={acc_number}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ledger transactions: {str(e)}")

# Single record endpoint
@router.get("/ledger-transactions/{auto_number}", response_model=LedgerTransaction)
async def get_ledger_transaction(auto_number: int):
    """Get a single ledger transaction by auto number"""
    logger.info(f"Ledger transaction detail request: auto_number={auto_number}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all fields
            fields = [
                "AutoNumber", "GDC", "AccNumber", "DiscFlag", "CurrCode", 
                "Spare", "PPeriod", "DDate", "EType", "Refrence", 
                "JobCode", "Amount", "TaxAmt", "ThisCurrTaxAmount", 
                "BankTaxAmount", "CurrAmt", "BankCurrAmount", "ReconFlag", 
                "Description", "TaxType", "Country", "Generated", 
                "PayBased", "UserID", "WhichUserRef", "LinkAcc", 
                "UpdateReconFlag", "ChequeFlag", "LinkID", "InInv", 
                "TaxReportDate", "TaxReportPeriod", "BatchID", 
                "TransactionID", "Exported", "ExportRef", "ExportNum", 
                "CostSyncDone"
            ]
            
            # Single line query to avoid ODBC truncation
            field_list = ", ".join(fields)
            query = f"SELECT {field_list} FROM LedgerTransactions WHERE AutoNumber = ?"
            
            cursor.execute(query, [auto_number])
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Ledger transaction not found: {auto_number}")
            
            # Build transaction object
            transaction_data = {}
            for j, field in enumerate(fields):
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                snake_case_field = s3.lower()
                value = row[j]
                
                # Handle data types
                if field in ['DDate', 'TaxReportDate'] and value:
                    if isinstance(value, str):
                        try:
                            if '/' in value:
                                transaction_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y').date()
                            else:
                                transaction_data[snake_case_field] = datetime.fromisoformat(value).date()
                        except:
                            transaction_data[snake_case_field] = None
                    else:
                        transaction_data[snake_case_field] = value
                elif isinstance(value, str):
                    # List of fields that should be integers
                    integer_fields = [
                        'CurrCode', 'PPeriod', 'EType', 'ReconFlag', 'TaxType',
                        'UserID', 'UpdateReconFlag', 'ChequeFlag', 'LinkID',
                        'InInv', 'TaxReportPeriod', 'BatchID', 'TransactionID',
                        'Exported', 'ExportNum'
                    ]
                    
                    # Handle special characters in numeric fields
                    if field in integer_fields and value in ['\x00', '', ' ', None]:
                        transaction_data[snake_case_field] = 0
                    else:
                        transaction_data[snake_case_field] = value.strip()
                else:
                    transaction_data[snake_case_field] = value
            
            transaction = LedgerTransaction(**transaction_data)
            logger.info(f"Retrieved ledger transaction: {auto_number}")
            
            return transaction
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ledger transaction {auto_number}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ledger transaction: {str(e)}") 