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
    customer_code: str  # This remains required
    category: Optional[int] = None
    customer_desc: Optional[str] = None
    
    # Balance fields - This Year (01-13)
    balance_this_01: Optional[float] = None
    balance_this_02: Optional[float] = None
    balance_this_03: Optional[float] = None
    balance_this_04: Optional[float] = None
    balance_this_05: Optional[float] = None
    balance_this_06: Optional[float] = None
    balance_this_07: Optional[float] = None
    balance_this_08: Optional[float] = None
    balance_this_09: Optional[float] = None
    balance_this_10: Optional[float] = None
    balance_this_11: Optional[float] = None
    balance_this_12: Optional[float] = None
    balance_this_13: Optional[float] = None
    
    # Balance fields - Last Year (01-13)
    balance_last_01: Optional[float] = None
    balance_last_02: Optional[float] = None
    balance_last_03: Optional[float] = None
    balance_last_04: Optional[float] = None
    balance_last_05: Optional[float] = None
    balance_last_06: Optional[float] = None
    balance_last_07: Optional[float] = None
    balance_last_08: Optional[float] = None
    balance_last_09: Optional[float] = None
    balance_last_10: Optional[float] = None
    balance_last_11: Optional[float] = None
    balance_last_12: Optional[float] = None
    balance_last_13: Optional[float] = None
    
    # Sales fields - This Year (01-13)
    sales_this_01: Optional[float] = None
    sales_this_02: Optional[float] = None
    sales_this_03: Optional[float] = None
    sales_this_04: Optional[float] = None
    sales_this_05: Optional[float] = None
    sales_this_06: Optional[float] = None
    sales_this_07: Optional[float] = None
    sales_this_08: Optional[float] = None
    sales_this_09: Optional[float] = None
    sales_this_10: Optional[float] = None
    sales_this_11: Optional[float] = None
    sales_this_12: Optional[float] = None
    sales_this_13: Optional[float] = None
    
    # Sales fields - Last Year (01-13)
    sales_last_01: Optional[float] = None
    sales_last_02: Optional[float] = None
    sales_last_03: Optional[float] = None
    sales_last_04: Optional[float] = None
    sales_last_05: Optional[float] = None
    sales_last_06: Optional[float] = None
    sales_last_07: Optional[float] = None
    sales_last_08: Optional[float] = None
    sales_last_09: Optional[float] = None
    sales_last_10: Optional[float] = None
    sales_last_11: Optional[float] = None
    sales_last_12: Optional[float] = None
    sales_last_13: Optional[float] = None
    
    # Address fields
    post_address_01: Optional[str] = None
    post_address_02: Optional[str] = None
    post_address_03: Optional[str] = None
    post_address_04: Optional[str] = None
    post_address_05: Optional[str] = None
    
    # Tax and financial fields
    tax_code: Optional[int] = None
    exempt_ref: Optional[str] = None
    settlement_terms: Optional[int] = None
    payment_terms: Optional[int] = None
    discount: Optional[float] = None
    credit_limit: Optional[float] = None
    interest_after: Optional[int] = None
    price_regime: Optional[int] = None
    
    # Transaction info
    last_cr_date: Optional[date] = None
    last_cr_amount: Optional[float] = None
    
    # Flags and settings
    blocked: Optional[int] = None
    open_item: Optional[bool] = None
    over_ride_tax: Optional[int] = None
    month_or_day: Optional[bool] = None
    
    # Currency fields
    country_code: Optional[str] = None
    currency_code: Optional[int] = None
    
    # Currency Balance fields - This Year (01-13)
    curr_balance_this_01: Optional[float] = None
    curr_balance_this_02: Optional[float] = None
    curr_balance_this_03: Optional[float] = None
    curr_balance_this_04: Optional[float] = None
    curr_balance_this_05: Optional[float] = None
    curr_balance_this_06: Optional[float] = None
    curr_balance_this_07: Optional[float] = None
    curr_balance_this_08: Optional[float] = None
    curr_balance_this_09: Optional[float] = None
    curr_balance_this_10: Optional[float] = None
    curr_balance_this_11: Optional[float] = None
    curr_balance_this_12: Optional[float] = None
    curr_balance_this_13: Optional[float] = None
    
    # Currency Balance fields - Last Year (01-13)
    curr_balance_last_01: Optional[float] = None
    curr_balance_last_02: Optional[float] = None
    curr_balance_last_03: Optional[float] = None
    curr_balance_last_04: Optional[float] = None
    curr_balance_last_05: Optional[float] = None
    curr_balance_last_06: Optional[float] = None
    curr_balance_last_07: Optional[float] = None
    curr_balance_last_08: Optional[float] = None
    curr_balance_last_09: Optional[float] = None
    curr_balance_last_10: Optional[float] = None
    curr_balance_last_11: Optional[float] = None
    curr_balance_last_12: Optional[float] = None
    curr_balance_last_13: Optional[float] = None
    
    # User defined fields
    user_defined_01: Optional[str] = None
    user_defined_02: Optional[str] = None
    user_defined_03: Optional[str] = None
    user_defined_04: Optional[str] = None
    user_defined_05: Optional[str] = None
    
    # Ageing fields
    ageing_01: Optional[float] = None
    ageing_02: Optional[float] = None
    ageing_03: Optional[float] = None
    ageing_04: Optional[float] = None
    ageing_05: Optional[float] = None
    
    # Other fields
    interest_per: Optional[str] = None
    freight_01: Optional[str] = None
    ship: Optional[str] = None
    updated_on: Optional[datetime] = None
    cash_account: Optional[bool] = None
    create_date: Optional[date] = None
    
    # Additional name fields
    cust_name: Optional[str] = None
    cust_surname: Optional[str] = None
    cust_id: Optional[str] = None
    
    # Bank details
    bank_name: Optional[str] = None
    bank_type: Optional[int] = None
    bank_branch: Optional[str] = None
    bank_acc_number: Optional[str] = None
    bank_acc_relation: Optional[int] = None
    
    # Additional IDs
    guid: Optional[str] = None
    third_party_id: Optional[str] = None
    passport_number: Optional[str] = None
    
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

# DeliveryAddress models
class DeliveryAddress(BaseModel):
    customer_code: str
    cust_deliv_code: str
    salesman_code: Optional[str] = None
    contact: Optional[str] = None
    telephone: Optional[str] = None
    cell: Optional[str] = None
    fax: Optional[str] = None
    del_address_01: Optional[str] = None
    del_address_02: Optional[str] = None
    del_address_03: Optional[str] = None
    del_address_04: Optional[str] = None
    del_address_05: Optional[str] = None
    email: Optional[str] = None
    contact_docs: Optional[str] = None
    email_docs: Optional[str] = None
    contact_statement: Optional[str] = None
    email_statement: Optional[str] = None
    
    class Config:
        from_attributes = True

class DeliveryAddressResponse(BaseModel):
    data: List[DeliveryAddress]
    metadata: PaginationMetadata

class DeliveryAddressQuery(BaseModel):
    cursor: Optional[str] = None
    limit: int = 50  # Default to 50, max will be enforced in endpoint
    customer_code: Optional[str] = None