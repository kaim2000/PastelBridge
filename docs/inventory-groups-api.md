# Inventory Groups API

## Overview

The Inventory Groups API provides endpoints to retrieve inventory group information from the Pastel Partner accounting system. Inventory groups define accounting rules and GL account mappings for different types of inventory items.

## Base URL

```
http://localhost:8000/api
```

## Authentication

All requests must include:
- `X-API-Key` header with your API key

## Endpoints

### List Inventory Groups

Get a paginated list of inventory groups.

**Endpoint:** `GET /inventory-groups`

**Query Parameters:**
- `cursor` (optional): Pagination cursor from previous response
- `limit` (optional): Number of items per page (default: 50, max: 100)
- `inv_group` (optional): Filter by specific group code

**Response:** `200 OK`
```json
{
  "data": [
    {
      "inv_group": "001",
      "description": "Wheat Buy as Delivered",
      "sales_acc": "1000002",
      "purch_acc": "2000002",
      "cos_acc": "2000002",
      "adjustment": "2100002",
      "stock_ctl": "7701000",
      "variance": "2150002",
      "purch_variance": "2200002",
      "sales_tax_type": 15,
      "purch_tax_type": 16
    }
  ],
  "metadata": {
    "page_size": 50,
    "cursor": null,
    "next_cursor": "MDAx",
    "has_more": true,
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### Get Single Inventory Group

Get details for a specific inventory group.

**Endpoint:** `GET /inventory-groups/{inv_group}`

**Path Parameters:**
- `inv_group`: The unique group code

**Response:** `200 OK`
```json
{
  "inv_group": "001",
  "description": "Wheat Buy as Delivered",
  "sales_acc": "1000002",
  "purch_acc": "2000002",
  "cos_acc": "2000002",
  "adjustment": "2100002",
  "stock_ctl": "7701000",
  "variance": "2150002",
  "purch_variance": "2200002",
  "sales_tax_type": 15,
  "purch_tax_type": 16
}
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| inv_group | string | Unique inventory group code |
| description | string | Group description |
| sales_acc | string | Sales general ledger account code |
| purch_acc | string | Purchase general ledger account code |
| cos_acc | string | Cost of sales general ledger account code |
| adjustment | string | Stock adjustment general ledger account code |
| stock_ctl | string | Stock control general ledger account code |
| variance | string | Stock variance general ledger account code |
| purch_variance | string | Purchase variance general ledger account code |
| sales_tax_type | integer | Default sales tax type for this group |
| purch_tax_type | integer | Default purchase tax type for this group |

## Error Responses

### 404 Not Found
```json
{
  "detail": "Inventory group not found: 999"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid API key"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to fetch inventory groups: [error details]"
}
```

## Example Usage

### Python
```python
import requests

headers = {
    "X-API-Key": "your-api-key"
}

# List all groups
response = requests.get(
    "http://localhost:8000/api/inventory-groups",
    headers=headers
)

# Get specific group
response = requests.get(
    "http://localhost:8000/api/inventory-groups/001",
    headers=headers
)
```

### cURL
```bash
# List groups
curl -X GET "http://localhost:8000/api/inventory-groups?limit=50" \
  -H "X-API-Key: your-api-key"

# Get specific group
curl -X GET "http://localhost:8000/api/inventory-groups/001" \
  -H "X-API-Key: your-api-key"
```

## Notes

- The `inv_group` field is the primary key and is always required
- Group codes are typically 3 characters
- All string fields are automatically trimmed of whitespace
- Inventory groups define the accounting behavior for inventory items
- The various account codes (sales_acc, purch_acc, etc.) reference general ledger accounts
- Tax types reference the tax configuration in Pastel
- Pagination uses cursor-based navigation for consistent results 