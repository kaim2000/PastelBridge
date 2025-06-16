from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

# Pagination models (moved to top as they're used by other models)
class PaginationMetadata(BaseModel):
    page_size: int
    total_records: Optional[int] = None
    cursor: Optional[str] = None
    next_cursor: Optional[str] = None
    has_more: bool
    timestamp: datetime

# Invoice (HistoryHeader) models
class Invoice(BaseModel):
    # Primary key fields
    document_type: int
    document_number: str
    
    # Core fields
    customer_code: str
    document_date: date
    order_number: Optional[str] = None
    salesman_code: Optional[str] = None
    user_id: Optional[int] = None
    excl_incl: Optional[int] = None
    
    # Message fields
    message_01: Optional[str] = None
    message_02: Optional[str] = None
    message_03: Optional[str] = None
    
    # Delivery address fields
    del_address_01: Optional[str] = None
    del_address_02: Optional[str] = None
    del_address_03: Optional[str] = None
    del_address_04: Optional[str] = None
    del_address_05: Optional[str] = None
    
    # Financial fields
    terms: Optional[int] = None
    extra_costs: Optional[float] = None
    cost_code: Optional[str] = None
    p_period: Optional[int] = None
    closing_date: Optional[date] = None
    
    # Contact fields
    telephone: Optional[str] = None
    fax: Optional[str] = None
    contact: Optional[str] = None
    
    # Currency fields
    currency_code: Optional[int] = None
    exchange_rate: Optional[float] = None
    
    # Totals and tax
    discount_percent: Optional[float] = None
    total: Optional[float] = None
    f_curr_total: Optional[float] = None
    total_tax: Optional[float] = None
    f_curr_total_tax: Optional[float] = None
    total_cost: Optional[float] = None
    
    # Status fields
    inv_deleted: Optional[str] = None
    inv_print_status: Optional[str] = None
    onhold: Optional[int] = None
    grn_misc: Optional[str] = None
    paid: Optional[int] = None
    
    # Shipping fields
    freight_01: Optional[str] = None
    ship: Optional[str] = None
    
    # TMB and export fields
    is_tmb_doc: Optional[int] = None
    spare: Optional[str] = None
    exported: Optional[int] = None
    export_ref: Optional[str] = None
    export_num: Optional[int] = None
    emailed: Optional[str] = None
    
    class Config:
        from_attributes = True

class InvoiceResponse(BaseModel):
    data: List[Invoice]
    metadata: PaginationMetadata

class InvoiceQuery(BaseModel):
    cursor: Optional[str] = None
    limit: int = 50
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    customer_code: Optional[str] = None
    document_type: Optional[int] = None
    document_number: Optional[str] = None

# HistoryLines models
class HistoryLine(BaseModel):
    # Primary keys
    document_type: int
    document_number: str
    link_num: int
    
    # Core fields
    user_id: Optional[int] = None
    item_code: Optional[str] = None
    customer_code: Optional[str] = None
    salesman_code: Optional[str] = None
    search_type: Optional[int] = None
    p_period: Optional[int] = None
    d_date: Optional[date] = None
    unit_used: Optional[str] = None
    
    # Tax and discount
    tax_type: Optional[int] = None
    discount_type: Optional[int] = None
    discount_percentage: Optional[float] = None
    description: Optional[str] = None
    
    # Pricing fields
    cost_price: Optional[float] = None
    qty: Optional[float] = None
    unit_price: Optional[float] = None
    inclusive_price: Optional[float] = None
    f_curr_unit_price: Optional[float] = None
    f_curr_incl_price: Optional[float] = None
    tax_amt: Optional[float] = None
    f_curr_tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    f_c_discount_amount: Optional[float] = None
    
    # Additional fields
    cost_code: Optional[str] = None
    date_time: Optional[datetime] = None
    physical: Optional[int] = None
    fixed: Optional[int] = None
    show_qty: Optional[int] = None
    linked_num: Optional[int] = None
    grn_qty: Optional[float] = None
    link_id: Optional[int] = None
    multi_store: Optional[str] = None
    is_tmb_line: Optional[int] = None
    
    # Link document fields
    link_document_type: Optional[int] = None
    link_document_number: Optional[str] = None
    
    # Export fields
    exported: Optional[int] = None
    export_ref: Optional[str] = None
    export_num: Optional[int] = None
    qty_left: Optional[float] = None
    
    # Case lot fields
    case_lot_code: Optional[str] = None
    case_lot_qty: Optional[float] = None
    case_lot_ratio: Optional[float] = None
    cost_sync_done: Optional[str] = None
    
    class Config:
        from_attributes = True

