# History Lines API Documentation

## Overview

The History Lines API provides access to invoice line item data from the HistoryLines table in the Pastel Partner system. This includes detailed information about products/services on invoices, credit notes, quotes, and other documents.

## Authentication

All endpoints require an API key to be passed in the `X-API-Key` header:

```
X-API-Key: your-api-key
```

## Base URL

```
https://your-server/api
```

## Endpoints

### 1. List History Lines

Get a paginated list of history lines with optional filters.

**Endpoint:** `GET /api/history-lines`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| cursor | string | No | Cursor for pagination |
| limit | integer | No | Number of records to return (default: 50, max: 100) |
| document_type | integer | No | Filter by document type |
| document_number | string | No | Filter by document number |
| customer_code | string | No | Filter by customer code |
| item_code | string | No | Filter by item/product code |

**Response:**

```json
{
  "data": [
    {
      "document_type": 3,
      "document_number": "INV123456",
      "link_num": 1,
      "user_id": 4,
      "item_code": "PROD001",
      "customer_code": "CUST001",
      "salesman_code": "REP01",
      "search_type": 4,
      "p_period": -99,
      "d_date": "2024-01-15",
      "unit_used": "Each",
      "tax_type": 1,
      "discount_type": 3,
      "discount_percentage": 0,
      "description": "Product Description - 1kg",
      "cost_price": 85.50,
      "qty": 10.0,
      "unit_price": 100.00,
      "inclusive_price": 114.00,
      "f_curr_unit_price": 100.00,
      "f_curr_incl_price": 114.00,
      "tax_amt": 140.00,
      "f_curr_tax_amount": 140.00,
      "discount_amount": 0.00,
      "f_c_discount_amount": 0.00,
      "cost_code": null,
      "date_time": null,
      "physical": 1,
      "fixed": 0,
      "show_qty": 1,
      "linked_num": 0,
      "grn_qty": 0.0,
      "link_id": 0,
      "multi_store": "001",
      "is_tmb_line": 0,
      "link_document_type": 2,
      "link_document_number": "SO12345",
      "exported": 0,
      "export_ref": null,
      "export_num": 0,
      "qty_left": 0.0,
      "case_lot_code": null,
      "case_lot_qty": 10.0,
      "case_lot_ratio": 1.0,
      "cost_sync_done": null
    }
  ],
  "metadata": {
    "page_size": 50,
    "cursor": null,
    "next_cursor": "MzpJTlYxMjM0NTY6MQ==",
    "has_more": true,
    "timestamp": "2024-01-15T10:30:00.000Z"
  }
}
```

**Example Request:**

```bash
curl -X GET "https://your-server/api/history-lines?document_type=3&customer_code=CUST001" \
  -H "X-API-Key: your-api-key"
```

### 2. Get Single History Line

Get details of a specific history line by document type, number, and link number.

**Endpoint:** `GET /api/history-lines/{document_type}/{document_number}/{link_num}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| document_type | integer | Yes | Document type code |
| document_number | string | Yes | Document number |
| link_num | integer | Yes | Line item number (link number) |

**Response:**

```json
{
  "document_type": 3,
  "document_number": "INV123456",
  "link_num": 1,
  "user_id": 4,
  "item_code": "PROD001",
  "customer_code": "CUST001",
  "salesman_code": "REP01",
  "search_type": 4,
  "p_period": -99,
  "d_date": "2024-01-15",
  "unit_used": "Each",
  "tax_type": 1,
  "discount_type": 3,
  "discount_percentage": 0,
  "description": "Product Description - 1kg",
  "cost_price": 85.50,
  "qty": 10.0,
  "unit_price": 100.00,
  "inclusive_price": 114.00,
  "f_curr_unit_price": 100.00,
  "f_curr_incl_price": 114.00,
  "tax_amt": 140.00,
  "f_curr_tax_amount": 140.00,
  "discount_amount": 0.00,
  "f_c_discount_amount": 0.00,
  "cost_code": null,
  "date_time": null,
  "physical": 1,
  "fixed": 0,
  "show_qty": 1,
  "linked_num": 0,
  "grn_qty": 0.0,
  "link_id": 0,
  "multi_store": "001",
  "is_tmb_line": 0,
  "link_document_type": 2,
  "link_document_number": "SO12345",
  "exported": 0,
  "export_ref": null,
  "export_num": 0,
  "qty_left": 0.0,
  "case_lot_code": null,
  "case_lot_qty": 10.0,
  "case_lot_ratio": 1.0,
  "cost_sync_done": null
}
```

**Example Request:**

```bash
curl -X GET "https://your-server/api/history-lines/3/INV123456/1" \
  -H "X-API-Key: your-api-key"
