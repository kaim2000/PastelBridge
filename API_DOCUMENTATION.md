# Pastel Bridge API Documentation

## Overview

Pastel Bridge API provides access to Pastel accounting data with built-in load management to ensure the desktop accounting system remains responsive.

## Load Reduction Features

The API implements several measures to minimize impact on the Pastel system:

- **Single Connection Pool**: Maximum 1 concurrent database connection
- **Aggressive Timeouts**: 5-second connection timeout, 2-second query timeout
- **Rate Limiting**: 15 requests per minute per IP address
- **Minimum Request Interval**: 500ms between requests
- **Circuit Breaker**: Automatically disables API if too many failures occur
- **Small Page Sizes**: Maximum 100 records per page, default 50
- **NOLOCK Hints**: Read queries use NOLOCK to reduce lock contention

## Authentication

All API requests require an `X-API-Key` header:

```
X-API-Key: your-api-key-here
```

## Endpoints

### CustomerMaster

#### List Customers
```
GET /api/customers
```

Query Parameters:
- `cursor` (optional): Cursor for pagination
- `limit` (optional): Number of records to return (1-100, default: 50)
- `customer_code` (optional): Filter by specific customer code
- `category` (optional): Filter by category number

Headers:
- `X-Prefer-Total-Count` (optional): Set to `true` to include total count (impacts performance)

Response:
```json
{
  "data": [
    {
      "category": 0,
      "customer_code": "01ALLS",
      "customer_desc": "Alles Vars",
      "balance_this_01": 0.0,
      "balance_this_02": 0.0,
      // ... all other fields
    }
  ],
  "metadata": {
    "page_size": 50,
    "total_records": null,
    "cursor": null,
    "next_cursor": "MjAwMQ==",
    "has_more": true,
    "timestamp": "2024-03-28T12:54:33"
  }
}
```

Response Headers:
- `X-Query-Time`: Query execution time in seconds
- `X-Page-Size`: Number of records returned
- `X-Load-High`: Present if query time exceeds threshold
- `X-Preferred-Schedule`: Suggested sync schedule if load is high

#### Get Customer by Code
```
GET /api/customers/{customer_code}
```

Path Parameters:
- `customer_code`: The customer code to retrieve

Response: Single CustomerMaster object

### Invoices

#### List Invoices
```
GET /api/invoices
```

Query Parameters:
- `from` (required): Start date (YYYY-MM-DD)
- `to` (required): End date (YYYY-MM-DD)
- `account_code` (optional): Filter by account code
- `limit` (optional): Number of records (1-100, default: 50)

Response: Array of Invoice objects

### Health Check

#### API Health
```
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-03-28T12:54:33",
  "database": "connected"
}
```

## Pagination

The API uses cursor-based pagination for efficient data retrieval:

1. Make initial request without cursor
2. Use `next_cursor` from response for subsequent pages
3. Continue until `has_more` is false

Example:
```python
# First page
response = requests.get("/api/customers", params={"limit": 50})
data = response.json()

# Next page
if data["metadata"]["next_cursor"]:
    response = requests.get("/api/customers", params={
        "limit": 50,
        "cursor": data["metadata"]["next_cursor"]
    })
```

## Error Handling

Common error responses:

- `401 Unauthorized`: Invalid or missing API key
- `403 Forbidden`: IP address not in whitelist
- `429 Too Many Requests`: Rate limit exceeded
- `503 Service Unavailable`: Circuit breaker open or database unavailable

Error response format:
```json
{
  "detail": "Error description"
}
```

## Best Practices

1. **Respect Rate Limits**: Don't exceed 15 requests per minute
2. **Use Cursor Pagination**: Always use cursors for consistent pagination
3. **Small Page Sizes**: Use smaller page sizes (10-50) for better performance
4. **Handle Retries**: Implement exponential backoff for 503 errors
5. **Monitor Headers**: Check X-Load-High header and adjust sync schedule
6. **Avoid Peak Hours**: Schedule syncs during off-peak hours when possible

## Performance Considerations

- Total count queries are expensive - only use when necessary
- Filtering by indexed fields (customer_code, category) is more efficient
- Circuit breaker may activate after 5 consecutive failures
- Recovery timeout is 30 seconds after circuit breaker opens

## Configuration

Key environment variables:

- `MAX_PAGE_SIZE`: Maximum records per page (default: 100)
- `DEFAULT_PAGE_SIZE`: Default page size (default: 50)
- `RATE_LIMIT_PER_MINUTE`: Requests per minute (default: 15)
- `MIN_REQUEST_INTERVAL_MS`: Minimum ms between requests (default: 500)
- `CIRCUIT_BREAKER_ENABLED`: Enable/disable circuit breaker (default: true) 