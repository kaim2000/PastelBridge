# Inventory Categories API

## Overview

The Inventory Categories API provides endpoints to retrieve inventory category information from the Pastel Partner accounting system. Categories are used to group inventory items for organizational and reporting purposes.

## Base URL

```
http://localhost:8000/api
```

## Authentication

All requests must include:
- `X-API-Key` header with your API key

## Endpoints

### List Inventory Categories

Get a paginated list of inventory categories.

**Endpoint:** `GET /inventory-categories`

**Query Parameters:**
- `cursor` (optional): Pagination cursor from previous response
- `limit` (optional): Number of items per page (default: 50, max: 100)
- `ic_code` (optional): Filter by specific category code

**Response:** `200 OK`
```json
{
  "data": [
    {
      "ic_code": "001",
      "ic_desc": "Best Bake Cake Flour"
    },
    {
      "ic_code": "002",
      "ic_desc": "Bread Flour"
    }
  ],
  "metadata": {
    "page_size": 50,
    "cursor": null,
    "next_cursor": "MDAy",
    "has_more": true,
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### Get Single Inventory Category

Get details for a specific inventory category.

**Endpoint:** `GET /inventory-categories/{ic_code}`

**Path Parameters:**
- `ic_code`: The unique category code

**Response:** `200 OK`
```json
{
  "ic_code": "001",
  "ic_desc": "Best Bake Cake Flour"
}
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| ic_code | string | Unique category code identifier |
| ic_desc | string | Category description |

## Error Responses

### 404 Not Found
```json
{
  "detail": "Inventory category not found: 999"
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
  "detail": "Failed to fetch inventory categories: [error details]"
}
```

## Example Usage

### Python
```python
import requests

headers = {
    "X-API-Key": "your-api-key"
}

# List all categories
response = requests.get(
    "http://localhost:8000/api/inventory-categories",
    headers=headers
)

# Get specific category
response = requests.get(
    "http://localhost:8000/api/inventory-categories/001",
    headers=headers
)
```

### cURL
```bash
# List categories
curl -X GET "http://localhost:8000/api/inventory-categories?limit=50" \
  -H "X-API-Key: your-api-key"

# Get specific category
curl -X GET "http://localhost:8000/api/inventory-categories/001" \
  -H "X-API-Key: your-api-key"
```

## Notes

- The `ic_code` field is the primary key and is always required
- Category codes are typically 3 characters
- All string fields are automatically trimmed of whitespace
- Categories are used to group inventory items and can be referenced in the Inventory API via the `category` field
- Pagination uses cursor-based navigation for consistent results 