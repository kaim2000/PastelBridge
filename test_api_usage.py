"""
Pastel Bridge API Test Script
============================
This script demonstrates proper API usage and helps diagnose common issues.
"""

import requests
import json
from datetime import datetime, timedelta
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings()

# Configuration - Update these values
API_BASE_URL = "https://localhost:8000"  # Update with your server address
API_KEY = "your-api-key-here"  # Update with your actual API key

def test_connection():
    """Test basic API connectivity"""
    print("\n1. Testing API Connection...")
    print("-" * 50)
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/ping",
            headers=headers,
            verify=False,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Connection successful!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        elif response.status_code == 401:
            print("✗ Invalid API key")
            print("  Fix: Check your API key in the X-API-Key header")
        elif response.status_code == 403:
            print("✗ IP address not whitelisted")
            print("  Fix: Add your IP to ALLOWED_IPS in the API's .env file")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed")
        print("  Possible causes:")
        print("  - Service not running (check: nssm status PastelBridgeAPI)")
        print("  - Wrong URL or port")
        print("  - Firewall blocking connection")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_invoice_missing_params():
    """Test invoice endpoint without required parameters"""
    print("\n2. Testing Invoice Endpoint (Missing Parameters)...")
    print("-" * 50)
    
    headers = {"X-API-Key": API_KEY}
    
    # Test with missing parameters
    response = requests.get(
        f"{API_BASE_URL}/api/invoices",
        headers=headers,
        params={"limit": 1},  # Missing required 'from' and 'to' dates
        verify=False
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 422:
        print("✓ Correctly rejected - missing required parameters")
        print(f"Error details: {json.dumps(response.json(), indent=2)}")
        print("\nRequired parameters: 'from' and 'to' dates in YYYY-MM-DD format")
    else:
        print(f"Unexpected response: {response.text}")

def test_invoice_last_7_days():
    """Test retrieving invoices for the last 7 days"""
    print("\n3. Testing Invoice Retrieval (Last 7 Days)...")
    print("-" * 50)
    
    headers = {"X-API-Key": API_KEY}
    
    # Calculate date range
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"Date range: {from_date} to {to_date}")
    
    params = {
        "from": from_date,
        "to": to_date,
        "limit": 100
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/invoices",
            headers=headers,
            params=params,
            verify=False,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            invoices = response.json()
            print(f"✓ Success! Retrieved {len(invoices)} invoices")
            
            if invoices:
                print("\nFirst 5 invoices:")
                for i, invoice in enumerate(invoices[:5]):
                    print(f"  {i+1}. {invoice['document_number']} - {invoice['document_date']} - {invoice['account_code']}")
            else:
                print("\nNo invoices found in this date range")
                print("Possible reasons:")
                print("  - No data in Pastel for this period")
                print("  - Date format issue")
                print("  - Database connection issue")
                
        elif response.status_code == 500:
            print("✗ Server error")
            print(f"Error: {response.json()}")
            print("\nPossible causes:")
            print("  - Database connection issue")
            print("  - Invalid table/column names in query")
            print("  - Check logs: C:\\PastelBridge\\logs\\service.log")
            
    except Exception as e:
        print(f"✗ Error: {e}")

def test_invoice_date_range():
    """Test different date ranges"""
    print("\n4. Testing Different Date Ranges...")
    print("-" * 50)
    
    headers = {"X-API-Key": API_KEY}
    
    test_ranges = [
        ("Today", 0, 0),
        ("Yesterday", 1, 1),
        ("Last 30 days", 30, 0),
        ("Last 90 days", 90, 0),
    ]
    
    for name, days_ago_start, days_ago_end in test_ranges:
        from_date = (datetime.now() - timedelta(days=days_ago_start)).strftime('%Y-%m-%d')
        to_date = (datetime.now() - timedelta(days=days_ago_end)).strftime('%Y-%m-%d')
        
        params = {
            "from": from_date,
            "to": to_date,
            "limit": 10
        }
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/invoices",
                headers=headers,
                params=params,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                count = len(response.json())
                print(f"✓ {name} ({from_date} to {to_date}): {count} invoices")
            else:
                print(f"✗ {name}: Error {response.status_code}")
                
        except Exception as e:
            print(f"✗ {name}: Connection error")

def test_rate_limiting():
    """Test rate limiting behavior"""
    print("\n5. Testing Rate Limiting...")
    print("-" * 50)
    
    headers = {"X-API-Key": API_KEY}
    
    print("Sending 5 rapid requests...")
    
    for i in range(5):
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/ping",
                headers=headers,
                verify=False,
                timeout=5
            )
            
            if response.status_code == 429:
                print(f"  Request {i+1}: Rate limited (429)")
                break
            else:
                print(f"  Request {i+1}: {response.status_code}")
                
        except Exception as e:
            print(f"  Request {i+1}: Error")
    
    print("\nRate limit: 60 requests per minute per IP")

def display_curl_examples():
    """Display curl command examples"""
    print("\n6. Curl Command Examples")
    print("-" * 50)
    
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    print("Test connection:")
    print(f'curl -X GET "{API_BASE_URL}/api/ping" \\')
    print(f'  -H "X-API-Key: {API_KEY}" \\')
    print('  -k\n')
    
    print("Get last 7 days invoices:")
    print(f'curl -X GET "{API_BASE_URL}/api/invoices?from={from_date}&to={to_date}&limit=100" \\')
    print(f'  -H "X-API-Key: {API_KEY}" \\')
    print('  -k')

def main():
    """Run all tests"""
    print("=" * 60)
    print("Pastel Bridge API Test Suite")
    print("=" * 60)
    print(f"API URL: {API_BASE_URL}")
    print(f"API Key: {'*' * 20}...{API_KEY[-4:]}" if len(API_KEY) > 4 else "NOT SET")
    
    if API_KEY == "your-api-key-here":
        print("\n⚠️  WARNING: Please update API_KEY with your actual API key!")
        return
    
    # Run tests
    test_connection()
    test_invoice_missing_params()
    test_invoice_last_7_days()
    test_invoice_date_range()
    test_rate_limiting()
    display_curl_examples()
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("\nFor more details, check the API logs:")
    print("  - Service log: C:\\PastelBridge\\logs\\service.log")
    print("  - Error log: C:\\PastelBridge\\logs\\service-error.log")
    print("  - API log: C:\\PastelBridge\\logs\\pastel_bridge.log")

if __name__ == "__main__":
    main() 