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

# CustomerMaster models
class CustomerMaster(BaseModel):
    category: int
    customer_code: str
    customer_desc: str
    
    # Balance fields - This Year (01-13)
    balance_this_01: float
    balance_this_02: float
    balance_this_03: float
    balance_this_04: float
    balance_this_05: float
    balance_this_06: float
    balance_this_07: float
    balance_this_08: float
    balance_this_09: float
    balance_this_10: float
    balance_this_11: float
    balance_this_12: float
    balance_this_13: float
    
    # Balance fields - Last Year (01-13)
    balance_last_01: float
    balance_last_02: float
    balance_last_03: float
    balance_last_04: float
    balance_last_05: float
    balance_last_06: float
    balance_last_07: float
    balance_last_08: float
    balance_last_09: float
    balance_last_10: float
    balance_last_11: float
    balance_last_12: float
    balance_last_13: float
    
    # Sales fields - This Year (01-13)
    sales_this_01: float
    sales_this_02: float
    sales_this_03: float
    sales_this_04: float
    sales_this_05: float
    sales_this_06: float
    sales_this_07: float
    sales_this_08: float
    sales_this_09: float
    sales_this_10: float
    sales_this_11: float
    sales_this_12: float
    sales_this_13: float
    
    # Sales fields - Last Year (01-13)
    sales_last_01: float
    sales_last_02: float
    sales_last_03: float
    sales_last_04: float
    sales_last_05: float
    sales_last_06: float
    sales_last_07: float
    sales_last_08: float
    sales_last_09: float
    sales_last_10: float
    sales_last_11: float
    sales_last_12: float
    sales_last_13: float
    
    # Address fields
    post_address_01: str
    post_address_02: str
    post_address_03: str
    post_address_04: str
    post_address_05: str
    
    # Tax and financial fields
    tax_code: int
    exempt_ref: str
    settlement_terms: int
    payment_terms: int
    discount: float
    credit_limit: float
    interest_after: int
    price_regime: int
    
    # Transaction info
    last_cr_date: Optional[date]
    last_cr_amount: float
    
    # Flags and settings
    blocked: int
    open_item: bool
    over_ride_tax: int
    month_or_day: bool
    
    # Currency fields
    country_code: str
    currency_code: int
    
    # Currency Balance fields - This Year (01-13)
    curr_balance_this_01: float
    curr_balance_this_02: float
    curr_balance_this_03: float
    curr_balance_this_04: float
    curr_balance_this_05: float
    curr_balance_this_06: float
    curr_balance_this_07: float
    curr_balance_this_08: float
    curr_balance_this_09: float
    curr_balance_this_10: float
    curr_balance_this_11: float
    curr_balance_this_12: float
    curr_balance_this_13: float
    
    # Currency Balance fields - Last Year (01-13)
    curr_balance_last_01: float
    curr_balance_last_02: float
    curr_balance_last_03: float
    curr_balance_last_04: float
    curr_balance_last_05: float
    curr_balance_last_06: float
    curr_balance_last_07: float
    curr_balance_last_08: float
    curr_balance_last_09: float
    curr_balance_last_10: float
    curr_balance_last_11: float
    curr_balance_last_12: float
    curr_balance_last_13: float
    
    # User defined fields
    user_defined_01: str
    user_defined_02: str
    user_defined_03: str
    user_defined_04: str
    user_defined_05: str
    
    # Ageing fields
    ageing_01: float
    ageing_02: float
    ageing_03: float
    ageing_04: float
    ageing_05: float
    
    # Other fields
    interest_per: str
    freight_01: str
    ship: str
    updated_on: Optional[datetime]
    cash_account: bool
    create_date: Optional[date]
    
    # Additional name fields
    cust_name: str
    cust_surname: str
    cust_id: str
    
    # Bank details
    bank_name: str
    bank_type: int
    bank_branch: str
    bank_acc_number: str
    bank_acc_relation: int
    
    # Additional IDs
    guid: str
    third_party_id: str
    passport_number: str
    
    class Config:
        from_attributes = True

# Pagination models
class PaginationMetadata(BaseModel):
    page_size: int
    total_records: Optional[int] = None
    cursor: Optional[str] = None
    next_cursor: Optional[str] = None
    has_more: bool
    timestamp: datetime

class CustomerMasterResponse(BaseModel):
    data: List[CustomerMaster]
    metadata: PaginationMetadata

class CustomerQuery(BaseModel):
    cursor: Optional[str] = None
    limit: int = 50  # Default to 50, max will be enforced in endpoint
    customer_code: Optional[str] = None
    category: Optional[int] = None