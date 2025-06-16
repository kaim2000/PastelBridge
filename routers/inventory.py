from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import db_pool
from config import settings
import logging
from models import Inventory, InventoryResponse, PaginationMetadata
from datetime import datetime
import base64
import re

# Define the router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/inventory", response_model=InventoryResponse)
async def get_inventory(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    item_code: Optional[str] = Query(None, description="Filter by item code"),
    category: Optional[str] = Query(None, description="Filter by category"),
    blocked: Optional[int] = Query(None, description="Filter by blocked status (0=not blocked, 1=blocked)"),
    physical: Optional[int] = Query(None, description="Filter by physical status (0=non-physical, 1=physical)")
):
    """Get a paginated list of inventory items"""
    logger.info(f"Inventory request: cursor={cursor}, limit={limit}, item_code={item_code}, category={category}, blocked={blocked}, physical={physical}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor_obj = conn.cursor()
            
            # Build the field list - MUST match exact database column names
            fields = [
                "Category", "ItemCode", "Description", "Barcode",
                "DiscountType", "Blocked", "Fixed", "ShowQty",
                "Physical", "UnitSize", "SalesTaxType", "PurchTaxType",
                "GLCode", "AllowTax", "LinkWeb", "SalesCommision",
                "SerialItem", "Picture", "UserDefText01", "UserDefText02",
                "UserDefText03", "UserDefNum01", "UserDefNum02", "UserDefNum03",
                "CommodityCode", "NettMass", "UpdatedOn", "GUID"
            ]
            
            # Build query - single line to avoid ODBC truncation issues
            field_list = ", ".join(fields)
            query = f"SELECT TOP {limit + 1} {field_list} FROM Inventory WHERE 1=1"
            params = []
            
            # Add filters
            if item_code:
                query += " AND ItemCode = ?"
                params.append(item_code)
            
            if category:
                query += " AND Category = ?"
                params.append(category)
            
            if blocked is not None:
                query += " AND Blocked = ?"
                params.append(blocked)
            
            if physical is not None:
                query += " AND Physical = ?"
                params.append(physical)
            
            # Add cursor for pagination
            if cursor:
                decoded_cursor = base64.b64decode(cursor).decode('utf-8')
                query += " AND ItemCode > ?"
                params.append(decoded_cursor)
            
            # Order by primary key
            query += " ORDER BY ItemCode"
            
            logger.debug(f"Executing query with {len(params)} parameters")
            cursor_obj.execute(query, params)
            
            items = []
            rows = cursor_obj.fetchall()
            
            # Process up to limit rows
            for i, row in enumerate(rows[:limit]):
                item_data = {}
                for j, field in enumerate(fields):
                    # Convert field name to snake_case for the model
                    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                    s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                    snake_case_field = s3.lower()
                    value = row[j]
                    
                    # Handle different data types
                    if field == 'UpdatedOn' and value:
                        # DateTime field handling
                        if isinstance(value, str):
                            try:
                                if '/' in value:
                                    # Handle format like "14/05/2025 12:26:28"
                                    item_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y %H:%M:%S')
                                else:
                                    item_data[snake_case_field] = datetime.fromisoformat(value)
                            except:
                                item_data[snake_case_field] = None
                        else:
                            item_data[snake_case_field] = value
                    elif isinstance(value, str):
                        # Trim string values
                        item_data[snake_case_field] = value.strip()
                    else:
                        item_data[snake_case_field] = value
                
                items.append(Inventory(**item_data))
            
            # Determine if there are more results
            has_more = len(rows) > limit
            next_cursor = None
            if has_more and items:
                next_cursor = base64.b64encode(items[-1].item_code.encode('utf-8')).decode('utf-8')
            
            logger.info(f"Retrieved {len(items)} inventory items")
            
            # Build response
            metadata = PaginationMetadata(
                page_size=limit,
                cursor=cursor,
                next_cursor=next_cursor,
                has_more=has_more,
                timestamp=datetime.now()
            )
            
            return InventoryResponse(data=items, metadata=metadata)
            
    except Exception as e:
        logger.error(f"Error fetching inventory: {e}")
        logger.error(f"Query parameters: cursor={cursor}, limit={limit}, item_code={item_code}, category={category}, blocked={blocked}, physical={physical}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory: {str(e)}")

# Single record endpoint
@router.get("/inventory/{item_code}", response_model=Inventory)
async def get_inventory_item(item_code: str):
    """Get a single inventory item by item code"""
    logger.info(f"Inventory detail request: item_code={item_code}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all fields
            fields = [
                "Category", "ItemCode", "Description", "Barcode",
                "DiscountType", "Blocked", "Fixed", "ShowQty",
                "Physical", "UnitSize", "SalesTaxType", "PurchTaxType",
                "GLCode", "AllowTax", "LinkWeb", "SalesCommision",
                "SerialItem", "Picture", "UserDefText01", "UserDefText02",
                "UserDefText03", "UserDefNum01", "UserDefNum02", "UserDefNum03",
                "CommodityCode", "NettMass", "UpdatedOn", "GUID"
            ]
            
            # Single line query to avoid ODBC truncation
            field_list = ", ".join(fields)
            query = f"SELECT {field_list} FROM Inventory WHERE ItemCode = ?"
            
            cursor.execute(query, [item_code])
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Inventory item not found: {item_code}")
            
            # Build inventory object
            item_data = {}
            for j, field in enumerate(fields):
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                snake_case_field = s3.lower()
                value = row[j]
                
                # Handle data types
                if field == 'UpdatedOn' and value:
                    if isinstance(value, str):
                        try:
                            if '/' in value:
                                item_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y %H:%M:%S')
                            else:
                                item_data[snake_case_field] = datetime.fromisoformat(value)
                        except:
                            item_data[snake_case_field] = None
                    else:
                        item_data[snake_case_field] = value
                elif isinstance(value, str):
                    item_data[snake_case_field] = value.strip()
                else:
                    item_data[snake_case_field] = value
            
            item = Inventory(**item_data)
            logger.info(f"Retrieved inventory item: {item_code}")
            
            return item
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching inventory item {item_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory item: {str(e)}") 