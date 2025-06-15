# API Endpoint Implementation Blueprint

This guide provides a step-by-step template for creating new API endpoints for tables in the Pastel Partner accounting system. Replace placeholders in `[BRACKETS]` with your specific values.

## Prerequisites
- Working PastelBridge API setup
- Access to the database table structure
- List of fields from the target table

## Step 1: Analyze the Table Structure

First, identify your table details:
- Table name: `[TABLE_NAME]` (e.g., `DeliveryAddresses`)
- Primary key field(s): `[PRIMARY_KEY]` (e.g., `CustomerCode, CustDelivCode`)
- All field names from the table

## Step 2: Create the Pydantic Model

Edit `models.py` and add your model after the existing models:

```python
# [TABLE_NAME] models
class [ModelName](BaseModel):
    # Primary key fields (required)
    [primary_key_field_1]: str
    [primary_key_field_2]: str  # if composite key
    
    # Other fields (all optional unless you know they're required)
    [field_name_1]: Optional[str] = None
    [field_name_2]: Optional[str] = None
    [field_name_3]: Optional[int] = None
    [field_name_4]: Optional[float] = None
    [field_name_5]: Optional[date] = None  # for date fields
    [field_name_6]: Optional[datetime] = None  # for datetime fields
    # ... add all fields from your table
    
    class Config:
        from_attributes = True

class [ModelName]Response(BaseModel):
    data: List[[ModelName]]
    metadata: PaginationMetadata

class [ModelName]Query(BaseModel):
    cursor: Optional[str] = None
    limit: int = 50  # Default to 50, max will be enforced in endpoint
    [filter_field_1]: Optional[str] = None  # Add common filter fields
    [filter_field_2]: Optional[int] = None
```

### Field Type Mapping Guide:
- String/char fields → `Optional[str]`
- Integer fields → `Optional[int]`
- Decimal/money fields → `Optional[float]`
- Date fields → `Optional[date]`
- DateTime fields → `Optional[datetime]`
- Boolean fields → `Optional[bool]`

## Step 3: Create the Router File

Create `routers/[table_name_plural].py`:

```python
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import db_pool
from config import settings
import logging
from models import [ModelName], [ModelName]Response, PaginationMetadata
from datetime import datetime
import base64
import re

# Define the router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/[route-name-plural]", response_model=[ModelName]Response)
async def get_[table_name_plural](
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    [filter_field_1]: Optional[str] = Query(None, description="Filter by [field description]"),
    [filter_field_2]: Optional[int] = Query(None, description="Filter by [field description]")
):
    """Get a paginated list of [table description]"""
    logger.info(f"[Table name] request: cursor={cursor}, limit={limit}, [filter_field_1]={[filter_field_1]}, [filter_field_2]={[filter_field_2]}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor_obj = conn.cursor()
            
            # Build the field list - MUST match exact database column names
            fields = [
                "[DatabaseField1]", "[DatabaseField2]", "[DatabaseField3]",
                # List ALL fields from your table in their exact database names
                # e.g., "CustomerCode", "CustDelivCode", "SalesmanCode"
            ]
            
            # Build query - single line to avoid ODBC truncation issues
            field_list = ", ".join(fields)
            query = f"SELECT TOP {limit + 1} {field_list} FROM [TABLE_NAME] WHERE 1=1"
            params = []
            
            # Add filters
            if [filter_field_1]:
                query += " AND [DatabaseFieldName1] = ?"
                params.append([filter_field_1])
            
            if [filter_field_2] is not None:
                query += " AND [DatabaseFieldName2] = ?"
                params.append([filter_field_2])
            
            # Add cursor for pagination
            if cursor:
                decoded_cursor = base64.b64decode(cursor).decode('utf-8')
                
                # For single primary key:
                query += " AND [PrimaryKeyField] > ?"
                params.append(decoded_cursor)
                
                # For composite primary key (uncomment and modify):
                # parts = decoded_cursor.split(':', 1)
                # if len(parts) == 2:
                #     query += " AND ([KeyField1] > ? OR ([KeyField1] = ? AND [KeyField2] > ?))"
                #     params.extend([parts[0], parts[0], parts[1]])
            
            # Order by primary key(s)
            query += " ORDER BY [PrimaryKeyField]"
            # For composite: query += " ORDER BY [KeyField1], [KeyField2]"
            
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
                    if field in ['[DateField1]', '[DateField2]'] and value:
                        # Date field handling
                        if isinstance(value, str):
                            try:
                                if '/' in value:
                                    item_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y').date()
                                else:
                                    item_data[snake_case_field] = datetime.fromisoformat(value).date()
                            except:
                                item_data[snake_case_field] = None
                        else:
                            item_data[snake_case_field] = value
                    elif isinstance(value, str):
                        # Trim string values
                        item_data[snake_case_field] = value.strip()
                    else:
                        item_data[snake_case_field] = value
                
                items.append([ModelName](**item_data))
            
            # Determine if there are more results
            has_more = len(rows) > limit
            next_cursor = None
            if has_more and items:
                # For single primary key:
                next_cursor = base64.b64encode(items[-1].[primary_key_field].encode('utf-8')).decode('utf-8')
                
                # For composite primary key (uncomment and modify):
                # last_item = items[-1]
                # cursor_value = f"{last_item.[key_field_1]}:{last_item.[key_field_2]}"
                # next_cursor = base64.b64encode(cursor_value.encode('utf-8')).decode('utf-8')
            
            logger.info(f"Retrieved {len(items)} [table name]")
            
            # Build response
            metadata = PaginationMetadata(
                page_size=limit,
                cursor=cursor,
                next_cursor=next_cursor,
                has_more=has_more,
                timestamp=datetime.now()
            )
            
            return [ModelName]Response(data=items, metadata=metadata)
            
    except Exception as e:
        logger.error(f"Error fetching [table name]: {e}")
        logger.error(f"Query parameters: cursor={cursor}, limit={limit}, [filter_field_1]={[filter_field_1]}, [filter_field_2]={[filter_field_2]}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch [table name]: {str(e)}")

# Single record endpoint
@router.get("/[route-name-plural]/{[primary_key_param]}", response_model=[ModelName])
async def get_[table_name_singular](
    [primary_key_param]: str
    # Add more path parameters for composite keys
):
    """Get a single [table name] by [primary key description]"""
    logger.info(f"[Table name] detail request: [primary_key_param]={[primary_key_param]}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all fields
            fields = [
                "[DatabaseField1]", "[DatabaseField2]", "[DatabaseField3]",
                # Same field list as above
            ]
            
            # Single line query to avoid ODBC truncation
            field_list = ", ".join(fields)
            query = f"SELECT {field_list} FROM [TABLE_NAME] WHERE [PrimaryKeyField] = ?"
            # For composite: WHERE [KeyField1] = ? AND [KeyField2] = ?
            
            cursor.execute(query, [[primary_key_param]])
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"[Table name] not found: {[primary_key_param]}")
            
            # Build object
            item_data = {}
            for j, field in enumerate(fields):
                # Same field processing as above
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                snake_case_field = s3.lower()
                value = row[j]
                
                # Handle data types (same as above)
                if field in ['[DateField1]', '[DateField2]'] and value:
                    if isinstance(value, str):
                        try:
                            if '/' in value:
                                item_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y').date()
                            else:
                                item_data[snake_case_field] = datetime.fromisoformat(value).date()
                        except:
                            item_data[snake_case_field] = None
                    else:
                        item_data[snake_case_field] = value
                elif isinstance(value, str):
                    item_data[snake_case_field] = value.strip()
                else:
                    item_data[snake_case_field] = value
            
            item = [ModelName](**item_data)
            logger.info(f"Retrieved [table name]: {[primary_key_param]}")
            
            return item
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching [table name] {[primary_key_param]}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch [table name]: {str(e)}")
```

