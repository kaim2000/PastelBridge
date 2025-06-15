# Invoices API Documentation

## Overview

The Invoices API provides access to invoice data from the HistoryHeader table in the Pastel Partner system. This includes all document types (invoices, credit notes, quotes, etc.) with complete header information.

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

### 1. List Invoices

Get a paginated list of invoices with optional filters.

**Endpoint:** `GET /api/invoices`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| cursor | string | No | Cursor for pagination |
| limit | integer | No | Number of records to return (default: 50, max: 100) |
| from_date | date | No | Filter by start date (YYYY-MM-DD) |
| to_date | date | No | Filter by end date (YYYY-MM-DD) |
| customer_code | string | No | Filter by customer code |
| document_type | integer | No | Filter by document type |
| document_number | string | No | Filter by document number |

**Document Types:**
- 1: Quote
- 2: Sales Order
- 3: Invoice
- 4: Credit Note
- 5: Deposit
- 6: Returned Goods
- 8: Purchase Order
- And others specific to your Pastel configuration

**Response:**

```json
{
  "data": [
    {
      "document_type": 3,
      "document_number": "INV123456",
      "customer_code": "CUST001",
      "document_date": "2024-01-15",
      "order_number": "SO12345",
      "salesman_code": "REP01",
      "user_id": 1,
      "excl_incl": 0,
      "message_01": "Thank you for your business",
      "message_02": null,
      "message_03": null,
      "del_address_01": "123 Main Street",
      "del_address_02": "Suite 100",
      "del_address_03": "City Name",
      "del_address_04": "Province",
      "del_address_05": "1234",
      "terms": 30,
      "extra_costs": 0.0,
      "cost_code": null,
      "p_period": -99,
      "closing_date": "2024-01-31",
      "telephone": "011-123-4567",
      "fax": "011-123-4568",
      "contact": "John Doe",
      "currency_code": 0,
      "exchange_rate": 1.0,
      "discount_percent": 5.0,
      "total": 11400.00,
      "f_curr_total": 11400.00,
      "total_tax": 1400.00,
      "f_curr_total_tax": 1400.00,
      "total_cost": 8000.00,
      "inv_deleted": null,
      "inv_print_status": "Y",
      "onhold": 0,
      "grn_misc": null,
      "paid": 0,
      "freight_01": null,
      "ship": null,
      "is_tmb_doc": 0,
      "spare": null,
      "exported": 0,
      "export_ref": null,
      "export_num": 0,
      "emailed": "Y"
    }
  ],
  "metadata": {
    "page_size": 50,
    "cursor": null,
    "next_cursor": "MzpJTlYxMjM0NTY=",
    "has_more": true,
    "timestamp": "2024-01-15T10:30:00.000Z"
  }
}
```

**Example Request:**

```bash
curl -X GET "https://your-server/api/invoices?from_date=2024-01-01&to_date=2024-01-31&limit=20" \
  -H "X-API-Key: your-api-key"
```

### 2. Get Single Invoice

Get details of a specific invoice by document type and number.

**Endpoint:** `GET /api/invoices/{document_type}/{document_number}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| document_type | integer | Yes | Document type code |
| document_number | string | Yes | Document number |

**Response:**

```json
{
  "document_type": 3,
  "document_number": "INV123456",
  "customer_code": "CUST001",
  "document_date": "2024-01-15",
  "order_number": "SO12345",
  "salesman_code": "REP01",
  "user_id": 1,
  "excl_incl": 0,
  "message_01": "Thank you for your business",
  "message_02": null,
  "message_03": null,
  "del_address_01": "123 Main Street",
  "del_address_02": "Suite 100",
  "del_address_03": "City Name",
  "del_address_04": "Province",
  "del_address_05": "1234",
  "terms": 30,
  "extra_costs": 0.0,
  "cost_code": null,
  "p_period": -99,
  "closing_date": "2024-01-31",
  "telephone": "011-123-4567",
  "fax": "011-123-4568",
  "contact": "John Doe",
  "currency_code": 0,
  "exchange_rate": 1.0,
  "discount_percent": 5.0,
  "total": 11400.00,
  "f_curr_total": 11400.00,
  "total_tax": 1400.00,
  "f_curr_total_tax": 1400.00,
  "total_cost": 8000.00,
  "inv_deleted": null,
  "inv_print_status": "Y",
  "onhold": 0,
  "grn_misc": null,
  "paid": 0,
  "freight_01": null,
  "ship": null,
  "is_tmb_doc": 0,
  "spare": null,
  "exported": 0,
  "export_ref": null,
  "export_num": 0,
  "emailed": "Y"
}
```

**Example Request:**

```bash
curl -X GET "https://your-server/api/invoices/3/INV123456" \
  -H "X-API-Key: your-api-key"
