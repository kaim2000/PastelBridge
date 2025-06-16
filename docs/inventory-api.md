# Inventory API

## Overview

The Inventory API provides endpoints to retrieve inventory item information from the Pastel Partner accounting system. This API supports pagination, filtering, and single item lookups.

## Base URL

```
http://localhost:8000/api
```

## Authentication

All requests must include:
- `X-API-Key` header with your API key

## Endpoints

### List Inventory Items

Get a paginated list of inventory items.

**Endpoint:** `GET /inventory`

**Query Parameters:**
- `cursor` (optional): Pagination cursor from previous response
- `limit` (optional): Number of items per page (default: 50, max: 100)
- `item_code` (optional): Filter by specific item code
- `category` (optional): Filter by category code
- `blocked` (optional): Filter by blocked status (0=not blocked, 1=blocked)
- `physical` (optional): Filter by physical status (0=non-physical, 1=physical)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "item_code": "1013001001",
      "category": "041",
      "description": "SW Stone Ground All Purpose 5*1kg",
      "barcode": "",
      "discount_type": 3,
      "blocked": 0,
      "fixed": 0,
      "show_qty": 1,
      "physical": 1,
      "unit_size": "Bale",
      "sales_tax_type": 1,
      "purch_tax_type": 4,
      "gl_code": "",
      "allow_tax": 1,
      "link_web": "",
      "sales_commision": 1,
      "serial_item": 0,
      "picture": "",
      "user_def_text_01": "",
      "user_def_text_02": "",
      "user_def_text_03": "",
      "user_def_num_01": 0.0,
      "user_def_num_02": 0.0,
      "user_def_num_03": 0.0,
      "commodity_code": "",
      "nett_mass": 0.01,
      "updated_on": "2025-05-14T12:26:28",
      "guid": "226E5E2544D08E2D2BDA0C8F6FBDA8FE"
    }
  ],
  "metadata": {
    "page_size": 50,
    "cursor": null,
    "next_cursor": "MTAxMzAwMTAwMQ==",
    "has_more": true,
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### Get Single Inventory Item

Get details for a specific inventory item.

**Endpoint:** `GET /inventory/{item_code}`

**Path Parameters:**
- `item_code`: The unique item code

**Response:** `200 OK`
```json
{
  "item_code": "1013001001",
  "category": "041",
  "description": "SW Stone Ground All Purpose 5*1kg",
  "barcode": "",
  "discount_type": 3,
  "blocked": 0,
  "fixed": 0,
  "show_qty": 1,
  "physical": 1,
  "unit_size": "Bale",
  "sales_tax_type": 1,
  "purch_tax_type": 4,
  "gl_code": "",
  "allow_tax": 1,
  "link_web": "",
  "sales_commision": 1,
  "serial_item": 0,
  "picture": "",
  "user_def_text_01": "",
  "user_def_text_02": "",
  "user_def_text_03": "",
  "user_def_num_01": 0.0,
  "user_def_num_02": 0.0,
  "user_def_num_03": 0.0,
  "commodity_code": "",
  "nett_mass": 0.01,
  "updated_on": "2025-05-14T12:26:28",
  "guid": "226E5E2544D08E2D2BDA0C8F6FBDA8FE"
}
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| item_code | string | Unique item code identifier |
| category | string | Category code the item belongs to |
| description | string | Item description |
| barcode | string | Item barcode |
| discount_type | integer | Type of discount applicable |
| blocked | integer | Whether item is blocked (0=no, 1=yes) |
| fixed | integer | Whether item has fixed pricing |
| show_qty | integer | Whether to show quantity |
| physical | integer | Whether item is physical (0=non-physical, 1=physical) |
| unit_size | string | Unit of measurement |
| sales_tax_type | integer | Sales tax type code |
| purch_tax_type | integer | Purchase tax type code |
| gl_code | string | General ledger code |
| allow_tax | integer | Whether tax is allowed |
| link_web | string | Web link reference |
| sales_commision | integer | Whether sales commission applies |
| serial_item | integer | Whether item is serialized |
| picture | string | Picture reference |
| user_def_text_01 | string | User-defined text field 1 |
| user_def_text_02 | string | User-defined text field 2 |
| user_def_text_03 | string | User-defined text field 3 |
| user_def_num_01 | float | User-defined numeric field 1 |
| user_def_num_02 | float | User-defined numeric field 2 |
| user_def_num_03 | float | User-defined numeric field 3 |
| commodity_code | string | Commodity code for customs |
| nett_mass | float | Net mass/weight |
| updated_on | datetime | Last update timestamp |
| guid | string | Global unique identifier |

## Error Responses

### 404 Not Found
```json
{
  "detail": "Inventory item not found: ABC123"
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
  "detail": "Failed to fetch inventory: [error details]"
}
```

## Example Usage

### Python
```python
import requests

headers = {
    "X-API-Key": "your-api-key"
}

# List inventory with filters
response = requests.get(
    "http://localhost:8000/api/inventory",
    headers=headers,
    params={
        "limit": 50,
        "category": "041",
        "physical": 1
    }
)

# Get specific item
response = requests.get(
    "http://localhost:8000/api/inventory/1013001001",
    headers=headers
)
```

### cURL
```bash
# List inventory
curl -X GET "http://localhost:8000/api/inventory?limit=50&category=041" \
  -H "X-API-Key: your-api-key"

# Get specific item
curl -X GET "http://localhost:8000/api/inventory/1013001001" \
  -H "X-API-Key: your-api-key"
```

## Notes

- The `item_code` field is the primary key and is always required
- All string fields are automatically trimmed of whitespace
- The `updated_on` field reflects when the item was last modified in Pastel
- Empty strings in numeric fields are returned as null
- Pagination uses cursor-based navigation for consistent results 