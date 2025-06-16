from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import db_pool
from config import settings
import logging
from models import InventoryGroup, InventoryGroupResponse, PaginationMetadata
from datetime import datetime
import base64
import re

# Define the router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/inventory-groups", response_model=InventoryGroupResponse)
async def get_inventory_groups(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    inv_group: Optional[str] = Query(None, description="Filter by inventory group code")
):
    """Get a paginated list of inventory groups"""
    logger.info(f"Inventory groups request: cursor={cursor}, limit={limit}, inv_group={inv_group}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor_obj = conn.cursor()
            
            # Build the field list - MUST match exact database column names
            fields = [
                "InvGroup", "Description", "SalesAcc", "PurchAcc",
                "COSAcc", "Adjustment", "StockCtl", "Variance",
                "PurchVariance", "SalesTaxType", "PurchTaxType"
            ]
            
            # Build query - single line to avoid ODBC truncation issues
            field_list = ", ".join(fields)
            query = f"SELECT TOP {limit + 1} {field_list} FROM InventoryGroups WHERE 1=1"
            params = []
            
            # Add filters
            if inv_group:
                query += " AND InvGroup = ?"
                params.append(inv_group)
            
            # Add cursor for pagination
            if cursor:
                decoded_cursor = base64.b64decode(cursor).decode('utf-8')
                query += " AND InvGroup > ?"
                params.append(decoded_cursor)
            
            # Order by primary key
            query += " ORDER BY InvGroup"
            
            logger.debug(f"Executing query with {len(params)} parameters")
            cursor_obj.execute(query, params)
            
            groups = []
            rows = cursor_obj.fetchall()
            
            # Process up to limit rows
            for i, row in enumerate(rows[:limit]):
                group_data = {}
                for j, field in enumerate(fields):
                    # Convert field name to snake_case for the model
                    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                    s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                    snake_case_field = s3.lower()
                    value = row[j]
                    
                    # Handle string values
                    if isinstance(value, str):
                        group_data[snake_case_field] = value.strip()
                    else:
                        group_data[snake_case_field] = value
                
                groups.append(InventoryGroup(**group_data))
            
            # Determine if there are more results
            has_more = len(rows) > limit
            next_cursor = None
            if has_more and groups:
                next_cursor = base64.b64encode(groups[-1].inv_group.encode('utf-8')).decode('utf-8')
            
            logger.info(f"Retrieved {len(groups)} inventory groups")
            
            # Build response
            metadata = PaginationMetadata(
                page_size=limit,
                cursor=cursor,
                next_cursor=next_cursor,
                has_more=has_more,
                timestamp=datetime.now()
            )
            
            return InventoryGroupResponse(data=groups, metadata=metadata)
            
    except Exception as e:
        logger.error(f"Error fetching inventory groups: {e}")
        logger.error(f"Query parameters: cursor={cursor}, limit={limit}, inv_group={inv_group}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory groups: {str(e)}")

# Single record endpoint
@router.get("/inventory-groups/{inv_group}", response_model=InventoryGroup)
async def get_inventory_group(inv_group: str):
    """Get a single inventory group by group code"""
    logger.info(f"Inventory group detail request: inv_group={inv_group}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all fields
            fields = [
                "InvGroup", "Description", "SalesAcc", "PurchAcc",
                "COSAcc", "Adjustment", "StockCtl", "Variance",
                "PurchVariance", "SalesTaxType", "PurchTaxType"
            ]
            
            # Single line query to avoid ODBC truncation
            field_list = ", ".join(fields)
            query = f"SELECT {field_list} FROM InventoryGroups WHERE InvGroup = ?"
            
            cursor.execute(query, [inv_group])
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Inventory group not found: {inv_group}")
            
            # Build group object
            group_data = {}
            for j, field in enumerate(fields):
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                snake_case_field = s3.lower()
                value = row[j]
                
                # Handle string values
                if isinstance(value, str):
                    group_data[snake_case_field] = value.strip()
                else:
                    group_data[snake_case_field] = value
            
            group = InventoryGroup(**group_data)
            logger.info(f"Retrieved inventory group: {inv_group}")
            
            return group
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching inventory group {inv_group}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory group: {str(e)}") 