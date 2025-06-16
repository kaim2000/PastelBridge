from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import db_pool
from config import settings
import logging
from models import InventoryCategory, InventoryCategoryResponse, PaginationMetadata
from datetime import datetime
import base64
import re

# Define the router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/inventory-categories", response_model=InventoryCategoryResponse)
async def get_inventory_categories(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    ic_code: Optional[str] = Query(None, description="Filter by category code")
):
    """Get a paginated list of inventory categories"""
    logger.info(f"Inventory category request: cursor={cursor}, limit={limit}, ic_code={ic_code}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor_obj = conn.cursor()
            
            # Build the field list - MUST match exact database column names
            fields = ["ICCode", "ICDesc"]
            
            # Build query - single line to avoid ODBC truncation issues
            field_list = ", ".join(fields)
            query = f"SELECT TOP {limit + 1} {field_list} FROM InventoryCategory WHERE 1=1"
            params = []
            
            # Add filters
            if ic_code:
                query += " AND ICCode = ?"
                params.append(ic_code)
            
            # Add cursor for pagination
            if cursor:
                decoded_cursor = base64.b64decode(cursor).decode('utf-8')
                query += " AND ICCode > ?"
                params.append(decoded_cursor)
            
            # Order by primary key
            query += " ORDER BY ICCode"
            
            logger.debug(f"Executing query with {len(params)} parameters")
            cursor_obj.execute(query, params)
            
            categories = []
            rows = cursor_obj.fetchall()
            
            # Process up to limit rows
            for i, row in enumerate(rows[:limit]):
                category_data = {}
                for j, field in enumerate(fields):
                    # Convert field name to snake_case for the model
                    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                    s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                    snake_case_field = s3.lower()
                    value = row[j]
                    
                    # Handle string values
                    if isinstance(value, str):
                        category_data[snake_case_field] = value.strip()
                    else:
                        category_data[snake_case_field] = value
                
                categories.append(InventoryCategory(**category_data))
            
            # Determine if there are more results
            has_more = len(rows) > limit
            next_cursor = None
            if has_more and categories:
                next_cursor = base64.b64encode(categories[-1].ic_code.encode('utf-8')).decode('utf-8')
            
            logger.info(f"Retrieved {len(categories)} inventory categories")
            
            # Build response
            metadata = PaginationMetadata(
                page_size=limit,
                cursor=cursor,
                next_cursor=next_cursor,
                has_more=has_more,
                timestamp=datetime.now()
            )
            
            return InventoryCategoryResponse(data=categories, metadata=metadata)
            
    except Exception as e:
        logger.error(f"Error fetching inventory categories: {e}")
        logger.error(f"Query parameters: cursor={cursor}, limit={limit}, ic_code={ic_code}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory categories: {str(e)}")

# Single record endpoint
@router.get("/inventory-categories/{ic_code}", response_model=InventoryCategory)
async def get_inventory_category(ic_code: str):
    """Get a single inventory category by category code"""
    logger.info(f"Inventory category detail request: ic_code={ic_code}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all fields
            fields = ["ICCode", "ICDesc"]
            
            # Single line query to avoid ODBC truncation
            field_list = ", ".join(fields)
            query = f"SELECT {field_list} FROM InventoryCategory WHERE ICCode = ?"
            
            cursor.execute(query, [ic_code])
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Inventory category not found: {ic_code}")
            
            # Build category object
            category_data = {}
            for j, field in enumerate(fields):
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                snake_case_field = s3.lower()
                value = row[j]
                
                # Handle string values
                if isinstance(value, str):
                    category_data[snake_case_field] = value.strip()
                else:
                    category_data[snake_case_field] = value
            
            category = InventoryCategory(**category_data)
            logger.info(f"Retrieved inventory category: {ic_code}")
            
            return category
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching inventory category {ic_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory category: {str(e)}") 