class HistoryLineResponse(BaseModel):
    data: List[HistoryLine]
    metadata: PaginationMetadata

class HistoryLineQuery(BaseModel):
    cursor: Optional[str] = None
    limit: int = 50
    document_type: Optional[int] = None
    document_number: Optional[str] = None
    customer_code: Optional[str] = None
    item_code: Optional[str] = None

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

# Inventory models
class Inventory(BaseModel):
    # Primary key field (required)
    item_code: str
    
    # Other fields (all optional)
    category: Optional[str] = None
    description: Optional[str] = None
    barcode: Optional[str] = None
    discount_type: Optional[int] = None
    blocked: Optional[int] = None
    fixed: Optional[int] = None
    show_qty: Optional[int] = None
    physical: Optional[int] = None
    unit_size: Optional[str] = None
    sales_tax_type: Optional[int] = None
    purch_tax_type: Optional[int] = None
    gl_code: Optional[str] = None
    allow_tax: Optional[int] = None
    link_web: Optional[str] = None
    sales_commision: Optional[int] = None  # Note: keeping database spelling
    serial_item: Optional[int] = None
    picture: Optional[str] = None
    user_def_text_01: Optional[str] = None
    user_def_text_02: Optional[str] = None
    user_def_text_03: Optional[str] = None
    user_def_num_01: Optional[float] = None
    user_def_num_02: Optional[float] = None
    user_def_num_03: Optional[float] = None
    commodity_code: Optional[str] = None
    nett_mass: Optional[float] = None
    updated_on: Optional[datetime] = None
    guid: Optional[str] = None
    
    class Config:
        from_attributes = True

class InventoryResponse(BaseModel):
    data: List[Inventory]
    metadata: PaginationMetadata

class InventoryQuery(BaseModel):
    cursor: Optional[str] = None
    limit: int = 50
    item_code: Optional[str] = None
    category: Optional[str] = None
    blocked: Optional[int] = None
    physical: Optional[int] = None

# InventoryCategory models
class InventoryCategory(BaseModel):
    # Primary key field (required)
    ic_code: str
    
    # Other fields
    ic_desc: Optional[str] = None
    
    class Config:
        from_attributes = True

class InventoryCategoryResponse(BaseModel):
    data: List[InventoryCategory]
    metadata: PaginationMetadata

class InventoryCategoryQuery(BaseModel):
    cursor: Optional[str] = None
    limit: int = 50
    ic_code: Optional[str] = None

# InventoryGroups models
class InventoryGroup(BaseModel):
    # Primary key field (required)
    inv_group: str
    
    # Other fields
    description: Optional[str] = None
    sales_acc: Optional[str] = None
    purch_acc: Optional[str] = None
    cos_acc: Optional[str] = None
    adjustment: Optional[str] = None
    stock_ctl: Optional[str] = None
    variance: Optional[str] = None
    purch_variance: Optional[str] = None
    sales_tax_type: Optional[int] = None
    purch_tax_type: Optional[int] = None
    
    class Config:
        from_attributes = True

class InventoryGroupResponse(BaseModel):
    data: List[InventoryGroup]
    metadata: PaginationMetadata

class InventoryGroupQuery(BaseModel):
    cursor: Optional[str] = None
    limit: int = 50
    inv_group: Optional[str] = None