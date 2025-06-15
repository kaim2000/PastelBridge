# API Endpoint Blueprint - Concrete Example: Suppliers Table

This is a filled-out example of the API endpoint blueprint for a hypothetical `Suppliers` table.

## Step 1: Table Analysis

- Table name: `Suppliers`
- Primary key: `SupplierCode`
- Fields from database:
  - SupplierCode
  - SupplierName
  - ContactPerson
  - Telephone
  - Email
  - Address01
  - Address02
  - City
  - PostalCode
  - TaxNumber
  - AccountNumber
  - PaymentTerms
  - CreditLimit
  - LastPurchaseDate
  - Active

## Step 2: Model Implementation

In `models.py`:

```python
# Suppliers models
class Supplier(BaseModel):
    # Primary key field (required)
    supplier_code: str
    
    # Other fields (all optional)
    supplier_name: Optional[str] = None
    contact_person: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    address_01: Optional[str] = None
    address_02: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    tax_number: Optional[str] = None
    account_number: Optional[str] = None
    payment_terms: Optional[int] = None
    credit_limit: Optional[float] = None
    last_purchase_date: Optional[date] = None
    active: Optional[bool] = None
    
    class Config:
        from_attributes = True

class SupplierResponse(BaseModel):
    data: List[Supplier]
    metadata: PaginationMetadata

class SupplierQuery(BaseModel):
    cursor: Optional[str] = None
    limit: int = 50
    supplier_code: Optional[str] = None
    active: Optional[bool] = None
```

## Step 3: Router Implementation

Create `routers/suppliers.py`:

```python
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import db_pool
from config import settings
import logging
from models import Supplier, SupplierResponse, PaginationMetadata
from datetime import datetime
import base64
import re

# Define the router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/suppliers", response_model=SupplierResponse)
async def get_suppliers(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    supplier_code: Optional[str] = Query(None, description="Filter by supplier code"),
    active: Optional[bool] = Query(None, description="Filter by active status")
):
    """Get a paginated list of suppliers"""
    logger.info(f"Supplier request: cursor={cursor}, limit={limit}, supplier_code={supplier_code}, active={active}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor_obj = conn.cursor()
            
            # Build the field list - MUST match exact database column names
            fields = [
                "SupplierCode", "SupplierName", "ContactPerson",
                "Telephone", "Email", "Address01", "Address02",
                "City", "PostalCode", "TaxNumber", "AccountNumber",
                "PaymentTerms", "CreditLimit", "LastPurchaseDate", "Active"
            ]
            
            # Build query - single line to avoid ODBC truncation issues
            field_list = ", ".join(fields)
            query = f"SELECT TOP {limit + 1} {field_list} FROM Suppliers WHERE 1=1"
            params = []
            
            # Add filters
            if supplier_code:
                query += " AND SupplierCode = ?"
                params.append(supplier_code)
            
            if active is not None:
                query += " AND Active = ?"
                params.append(1 if active else 0)
            
            # Add cursor for pagination
            if cursor:
                decoded_cursor = base64.b64decode(cursor).decode('utf-8')
                query += " AND SupplierCode > ?"
                params.append(decoded_cursor)
            
            # Order by primary key
            query += " ORDER BY SupplierCode"
            
            logger.debug(f"Executing query with {len(params)} parameters")
            cursor_obj.execute(query, params)
            
            suppliers = []
            rows = cursor_obj.fetchall()
            
            # Process up to limit rows
            for i, row in enumerate(rows[:limit]):
                supplier_data = {}
                for j, field in enumerate(fields):
                    # Convert field name to snake_case for the model
                    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                    s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                    snake_case_field = s3.lower()
                    value = row[j]
                    
                    # Handle different data types
                    if field == 'LastPurchaseDate' and value:
                        # Date field handling
                        if isinstance(value, str):
                            try:
                                if '/' in value:
                                    supplier_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y').date()
                                else:
                                    supplier_data[snake_case_field] = datetime.fromisoformat(value).date()
                            except:
                                supplier_data[snake_case_field] = None
                        else:
                            supplier_data[snake_case_field] = value
                    elif field == 'Active' and value is not None:
                        # Convert to boolean
                        supplier_data[snake_case_field] = bool(value)
                    elif isinstance(value, str):
                        # Trim string values
                        supplier_data[snake_case_field] = value.strip()
                    else:
                        supplier_data[snake_case_field] = value
                
                suppliers.append(Supplier(**supplier_data))
            
            # Determine if there are more results
            has_more = len(rows) > limit
            next_cursor = None
            if has_more and suppliers:
                next_cursor = base64.b64encode(suppliers[-1].supplier_code.encode('utf-8')).decode('utf-8')
            
            logger.info(f"Retrieved {len(suppliers)} suppliers")
            
            # Build response
            metadata = PaginationMetadata(
                page_size=limit,
                cursor=cursor,
                next_cursor=next_cursor,
                has_more=has_more,
                timestamp=datetime.now()
            )
            
            return SupplierResponse(data=suppliers, metadata=metadata)
            
    except Exception as e:
        logger.error(f"Error fetching suppliers: {e}")
        logger.error(f"Query parameters: cursor={cursor}, limit={limit}, supplier_code={supplier_code}, active={active}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch suppliers: {str(e)}")

# Single record endpoint
@router.get("/suppliers/{supplier_code}", response_model=Supplier)
async def get_supplier(supplier_code: str):
    """Get a single supplier by supplier code"""
    logger.info(f"Supplier detail request: supplier_code={supplier_code}")
    
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all fields
            fields = [
                "SupplierCode", "SupplierName", "ContactPerson",
                "Telephone", "Email", "Address01", "Address02",
                "City", "PostalCode", "TaxNumber", "AccountNumber",
                "PaymentTerms", "CreditLimit", "LastPurchaseDate", "Active"
            ]
            
            # Single line query to avoid ODBC truncation
            field_list = ", ".join(fields)
            query = f"SELECT {field_list} FROM Suppliers WHERE SupplierCode = ?"
            
            cursor.execute(query, [supplier_code])
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Supplier not found: {supplier_code}")
            
            # Build supplier object
            supplier_data = {}
            for j, field in enumerate(fields):
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
                s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
                s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
                snake_case_field = s3.lower()
                value = row[j]
                
                # Handle data types
                if field == 'LastPurchaseDate' and value:
                    if isinstance(value, str):
                        try:
                            if '/' in value:
                                supplier_data[snake_case_field] = datetime.strptime(value, '%d/%m/%Y').date()
                            else:
                                supplier_data[snake_case_field] = datetime.fromisoformat(value).date()
                        except:
                            supplier_data[snake_case_field] = None
                    else:
                        supplier_data[snake_case_field] = value
                elif field == 'Active' and value is not None:
                    supplier_data[snake_case_field] = bool(value)
                elif isinstance(value, str):
                    supplier_data[snake_case_field] = value.strip()
                else:
                    supplier_data[snake_case_field] = value
            
            supplier = Supplier(**supplier_data)
            logger.info(f"Retrieved supplier: {supplier_code}")
            
            return supplier
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching supplier {supplier_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch supplier: {str(e)}")
```

## Step 4: Router Registration

In `main.py`:

```python
# Add to imports
from routers import health, invoices, customers, delivery_addresses, suppliers

# Add router registration
app.include_router(suppliers.router, prefix="/api", tags=["suppliers"])
```

## Result: Working Endpoints

You now have these working endpoints:
- `GET /api/suppliers` - List all suppliers with pagination and filters
- `GET /api/suppliers/{supplier_code}` - Get specific supplier

## Key Differences from Template

1. **Boolean field handling**: Added conversion for the `Active` field
2. **Single primary key**: Simpler cursor handling than composite keys
3. **Date field**: Only one date field (`LastPurchaseDate`) to handle
4. **Filter parameters**: Added `active` filter that converts boolean to 0/1 for database

This example shows how the template adapts to different field types and requirements! 