```

### 3. Get Customer Invoices

Get all invoices for a specific customer.

**Endpoint:** `GET /api/customers/{customer_code}/invoices`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| customer_code | string | Yes | Customer code |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| cursor | string | No | Cursor for pagination |
| limit | integer | No | Number of records to return (default: 50, max: 100) |
| from_date | date | No | Filter by start date (YYYY-MM-DD) |
| to_date | date | No | Filter by end date (YYYY-MM-DD) |

**Response:** Same as List Invoices endpoint

**Example Request:**

```bash
curl -X GET "https://your-server/api/customers/CUST001/invoices?from_date=2024-01-01" \
  -H "X-API-Key: your-api-key"
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| document_type | integer | Type of document (1=Quote, 3=Invoice, 4=Credit Note, etc.) |
| document_number | string | Unique document number |
| customer_code | string | Customer account code |
| document_date | date | Date of the document |
| order_number | string | Related order number |
| salesman_code | string | Sales representative code |
| user_id | integer | User who created the document |
| excl_incl | integer | 0=Exclusive of tax, 1=Inclusive of tax |
| message_01-03 | string | Custom messages on the document |
| del_address_01-05 | string | Delivery address lines |
| terms | integer | Payment terms in days |
| extra_costs | float | Additional costs |
| cost_code | string | Cost center code |
| p_period | integer | Period number |
| closing_date | date | Closing date for the period |
| telephone | string | Contact telephone |
| fax | string | Contact fax |
| contact | string | Contact person name |
| currency_code | integer | Currency code (0=local currency) |
| exchange_rate | float | Exchange rate to local currency |
| discount_percent | float | Overall discount percentage |
| total | float | Total amount in local currency |
| f_curr_total | float | Total amount in foreign currency |
| total_tax | float | Total tax amount in local currency |
| f_curr_total_tax | float | Total tax amount in foreign currency |
| total_cost | float | Total cost amount |
| inv_deleted | string | Deletion status |
| inv_print_status | string | Print status (Y/N) |
| onhold | integer | On hold status (0=No, 1=Yes) |
| grn_misc | string | GRN miscellaneous field |
| paid | integer | Payment status (0=Unpaid, 1=Paid) |
| freight_01 | string | Freight details |
| ship | string | Shipping method |
| is_tmb_doc | integer | TMB document flag |
| spare | string | Spare field for custom use |
| exported | integer | Export status |
| export_ref | string | Export reference |
| export_num | integer | Export number |
| emailed | string | Email sent status (Y/N) |

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD"
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
  "detail": "Invoice not found: 3/INV999999"
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
  "detail": "Failed to fetch invoices: Database connection error"
}
```

## Pagination

The API uses cursor-based pagination. To get the next page of results:

1. Use the `next_cursor` value from the response metadata
2. Pass it as the `cursor` parameter in the next request
3. Continue until `has_more` is false

Example:

```bash
# First page
curl -X GET "https://your-server/api/invoices?limit=50" \
  -H "X-API-Key: your-api-key"

# Next page
curl -X GET "https://your-server/api/invoices?limit=50&cursor=MzpJTlYxMjM0NTY=" \
  -H "X-API-Key: your-api-key"
```

## Rate Limiting

- Maximum 30 requests per minute per IP address
- Minimum 100ms between requests
- Response includes `X-Process-Time` header with processing time
- 429 response includes `X-Retry-After` header

## Notes

1. All string fields are automatically trimmed of whitespace
2. Date fields accept both ISO format (YYYY-MM-DD) and DD/MM/YYYY format
3. The composite primary key is document_type + document_number
4. Currency code 0 represents the local currency
5. Exchange rate is 1.0 for local currency transactions
6. The p_period field typically uses -99 for current period 