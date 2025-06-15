from fastapi import APIRouter, HTTPException, Query
from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from database import db_pool
from config import settings
import logging
from models import CustomerMaster, CustomerMasterResponse, PaginationMetadata
from datetime import datetime
import base64
import re

# Define the router
router = APIRouter()
logger = logging.getLogger(__name__)

# Customer model
class Customer(BaseModel):
    customer_code: str
    customer_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

@router.get("/customers", response_model=CustomerMasterResponse)
async def get_customers(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    customer_code: Optional[str] = Query(None, description="Filter by customer code"),
    category: Optional[int] = Query(None, description="Filter by category")
):
    """Get a paginated list of customers with all fields"""
    logger.info(f"Customer request: cursor={cursor}, limit={limit}, customer_code={customer_code}, category={category}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor_obj = conn.cursor()
            
            # Build the field list - all CustomerMaster fields
            fields = [
                "Category", "CustomerCode", "CustomerDesc",
                # Balance fields - This Year
                "BalanceThis01", "BalanceThis02", "BalanceThis03", "BalanceThis04", "BalanceThis05",
                "BalanceThis06", "BalanceThis07", "BalanceThis08", "BalanceThis09", "BalanceThis10",
                "BalanceThis11", "BalanceThis12", "BalanceThis13",
                # Balance fields - Last Year
                "BalanceLast01", "BalanceLast02", "BalanceLast03", "BalanceLast04", "BalanceLast05",
                "BalanceLast06", "BalanceLast07", "BalanceLast08", "BalanceLast09", "BalanceLast10",
                "BalanceLast11", "BalanceLast12", "BalanceLast13",
                # Sales fields - This Year
                "SalesThis01", "SalesThis02", "SalesThis03", "SalesThis04", "SalesThis05",
                "SalesThis06", "SalesThis07", "SalesThis08", "SalesThis09", "SalesThis10",
                "SalesThis11", "SalesThis12", "SalesThis13",
                # Sales fields - Last Year
                "SalesLast01", "SalesLast02", "SalesLast03", "SalesLast04", "SalesLast05",
                "SalesLast06", "SalesLast07", "SalesLast08", "SalesLast09", "SalesLast10",
                "SalesLast11", "SalesLast12", "SalesLast13",
                # Address fields
                "PostAddress01", "PostAddress02", "PostAddress03", "PostAddress04", "PostAddress05",
                # Financial fields
                "TaxCode", "ExemptRef", "SettlementTerms", "PaymentTerms", "Discount",
                "LastCrDate", "LastCrAmount", "Blocked", "OpenItem", "OverRideTax",
                "MonthOrDay", "CountryCode", "CurrencyCode", "CreditLimit", "InterestAfter",
                "PriceRegime",
                # Currency Balance fields - This Year
                "CurrBalanceThis01", "CurrBalanceThis02", "CurrBalanceThis03", "CurrBalanceThis04",
                "CurrBalanceThis05", "CurrBalanceThis06", "CurrBalanceThis07", "CurrBalanceThis08",
                "CurrBalanceThis09", "CurrBalanceThis10", "CurrBalanceThis11", "CurrBalanceThis12",
                "CurrBalanceThis13",
                # Currency Balance fields - Last Year
                "CurrBalanceLast01", "CurrBalanceLast02", "CurrBalanceLast03", "CurrBalanceLast04",
                "CurrBalanceLast05", "CurrBalanceLast06", "CurrBalanceLast07", "CurrBalanceLast08",
                "CurrBalanceLast09", "CurrBalanceLast10", "CurrBalanceLast11", "CurrBalanceLast12",
                "CurrBalanceLast13",
                # User defined fields
                "UserDefined01", "UserDefined02", "UserDefined03", "UserDefined04", "UserDefined05",
                # Ageing fields
                "Ageing01", "Ageing02", "Ageing03", "Ageing04", "Ageing05",
                # Other fields
                "InterestPer", "Freight01", "Ship", "UpdatedOn", "CashAccount", "CreateDate",
                "CustName", "CustSurname", "CustID",
                # Bank details
                "BankName", "BankType", "BankBranch", "BankAccNumber", "BankAccRelation",
                # Additional IDs
                "GUID", "ThirdPartyID", "PassportNumber"
            ]
            
            # Build query - single line to avoid ODBC truncation issues
            field_list = ", ".join(fields)
            query = f"SELECT TOP {limit + 1} {field_list} FROM CustomerMaster WHERE 1=1"
            params = []
            
            # Add filters
            if customer_code:
                query += " AND CustomerCode = ?"
                params.append(customer_code)
            
            if category is not None:
                query += " AND Category = ?"
                params.append(category)
            
            # Add cursor for pagination
            if cursor:
                decoded_cursor = base64.b64decode(cursor).decode('utf-8')
                query += " AND CustomerCode > ?"
                params.append(decoded_cursor)
            
            query += " ORDER BY CustomerCode"
            
            logger.debug(f"Executing query with {len(params)} parameters")
            cursor_obj.execute(query, params)
            
            customers = []
            rows = cursor_obj.fetchall()
            
            # Process up to limit rows
            for i, row in enumerate(rows[:limit]):
                customer_data = {}
                for j, field in enumerate(fields):
                    # Convert field name to snake_case for the model
                    # Fixed: Add underscore before numbers
                    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                    s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                    snake_case_field = s3.lower()
                    value = row[j]
                    
                    # Handle date conversions
                    if field in ['LastCrDate', 'UpdatedOn', 'CreateDate'] and value:
                        if isinstance(value, str):
                            try:
                                # Parse date string
                                if '/' in value:
                                    customer_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y').date()
                                else:
                                    customer_data[snake_case_field] = datetime.fromisoformat(value).date()
                            except:
                                customer_data[snake_case_field] = None
                        else:
                            customer_data[snake_case_field] = value
                    else:
                        customer_data[snake_case_field] = value
                
                customers.append(CustomerMaster(**customer_data))
            
            # Determine if there are more results
            has_more = len(rows) > limit
            next_cursor = None
            if has_more and customers:
                # Use the last customer code as the cursor
                next_cursor = base64.b64encode(customers[-1].customer_code.encode('utf-8')).decode('utf-8')
            
            logger.info(f"Retrieved {len(customers)} customers")
            
            # Build response
            metadata = PaginationMetadata(
                page_size=limit,
                cursor=cursor,
                next_cursor=next_cursor,
                has_more=has_more,
                timestamp=datetime.now()
            )
            
            return CustomerMasterResponse(data=customers, metadata=metadata)
            
    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        logger.error(f"Query parameters: cursor={cursor}, limit={limit}, customer_code={customer_code}, category={category}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch customers: {str(e)}")

@router.get("/customers/{customer_code}", response_model=CustomerMaster)
async def get_customer(customer_code: str):
    """Get a single customer by code with all fields"""
    logger.info(f"Customer detail request: customer_code={customer_code}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all fields
            fields = [
                "Category", "CustomerCode", "CustomerDesc",
                # Balance fields - This Year
                "BalanceThis01", "BalanceThis02", "BalanceThis03", "BalanceThis04", "BalanceThis05",
                "BalanceThis06", "BalanceThis07", "BalanceThis08", "BalanceThis09", "BalanceThis10",
                "BalanceThis11", "BalanceThis12", "BalanceThis13",
                # Balance fields - Last Year
                "BalanceLast01", "BalanceLast02", "BalanceLast03", "BalanceLast04", "BalanceLast05",
                "BalanceLast06", "BalanceLast07", "BalanceLast08", "BalanceLast09", "BalanceLast10",
                "BalanceLast11", "BalanceLast12", "BalanceLast13",
                # Sales fields - This Year
                "SalesThis01", "SalesThis02", "SalesThis03", "SalesThis04", "SalesThis05",
                "SalesThis06", "SalesThis07", "SalesThis08", "SalesThis09", "SalesThis10",
                "SalesThis11", "SalesThis12", "SalesThis13",
                # Sales fields - Last Year
                "SalesLast01", "SalesLast02", "SalesLast03", "SalesLast04", "SalesLast05",
                "SalesLast06", "SalesLast07", "SalesLast08", "SalesLast09", "SalesLast10",
                "SalesLast11", "SalesLast12", "SalesLast13",
                # Address fields
                "PostAddress01", "PostAddress02", "PostAddress03", "PostAddress04", "PostAddress05",
                # Financial fields
                "TaxCode", "ExemptRef", "SettlementTerms", "PaymentTerms", "Discount",
                "LastCrDate", "LastCrAmount", "Blocked", "OpenItem", "OverRideTax",
                "MonthOrDay", "CountryCode", "CurrencyCode", "CreditLimit", "InterestAfter",
                "PriceRegime",
                # Currency Balance fields - This Year
                "CurrBalanceThis01", "CurrBalanceThis02", "CurrBalanceThis03", "CurrBalanceThis04",
                "CurrBalanceThis05", "CurrBalanceThis06", "CurrBalanceThis07", "CurrBalanceThis08",
                "CurrBalanceThis09", "CurrBalanceThis10", "CurrBalanceThis11", "CurrBalanceThis12",
                "CurrBalanceThis13",
                # Currency Balance fields - Last Year
                "CurrBalanceLast01", "CurrBalanceLast02", "CurrBalanceLast03", "CurrBalanceLast04",
                "CurrBalanceLast05", "CurrBalanceLast06", "CurrBalanceLast07", "CurrBalanceLast08",
                "CurrBalanceLast09", "CurrBalanceLast10", "CurrBalanceLast11", "CurrBalanceLast12",
                "CurrBalanceLast13",
                # User defined fields
                "UserDefined01", "UserDefined02", "UserDefined03", "UserDefined04", "UserDefined05",
                # Ageing fields
                "Ageing01", "Ageing02", "Ageing03", "Ageing04", "Ageing05",
                # Other fields
                "InterestPer", "Freight01", "Ship", "UpdatedOn", "CashAccount", "CreateDate",
                "CustName", "CustSurname", "CustID",
                # Bank details
                "BankName", "BankType", "BankBranch", "BankAccNumber", "BankAccRelation",
                # Additional IDs
                "GUID", "ThirdPartyID", "PassportNumber"
            ]
            
            # Single line query to avoid ODBC truncation
            field_list = ", ".join(fields)
            query = f"SELECT {field_list} FROM CustomerMaster WHERE CustomerCode = ?"
            
            cursor.execute(query, [customer_code])
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Customer {customer_code} not found")
            
            # Build customer object
            customer_data = {}
            for j, field in enumerate(fields):
                # Fixed: Add underscore before numbers
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                snake_case_field = s3.lower()
                value = row[j]
                
                # Handle date conversions
                if field in ['LastCrDate', 'UpdatedOn', 'CreateDate'] and value:
                    if isinstance(value, str):
                        try:
                            if '/' in value:
                                customer_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y').date()
                            else:
                                customer_data[snake_case_field] = datetime.fromisoformat(value).date()
                        except:
                            customer_data[snake_case_field] = None
                    else:
                        customer_data[snake_case_field] = value
                else:
                    customer_data[snake_case_field] = value
            
            customer = CustomerMaster(**customer_data)
            logger.info(f"Retrieved customer: {customer_code}")
            
            return customer
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer {customer_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch customer: {str(e)}") 