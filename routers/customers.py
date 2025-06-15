from fastapi import APIRouter, HTTPException, Query
from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from database import db_pool
from config import settings
import logging

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

@router.get("/customers", response_model=List[Customer])
async def get_customers(
    search: Optional[str] = Query(None, description="Search term for customer name or code"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size)
):
    """Get a list of customers"""
    logger.info(f"Customer request: search={search}, limit={limit}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Base query for customers
            query = f"""
                SELECT TOP {limit}
                    CustomerCode,
                    CustomerDescription,
                    ContactName,
                    Email,
                    Telephone
                FROM CustomerMaster WITH (NOLOCK)
                WHERE 1=1
            """
            params = []
            
            if search:
                query += " AND (CustomerCode LIKE ? OR CustomerDescription LIKE ?)"
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern])
                
            query += " ORDER BY CustomerCode"
            
            logger.debug(f"Executing query: {query}")
            logger.debug(f"Parameters: {params}")
            
            cursor.execute(query, params)
            
            customers = []
            row_count = 0
            for row in cursor.fetchall():
                row_count += 1
                customers.append(Customer(
                    customer_code=row.CustomerCode,
                    customer_name=row.CustomerDescription,
                    contact_name=row.ContactName if hasattr(row, 'ContactName') else None,
                    email=row.Email if hasattr(row, 'Email') else None,
                    phone=row.Telephone if hasattr(row, 'Telephone') else None
                ))
            
            logger.info(f"Retrieved {row_count} customers")
            
            return customers
            
    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        logger.error(f"Query parameters: search={search}, limit={limit}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch customers: {str(e)}")

@router.get("/customers/{customer_code}", response_model=Customer)
async def get_customer(customer_code: str):
    """Get a single customer by code"""
    logger.info(f"Customer detail request: customer_code={customer_code}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    CustomerCode,
                    CustomerDescription,
                    ContactName,
                    Email,
                    Telephone
                FROM CustomerMaster WITH (NOLOCK)
                WHERE CustomerCode = ?
            """
            
            cursor.execute(query, [customer_code])
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Customer {customer_code} not found")
            
            customer = Customer(
                customer_code=row.CustomerCode,
                customer_name=row.CustomerDescription,
                contact_name=row.ContactName if hasattr(row, 'ContactName') else None,
                email=row.Email if hasattr(row, 'Email') else None,
                phone=row.Telephone if hasattr(row, 'Telephone') else None
            )
            
            logger.info(f"Retrieved customer: {customer_code}")
            
            return customer
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer {customer_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch customer: {str(e)}") 