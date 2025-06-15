# Delivery Addresses API Documentation

## Overview
The Delivery Addresses API provides access to customer delivery address information from the Pastel Partner system. This API allows you to retrieve delivery addresses with various filtering options and pagination support.

## Authentication
All requests require an API key to be passed in the header:
```
X-API-Key: your-api-key-here
```

## Base URL
```
https://your-domain.com/api
```

## Endpoints

### 1. List All Delivery Addresses
```
GET /delivery-addresses
```

Retrieves a paginated list of all delivery addresses in the system.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_code` | string | No | Filter by specific customer code |
| `cust_deliv_code` | string | No | Filter by specific delivery code |
| `limit` | integer | No | Number of records to return (default: 50, max: 100) |
| `cursor` | string | No | Pagination cursor from previous response |

#### Response Example
```json
{
  "data": [
    {
      "customer_code": "01CAPS",
      "cust_deliv_code": "",
      "salesman_code": "YJBB",
      "contact": "Christolene",
      "telephone": "021 - 863 0031",
      "cell": "",
      "fax": "E021 - 863 0038",
      "del_address_01": "Louw Singel 9",
      "del_address_02": "Suider Paarl",
      "del_address_03": "",
      "del_address_04": "",
      "del_address_05": "",
      "email": "boekhouer2@capebasicproducts.co.za",
      "contact_docs": "Lenatra",
      "email_docs": "boekhouer2@capebasicproducts.co.za",
      "contact_statement": "Christolene",
      "email_statement": "boekhouer2@capebasicproducts.co.za"
    }
  ],
  "metadata": {
    "page_size": 50,
    "cursor": null,
    "next_cursor": "MDFDQVBTOTBERUE=",
    "has_more": true,
    "timestamp": "2024-06-15T21:45:00.123Z"
  }
}
```

### 2. Get Specific Delivery Address
```
GET /delivery-addresses/{customer_code}/{cust_deliv_code}
```

Retrieves a single delivery address by customer code and delivery code.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_code` | string | Yes | The customer code |
| `cust_deliv_code` | string | Yes | The delivery address code |

#### Response Example
```json
{
  "customer_code": "01CAPS",
  "cust_deliv_code": "MAIN",
  "salesman_code": "YJBB",
  "contact": "Christolene",
  "telephone": "021 - 863 0031",
  "cell": "082 123 4567",
  "fax": "E021 - 863 0038",
  "del_address_01": "Louw Singel 9",
  "del_address_02": "Suider Paarl",
  "del_address_03": "7624",
  "del_address_04": "",
  "del_address_05": "",
  "email": "boekhouer2@capebasicproducts.co.za",
  "contact_docs": "Lenatra",
  "email_docs": "boekhouer2@capebasicproducts.co.za",
  "contact_statement": "Christolene",
  "email_statement": "boekhouer2@capebasicproducts.co.za"
}
```

### 3. Get Customer's Delivery Addresses
```
GET /customers/{customer_code}/delivery-addresses
```

Retrieves all delivery addresses for a specific customer.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_code` | string | Yes | The customer code |

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Number of records to return (default: 50, max: 100) |
| `cursor` | string | No | Pagination cursor from previous response |

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `customer_code` | string | Unique identifier for the customer |
| `cust_deliv_code` | string | Unique code for this delivery address (can be empty) |
| `salesman_code` | string | Code of the salesman assigned to this address |
| `contact` | string | Primary contact person name |
| `telephone` | string | Primary telephone number |
| `cell` | string | Mobile/cell phone number |
| `fax` | string | Fax number (may include 'E' prefix for email-to-fax) |
| `del_address_01` | string | Delivery address line 1 (street/building) |
| `del_address_02` | string | Delivery address line 2 (suburb/area) |
| `del_address_03` | string | Delivery address line 3 (city/postal code) |
| `del_address_04` | string | Delivery address line 4 (province/state) |
| `del_address_05` | string | Delivery address line 5 (additional info) |
| `email` | string | Primary email address |
| `contact_docs` | string | Contact person for document delivery |
| `email_docs` | string | Email address for document delivery |
| `contact_statement` | string | Contact person for statements |
| `email_statement` | string | Email address for statements |

## Pagination

The API uses cursor-based pagination for efficient data retrieval:

1. Initial request: Don't include a cursor
2. The response includes `metadata.next_cursor` if more results exist
3. Use this cursor in the next request's `cursor` parameter
4. Continue until `has_more` is false

### Example Pagination Flow
```bash
# First request
GET /api/delivery-addresses?limit=50

# Response includes next_cursor: "MDFDQVBTOTBERUE="

# Next request
GET /api/delivery-addresses?limit=50&cursor=MDFDQVBTOTBERUE=
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid query parameters"
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
  "detail": "Delivery address not found for customer 01CAPS with code MAIN"
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
  "detail": "Failed to fetch delivery addresses: [error details]"
}
```

## Rate Limiting
- Default: 60 requests per minute per IP
- Minimum interval between requests: 100ms
- When rate limited, response includes `X-Retry-After` header

## Best Practices

1. **Use Pagination**: Always implement pagination to handle large datasets efficiently
2. **Handle Empty Fields**: Many fields can be empty strings - handle these appropriately in your UI
3. **Trim Spaces**: While the API trims trailing spaces, be prepared for internal spaces in addresses
4. **Email Fields**: Different email fields serve different purposes:
   - `email`: General contact email
   - `email_docs`: For delivery documents
   - `email_statement`: For financial statements
5. **Error Handling**: Implement proper error handling for all possible HTTP status codes
6. **Caching**: Consider caching delivery addresses locally as they don't change frequently

## Example Integration (JavaScript)

```javascript
const API_KEY = 'your-api-key';
const BASE_URL = 'https://your-domain.com/api';

// Fetch all delivery addresses for a customer
async function getCustomerDeliveryAddresses(customerCode) {
  const response = await fetch(
    `${BASE_URL}/customers/${customerCode}/delivery-addresses`,
    {
      headers: {
        'X-API-Key': API_KEY
      }
    }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  return data;
}

// Fetch with pagination
async function getAllDeliveryAddresses() {
  let allAddresses = [];
  let cursor = null;
  let hasMore = true;
  
  while (hasMore) {
    const url = new URL(`${BASE_URL}/delivery-addresses`);
    url.searchParams.append('limit', '100');
    if (cursor) {
      url.searchParams.append('cursor', cursor);
    }
    
    const response = await fetch(url, {
      headers: {
        'X-API-Key': API_KEY
      }
    });
    
    const data = await response.json();
    allAddresses = allAddresses.concat(data.data);
    
    cursor = data.metadata.next_cursor;
    hasMore = data.metadata.has_more;
  }
  
  return allAddresses;
}
``` 