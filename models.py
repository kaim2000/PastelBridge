from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

class Invoice(BaseModel):
    document_number: str
    document_date: date
    account_code: str
    
    
    class Config:
        from_attributes = True

class InvoiceQuery(BaseModel):
    from_date: date
    to_date: date
    account_code: Optional[str] = None
    limit: int = 1000