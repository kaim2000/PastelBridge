# Quick Fix: Retrieving Last 7 Days of Invoices

## The Problem
Based on your logs, the issue with retrieving invoices is that **the API requires both `from` and `to` date parameters**, but your CRM might not be sending them correctly.

Looking at your logs:
- ❌ `GET /api/invoices?limit=1` → 422 Unprocessable Content (missing dates)
- ✅ `GET /api/invoices?from=2025-06-08&to=2025-06-15&limit=100` → 200 OK

## The Solution

### For Your CRM Developer

The invoice endpoint **requires** these parameters:
- `from` - Start date (YYYY-MM-DD format)
- `to` - End date (YYYY-MM-DD format)

### Correct API Call for Last 7 Days

```php
// PHP/Laravel Example
$toDate = date('Y-m-d');  // Today
$fromDate = date('Y-m-d', strtotime('-7 days'));  // 7 days ago

$response = Http::withHeaders([
    'X-API-Key' => 'your-api-key-here'
])
->get('https://your-server:8000/api/invoices', [
    'from' => $fromDate,
    'to' => $toDate,
    'limit' => 100
]);
```

### Common Issues and Fixes

1. **403 Forbidden**
   - Your server IP is not whitelisted
   - Fix: Add the IP `13.247.230.43` to `ALLOWED_IPS` in the `.env` file
   
2. **401 Unauthorized**
   - Missing or wrong API key
   - Fix: Include `X-API-Key` header with the correct key

3. **422 Unprocessable Content**
   - Missing `from` and `to` parameters
   - Fix: Always include both date parameters

## Testing the Fix

1. **First, test locally on the server:**
   ```powershell
   $headers = @{"X-API-Key" = "your-api-key"}
   $fromDate = (Get-Date).AddDays(-7).ToString("yyyy-MM-dd")
   $toDate = (Get-Date).ToString("yyyy-MM-dd")
   
   Invoke-RestMethod -Uri "https://localhost:8000/api/invoices?from=$fromDate&to=$toDate&limit=10" -Headers $headers -Method Get
   ```

2. **Then test from your CRM server:**
   ```bash
   curl -X GET "https://your-server:8000/api/invoices?from=2025-06-08&to=2025-06-15&limit=10" \
     -H "X-API-Key: your-api-key" \
     -k
   ```

## Configuration Checklist

- [ ] API key is set in CRM configuration
- [ ] CRM server IP is in `ALLOWED_IPS` in the API's `.env` file
- [ ] Date parameters are being sent in YYYY-MM-DD format
- [ ] Both `from` and `to` dates are included in every request
- [ ] SSL certificate verification is handled (use `-k` flag or `verify=false`)

## Need More Help?

1. Check the enhanced logs at: `C:\PastelBridge\logs\pastel_bridge.log`
2. Run the test script: `python test_api_usage.py`
3. See full documentation: `API_USAGE_GUIDE.md` 