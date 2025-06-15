from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import db_pool
from config import settings
import logging
from models import DeliveryAddress, DeliveryAddressResponse, PaginationMetadata
from datetime import datetime
import base64
import re

# Define the router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/delivery-addresses", response_model=DeliveryAddressResponse)
async def get_delivery_addresses(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    customer_code: Optional[str] = Query(None, description="Filter by customer code"),
    cust_deliv_code: Optional[str] = Query(None, description="Filter by delivery code")
):
    """Get a paginated list of delivery addresses"""
    logger.info(f"Delivery address request: cursor={cursor}, limit={limit}, customer_code={customer_code}, cust_deliv_code={cust_deliv_code}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor_obj = conn.cursor()
            
            # Build the field list
            fields = [
                "CustomerCode", "CustDelivCode", "SalesmanCode",
                "Contact", "Telephone", "Cell", "Fax",
                "DelAddress01", "DelAddress02", "DelAddress03", "DelAddress04", "DelAddress05",
                "Email", "ContactDocs", "EmailDocs", "ContactStatement", "EmailStatement"
            ]
            
            # Build query - single line to avoid ODBC truncation issues
            field_list = ", ".join(fields)
            query = f"SELECT TOP {limit + 1} {field_list} FROM DeliveryAddresses WHERE 1=1"
            params = []
            
            # Add filters
            if customer_code:
                query += " AND CustomerCode = ?"
                params.append(customer_code)
            
            if cust_deliv_code:
                query += " AND CustDelivCode = ?"
                params.append(cust_deliv_code)
            
            # Add cursor for pagination
            if cursor:
                decoded_cursor = base64.b64decode(cursor).decode('utf-8')
                # Decode as CustomerCode:CustDelivCode
                parts = decoded_cursor.split(':', 1)
                if len(parts) == 2:
                    query += " AND (CustomerCode > ? OR (CustomerCode = ? AND CustDelivCode > ?))"
                    params.extend([parts[0], parts[0], parts[1]])
            
            query += " ORDER BY CustomerCode, CustDelivCode"
            
            logger.debug(f"Executing query with {len(params)} parameters")
            cursor_obj.execute(query, params)
            
            delivery_addresses = []
            rows = cursor_obj.fetchall()
            
            # Process up to limit rows
            for i, row in enumerate(rows[:limit]):
                address_data = {}
                for j, field in enumerate(fields):
                    # Convert field name to snake_case for the model
                    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                    s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                    snake_case_field = s3.lower()
                    value = row[j]
                    
                    # Trim string values
                    if isinstance(value, str):
                        address_data[snake_case_field] = value.strip()
                    else:
                        address_data[snake_case_field] = value
                
                delivery_addresses.append(DeliveryAddress(**address_data))
            
            # Determine if there are more results
            has_more = len(rows) > limit
            next_cursor = None
            if has_more and delivery_addresses:
                # Use composite cursor: CustomerCode:CustDelivCode
                last_addr = delivery_addresses[-1]
                cursor_value = f"{last_addr.customer_code}:{last_addr.cust_deliv_code}"
                next_cursor = base64.b64encode(cursor_value.encode('utf-8')).decode('utf-8')
            
            logger.info(f"Retrieved {len(delivery_addresses)} delivery addresses")
            
            # Build response
            metadata = PaginationMetadata(
                page_size=limit,
                cursor=cursor,
                next_cursor=next_cursor,
                has_more=has_more,
                timestamp=datetime.now()
            )
            
            return DeliveryAddressResponse(data=delivery_addresses, metadata=metadata)
            
    except Exception as e:
        logger.error(f"Error fetching delivery addresses: {e}")
        logger.error(f"Query parameters: cursor={cursor}, limit={limit}, customer_code={customer_code}, cust_deliv_code={cust_deliv_code}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch delivery addresses: {str(e)}")

@router.get("/delivery-addresses/{customer_code}/{cust_deliv_code}", response_model=DeliveryAddress)
async def get_delivery_address(customer_code: str, cust_deliv_code: str):
    """Get a single delivery address by customer code and delivery code"""
    logger.info(f"Delivery address detail request: customer_code={customer_code}, cust_deliv_code={cust_deliv_code}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all fields
            fields = [
                "CustomerCode", "CustDelivCode", "SalesmanCode",
                "Contact", "Telephone", "Cell", "Fax",
                "DelAddress01", "DelAddress02", "DelAddress03", "DelAddress04", "DelAddress05",
                "Email", "ContactDocs", "EmailDocs", "ContactStatement", "EmailStatement"
            ]
            
            # Single line query to avoid ODBC truncation
            field_list = ", ".join(fields)
            query = f"SELECT {field_list} FROM DeliveryAddresses WHERE CustomerCode = ? AND CustDelivCode = ?"
            
            cursor.execute(query, [customer_code, cust_deliv_code])
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Delivery address not found for customer {customer_code} with code {cust_deliv_code}")
            
            # Build delivery address object
            address_data = {}
            for j, field in enumerate(fields):
                # Convert field name to snake_case
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                snake_case_field = s3.lower()
                value = row[j]
                
                # Trim string values
                if isinstance(value, str):
                    address_data[snake_case_field] = value.strip()
                else:
                    address_data[snake_case_field] = value
            
            delivery_address = DeliveryAddress(**address_data)
            logger.info(f"Retrieved delivery address: {customer_code}/{cust_deliv_code}")
            
            return delivery_address
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching delivery address {customer_code}/{cust_deliv_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch delivery address: {str(e)}")

@router.get("/customers/{customer_code}/delivery-addresses", response_model=DeliveryAddressResponse)
async def get_customer_delivery_addresses(
    customer_code: str,
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size)
):
    """Get all delivery addresses for a specific customer"""
    logger.info(f"Customer delivery addresses request: customer_code={customer_code}, cursor={cursor}, limit={limit}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor_obj = conn.cursor()
            
            # Build the field list
            fields = [
                "CustomerCode", "CustDelivCode", "SalesmanCode",
                "Contact", "Telephone", "Cell", "Fax",
                "DelAddress01", "DelAddress02", "DelAddress03", "DelAddress04", "DelAddress05",
                "Email", "ContactDocs", "EmailDocs", "ContactStatement", "EmailStatement"
            ]
            
            # Build query
            field_list = ", ".join(fields)
            query = f"SELECT TOP {limit + 1} {field_list} FROM DeliveryAddresses WHERE CustomerCode = ?"
            params = [customer_code]
            
            # Add cursor for pagination
            if cursor:
                decoded_cursor = base64.b64decode(cursor).decode('utf-8')
                query += " AND CustDelivCode > ?"
                params.append(decoded_cursor)
            
            query += " ORDER BY CustDelivCode"
            
            logger.debug(f"Executing query with {len(params)} parameters")
            cursor_obj.execute(query, params)
            
            delivery_addresses = []
            rows = cursor_obj.fetchall()
            
            # Process up to limit rows
            for i, row in enumerate(rows[:limit]):
                address_data = {}
                for j, field in enumerate(fields):
                    # Convert field name to snake_case
                    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                    s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                    snake_case_field = s3.lower()
                    value = row[j]
                    
                    # Trim string values
                    if isinstance(value, str):
                        address_data[snake_case_field] = value.strip()
                    else:
                        address_data[snake_case_field] = value
                
                delivery_addresses.append(DeliveryAddress(**address_data))
            
            # Determine if there are more results
            has_more = len(rows) > limit
            next_cursor = None
            if has_more and delivery_addresses:
                # Use CustDelivCode as cursor
                next_cursor = base64.b64encode(delivery_addresses[-1].cust_deliv_code.encode('utf-8')).decode('utf-8')
            
            logger.info(f"Retrieved {len(delivery_addresses)} delivery addresses for customer {customer_code}")
            
            # Build response
            metadata = PaginationMetadata(
                page_size=limit,
                cursor=cursor,
                next_cursor=next_cursor,
                has_more=has_more,
                timestamp=datetime.now()
            )
            
            return DeliveryAddressResponse(data=delivery_addresses, metadata=metadata)
            
    except Exception as e:
        logger.error(f"Error fetching delivery addresses for customer {customer_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch delivery addresses: {str(e)}") 