## Step 4: Register the Router

In `main.py`, add the import and registration:

1. Add to imports section:
```python
from routers import health, invoices, customers, delivery_addresses, [table_name_plural]
```

2. Add router registration (keep alphabetical order):
```python
app.include_router([table_name_plural].router, prefix="/api", tags=["[table-name-plural]"])
```

## Step 5: Common Patterns and Gotchas

### 1. Field Name Conversion
The code automatically converts database field names from PascalCase to snake_case:
- `CustomerCode` → `customer_code`
- `DelAddress01` → `del_address_01`
- `SalesThis01` → `sales_this_01`

### 2. Date Field Handling
Always list your date fields in the date handling section:
```python
if field in ['LastCrDate', 'UpdatedOn', 'CreateDate'] and value:
```

### 3. Composite Primary Keys
For tables with composite keys (like DeliveryAddresses), you need:
- Composite cursor encoding: `"key1:key2"`
- Special WHERE clause for pagination
- Multiple path parameters for single record endpoint

### 4. ODBC Query Formatting
**CRITICAL**: Always build queries on a single line to avoid ODBC truncation:
```python
# GOOD
query = f"SELECT {field_list} FROM TableName WHERE 1=1"

# BAD - Will cause syntax errors
query = f"""
    SELECT {field_list} 
    FROM TableName 
    WHERE 1=1
"""
```

### 5. Optional vs Required Fields
- Primary keys: Always required (no `Optional`)
- All other fields: Make optional unless you're certain they're always populated
- Use appropriate default: `= None` for optional fields

### 6. String Field Trimming
All string fields are automatically trimmed:
```python
if isinstance(value, str):
    item_data[snake_case_field] = value.strip()
```

## Step 6: Testing Checklist

After implementation, test these scenarios:

1. **List endpoint without filters**:
   ```
   GET /api/[route-name-plural]
   ```

2. **List endpoint with pagination**:
   ```
   GET /api/[route-name-plural]?limit=10
   GET /api/[route-name-plural]?cursor=[next_cursor_value]
   ```

3. **List endpoint with filters**:
   ```
   GET /api/[route-name-plural]?[filter_field]=value
   ```

4. **Single record endpoint**:
   ```
   GET /api/[route-name-plural]/[primary_key_value]
   ```

5. **Error cases**:
   - Invalid primary key (should return 404)
   - Missing API key (should return 401)
   - Rate limiting (rapid requests)

## Step 7: Documentation Template

Create `docs/[table-name]-api.md` using the delivery-addresses-api.md as a template:

1. Replace endpoint names
2. Update field descriptions
3. Adjust examples with real data
4. Update filter parameters
5. Note any special business logic

## Quick Reference: File Locations

- Models: `models.py`
- Router: `routers/[table_name_plural].py`
- Main app: `main.py`
- Documentation: `docs/[table-name]-api.md`

## Example: Implementing for "Suppliers" Table

If implementing for a `Suppliers` table:

1. Model name: `Supplier`
2. Router file: `routers/suppliers.py`
3. Routes:
   - `GET /api/suppliers`
   - `GET /api/suppliers/{supplier_code}`
4. Import: `from routers import suppliers`
5. Register: `app.include_router(suppliers.router, prefix="/api", tags=["suppliers"])`

## Troubleshooting

### Common Errors and Solutions

1. **"Syntax Error" in logs**
   - Check query is on single line
   - Verify field names match database exactly
   - Check for missing commas in field list

2. **"KeyError" when creating model**
   - Field name conversion might be wrong
   - Add debug logging to see actual field names
   - Check for special characters in field names

3. **Date parsing errors**
   - Add the field to date handling section
   - Check date format (might need different strptime pattern)

4. **Empty responses**
   - Check table name spelling
   - Verify database connection
   - Check if WHERE clause is too restrictive

Remember: The key to success is matching database field names exactly and handling the ODBC single-line query requirement! 