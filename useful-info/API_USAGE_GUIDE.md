# Pastel Bridge API Usage Guide

## Overview
The Pastel Bridge API provides a secure REST API interface to access Pastel Partner data. This guide covers everything you need to integrate with the API from your CRM or other applications.

## Table of Contents
1. [Authentication](#authentication)
2. [API Endpoints](#api-endpoints)
3. [Request Examples](#request-examples)
4. [Error Handling](#error-handling)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Authentication

The API uses two layers of security:

### 1. API Key Authentication
Every request must include an API key in the `X-API-Key` header:
```
X-API-Key: your-api-key-here
```

### 2. IP Whitelist
Your server's IP address must be whitelisted in the API configuration. Contact the system administrator to add your IP.

## API Endpoints

### Base URL
```
https://[server-address]:8000
```

### Available Endpoints

#### 1. Health Check
```
GET /api/ping
```
Returns the API status and database connection info.

**Response:**
```json
{
    "status": "healthy",
    "database": "connected",
    "connection_test": 1,
    "table_count": 42,
    "dsn": "GRP25_x64"
}
```

#### 2. Get Invoices
```
GET /api/invoices
```
Retrieves invoices within a date range.

**Required Parameters:**
- `from` (date, required): Start date in YYYY-MM-DD format
- `to` (date, required): End date in YYYY-MM-DD format

**Optional Parameters:**
- `account_code` (string): Filter by specific customer account
- `limit` (integer): Maximum number of records (default: 1000, max: 5000)

**Response:**
```json
[
    {
        "document_number": "INV001",
        "document_date": "2025-06-14",
        "account_code": "CUST001"
    }
]
```

## Request Examples

### PHP/Laravel Example

```php
<?php

use Illuminate\Support\Facades\Http;
use Carbon\Carbon;

class PastelBridgeService
{
    private $baseUrl;
    private $apiKey;

    public function __construct()
    {
        $this->baseUrl = config('services.pastel_bridge.url');
        $this->apiKey = config('services.pastel_bridge.api_key');
    }

    /**
     * Get invoices for the last 7 days
     */
    public function getLastWeekInvoices()
    {
        $toDate = Carbon::now()->format('Y-m-d');
        $fromDate = Carbon::now()->subDays(7)->format('Y-m-d');
        
        $response = Http::withHeaders([
            'X-API-Key' => $this->apiKey,
            'Accept' => 'application/json',
        ])
        ->withoutVerifying() // Only for self-signed certificates
        ->get("{$this->baseUrl}/api/invoices", [
            'from' => $fromDate,
            'to' => $toDate,
            'limit' => 100
        ]);

        if ($response->successful()) {
            return $response->json();
        }

        throw new \Exception("API Error: " . $response->body());
    }

    /**
     * Get invoices for a specific customer
     */
    public function getCustomerInvoices($accountCode, $days = 30)
    {
        $toDate = Carbon::now()->format('Y-m-d');
        $fromDate = Carbon::now()->subDays($days)->format('Y-m-d');
        
        $response = Http::withHeaders([
            'X-API-Key' => $this->apiKey,
            'Accept' => 'application/json',
        ])
        ->withoutVerifying()
        ->get("{$this->baseUrl}/api/invoices", [
            'from' => $fromDate,
            'to' => $toDate,
            'account_code' => $accountCode,
            'limit' => 500
        ]);

        if ($response->successful()) {
            return $response->json();
        }

        throw new \Exception("API Error: " . $response->body());
    }

    /**
     * Test API connection
     */
    public function testConnection()
    {
        $response = Http::withHeaders([
            'X-API-Key' => $this->apiKey,
            'Accept' => 'application/json',
        ])
        ->withoutVerifying()
        ->get("{$this->baseUrl}/api/ping");

        return $response->successful();
    }
}
```

### Laravel Configuration (.env)
```env
PASTEL_BRIDGE_URL=https://192.168.1.100:8000
PASTEL_BRIDGE_API_KEY=your-api-key-here
```

### Laravel Config (config/services.php)
```php
'pastel_bridge' => [
    'url' => env('PASTEL_BRIDGE_URL'),
    'api_key' => env('PASTEL_BRIDGE_API_KEY'),
],
```

### Python Example

```python
import requests
from datetime import datetime, timedelta
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings()

class PastelBridgeClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Accept': 'application/json'
        }
    
    def get_invoices(self, from_date, to_date, account_code=None, limit=1000):
        """Get invoices within date range"""
        params = {
            'from': from_date,
            'to': to_date,
            'limit': limit
        }
        
        if account_code:
            params['account_code'] = account_code
        
        response = requests.get(
            f"{self.base_url}/api/invoices",
            headers=self.headers,
            params=params,
            verify=False  # For self-signed certificates
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_last_week_invoices(self):
        """Get invoices from the last 7 days"""
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        return self.get_invoices(from_date, to_date)
    
    def test_connection(self):
        """Test API connectivity"""
        response = requests.get(
            f"{self.base_url}/api/ping",
            headers=self.headers,
            verify=False
        )
        
        return response.status_code == 200

# Usage
client = PastelBridgeClient(
    base_url="https://192.168.1.100:8000",
    api_key="your-api-key-here"
)

# Get last 7 days of invoices
invoices = client.get_last_week_invoices()
for invoice in invoices:
    print(f"Invoice {invoice['document_number']} - {invoice['document_date']}")
```

### cURL Examples

```bash
# Test connection
curl -X GET "https://192.168.1.100:8000/api/ping" \
  -H "X-API-Key: your-api-key-here" \
  -k  # -k flag for self-signed certificates

# Get last 7 days of invoices
curl -X GET "https://192.168.1.100:8000/api/invoices?from=2025-06-08&to=2025-06-15&limit=100" \
  -H "X-API-Key: your-api-key-here" \
  -k

# Get invoices for specific customer
curl -X GET "https://192.168.1.100:8000/api/invoices?from=2025-06-01&to=2025-06-15&account_code=CUST001" \
  -H "X-API-Key: your-api-key-here" \
  -k
```

## Error Handling

### Common Error Responses

#### 401 Unauthorized
Missing or invalid API key.
```json
{
    "detail": "Invalid API key"
}
```

#### 403 Forbidden
IP address not whitelisted.
```json
{
    "detail": "Access forbidden"
}
```

#### 422 Unprocessable Entity
Missing required parameters or invalid data format.
```json
{
    "detail": [
        {
            "loc": ["query", "from"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

#### 429 Too Many Requests
Rate limit exceeded (60 requests per minute).
```json
{
    "detail": "Rate limit exceeded"
}
```

#### 500 Internal Server Error
Database connection or query error.
```json
{
    "detail": "Failed to fetch invoices: [error details]"
}
```

#### 503 Service Unavailable
Database connection failed.
```json
{
    "detail": "Database connection failed: [error details]"
}
```

## Best Practices

### 1. Date Range Optimization
- Always specify reasonable date ranges to avoid large result sets
- Use pagination with smaller date ranges for large data sets
- Consider daily/weekly batch syncs instead of real-time for large volumes

### 2. Error Handling
```php
try {
    $invoices = $pastelService->getLastWeekInvoices();
} catch (\Exception $e) {
    Log::error('Pastel API Error: ' . $e->getMessage());
    
    // Implement retry logic for transient errors
    if (str_contains($e->getMessage(), '503')) {
        // Wait and retry
        sleep(5);
        $invoices = $pastelService->getLastWeekInvoices();
    }
}
```

### 3. Caching
- Cache health check results for 1-5 minutes
- Consider caching invoice data based on your sync frequency
- Implement cache invalidation on updates

### 4. Connection Pooling
- Reuse HTTP clients when possible
- Implement connection timeouts (recommended: 30 seconds)

## Troubleshooting

### Connection Issues

1. **SSL Certificate Errors**
   - The API uses self-signed certificates
   - Disable certificate verification in production carefully
   - Consider using proper SSL certificates for production

2. **Connection Refused**
   - Check if the service is running: `nssm status PastelBridgeAPI`
   - Verify firewall rules allow your IP
   - Check the correct port (default: 8000)

3. **403 Forbidden**
   - Verify your IP is whitelisted in the API's .env file
   - Contact administrator to add your IP to ALLOWED_IPS

4. **401 Unauthorized**
   - Verify API key is correct
   - Ensure X-API-Key header is being sent
   - Check for typos or extra spaces

### Data Issues

1. **No Data Returned**
   - Verify date range contains data
   - Check date format (must be YYYY-MM-DD)
   - Ensure Pastel database has data for the period

2. **Incomplete Data**
   - Check the limit parameter (max 5000)
   - Use smaller date ranges and pagination
   - Verify account_code filter if used

### Performance Issues

1. **Slow Responses**
   - Reduce date range
   - Lower limit parameter
   - Check Pastel database performance
   - Consider implementing caching

2. **Timeouts**
   - Increase client timeout settings
   - Reduce query complexity
   - Check network latency

## Rate Limiting

The API implements rate limiting:
- **Limit**: 60 requests per minute per IP
- **Window**: Rolling 60-second window
- **Response**: 429 status code when exceeded

Implement exponential backoff:
```php
$maxRetries = 3;
$delay = 1;

for ($i = 0; $i < $maxRetries; $i++) {
    $response = $client->get('/api/invoices', $params);
    
    if ($response->status() !== 429) {
        break;
    }
    
    sleep($delay);
    $delay *= 2; // Exponential backoff
}
```

## Security Considerations

1. **API Key Storage**
   - Never commit API keys to version control
   - Use environment variables
   - Rotate keys periodically

2. **SSL/TLS**
   - Use proper certificates in production
   - Keep TLS version updated
   - Monitor certificate expiration

3. **IP Whitelisting**
   - Use static IPs when possible
   - Update whitelist when IPs change
   - Consider VPN for dynamic IPs

## Support

For issues or questions:
1. Check service logs: `C:\PastelBridge\logs\service.log`
2. Verify configuration in `.env` file
3. Contact system administrator for:
   - IP whitelist changes
   - API key resets
   - Service restarts

## Version History

- **v1.0.0** - Initial release
  - Basic invoice retrieval
  - Health check endpoint
  - IP whitelisting and API key auth 