```

### 3. Get Invoice Lines

Get all line items for a specific invoice.

**Endpoint:** `GET /api/invoices/{document_type}/{document_number}/lines`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| document_type | integer | Yes | Document type code |
| document_number | string | Yes | Document number |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| cursor | string | No | Cursor for pagination |
| limit | integer | No | Number of records to return (default: 50, max: 100) |

**Response:** Same structure as List History Lines endpoint

**Example Request:**

```bash
curl -X GET "https://your-server/api/invoices/3/INV123456/lines" \
  -H "X-API-Key: your-api-key"
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| document_type | integer | Type of document (matches HistoryHeader) |
| document_number | string | Document number (matches HistoryHeader) |
| link_num | integer | Line item sequence number |
| user_id | integer | User who created the line |
| item_code | string | Product/service code |
| customer_code | string | Customer account code |
| salesman_code | string | Sales representative code |
| search_type | integer | Search type used |
| p_period | integer | Period number |
| d_date | date | Transaction date |
| unit_used | string | Unit of measure |
| tax_type | integer | Tax type code |
| discount_type | integer | Type of discount applied |
| discount_percentage | float | Discount percentage |
| description | string | Item description |
| cost_price | float | Cost price per unit |
| qty | float | Quantity |
| unit_price | float | Unit price excluding tax |
| inclusive_price | float | Unit price including tax |
| f_curr_unit_price | float | Foreign currency unit price |
| f_curr_incl_price | float | Foreign currency inclusive price |
| tax_amt | float | Tax amount |
| f_curr_tax_amount | float | Foreign currency tax amount |
| discount_amount | float | Discount amount |
| f_c_discount_amount | float | Foreign currency discount amount |
| cost_code | string | Cost center code |
| date_time | datetime | Transaction timestamp |
| physical | integer | Physical item flag (1=Yes, 0=No) |
| fixed | integer | Fixed price flag |
| show_qty | integer | Show quantity flag |
| linked_num | integer | Linked line number |
| grn_qty | float | Goods received quantity |
| link_id | integer | Link identifier |
| multi_store | string | Store code |
| is_tmb_line | integer | TMB line flag |
| link_document_type | integer | Linked document type |
| link_document_number | string | Linked document number |
| exported | integer | Export status |
| export_ref | string | Export reference |
| export_num | integer | Export number |
| qty_left | float | Remaining quantity |
| case_lot_code | string | Case/lot code |
| case_lot_qty | float | Case/lot quantity |
| case_lot_ratio | float | Case/lot ratio |
| cost_sync_done | string | Cost sync status |

## Calculations and Relationships

### Line Total Calculations

```
Line Total (excl tax) = qty * unit_price - discount_amount
Line Total (incl tax) = qty * inclusive_price - discount_amount
Tax Amount = tax_amt (already calculated)
```

### Document Type Reference

The `document_type` field matches the types in HistoryHeader:
- 1: Quote
- 2: Sales Order  
- 3: Invoice
- 4: Credit Note
- 5: Deposit
- 6: Returned Goods
- 8: Purchase Order
- And others specific to your Pastel configuration

### Linking

- Lines can be linked to other documents via `link_document_type` and `link_document_number`
- For example, an invoice line might link back to a sales order line
- The `link_num` provides the sequence within a document

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid parameter value"
}
```

### 401 Unauthorized

```json
{
  "detail": "Invalid API key"
}
```

### 403 Forbidden

```json
{
  "detail": "Access forbidden"
}
```

### 404 Not Found

```json
{
  "detail": "History line not found: 3/INV123456/1"
}
```

### 429 Too Many Requests

```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Failed to fetch history lines: Database connection error"
}
```

## Pagination

The API uses cursor-based pagination with composite keys. The cursor encodes:
- document_type
- document_number  
- link_num

To get the next page:

1. Use the `next_cursor` value from the response metadata
2. Pass it as the `cursor` parameter in the next request
3. Continue until `has_more` is false

Example:

```bash
# First page
curl -X GET "https://your-server/api/history-lines?limit=50" \
  -H "X-API-Key: your-api-key"

# Next page
curl -X GET "https://your-server/api/history-lines?limit=50&cursor=MzpJTlYxMjM0NTY6MQ==" \
  -H "X-API-Key: your-api-key"
```

## Rate Limiting

- Maximum 30 requests per minute per IP address
- Minimum 100ms between requests
- Response includes `X-Process-Time` header with processing time
- 429 response includes `X-Retry-After` header

## Integration Examples

### Get Complete Invoice with Lines

```python
import requests
import base64

API_KEY = "your-api-key"
BASE_URL = "https://your-server/api"

# Get invoice header
invoice_response = requests.get(
    f"{BASE_URL}/invoices/3/INV123456",
    headers={"X-API-Key": API_KEY}
)
invoice = invoice_response.json()

# Get invoice lines
lines_response = requests.get(
    f"{BASE_URL}/invoices/3/INV123456/lines",
    headers={"X-API-Key": API_KEY}
)
lines = lines_response.json()

# Calculate totals
total_excl = sum(line['qty'] * line['unit_price'] - line['discount_amount'] 
                 for line in lines['data'])
total_tax = sum(line['tax_amt'] for line in lines['data'])
total_incl = total_excl + total_tax

print(f"Invoice: {invoice['document_number']}")
print(f"Customer: {invoice['customer_code']}")
print(f"Lines: {len(lines['data'])}")
print(f"Total: {total_incl}")
```

### Filter Lines by Product

```bash
# Get all lines for a specific product across all documents
curl -X GET "https://your-server/api/history-lines?item_code=PROD001&limit=100" \
  -H "X-API-Key: your-api-key"
```

## Notes

1. All string fields are automatically trimmed of whitespace
2. The composite primary key is document_type + document_number + link_num
3. Quantities can be decimal values for partial units
4. The `physical` flag indicates if the item affects inventory
5. Tax calculations depend on the `tax_type` and system configuration
6. The `multi_store` field indicates which store location the line relates to
7. Date fields accept both ISO format (YYYY-MM-DD) and DD/MM/YYYY format 