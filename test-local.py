import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"  # Changed from https to http
API_KEY = "cc522a73-5a85-40f8-802d-02ba6560caf5"  # Replace with your actual API key

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_health():
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/ping", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_invoices():
    print("\nTesting invoices endpoint...")
    
    # Get last 7 days of invoices
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    params = {
        "from": from_date,
        "to": to_date
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/invoices", 
            headers=headers, 
            params=params
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            invoices = response.json()
            print(f"Found {len(invoices)} invoices")
            
            # Show first invoice as sample
            if invoices:
                print("\nFirst invoice:")
                print(json.dumps(invoices[0], indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Pastel Bridge API...\n")
    
    if test_health():
        print("\n✓ Health check passed!")
        test_invoices()
    else:
        print("\n✗ Health check failed!")