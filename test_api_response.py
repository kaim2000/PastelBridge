import requests
import json
from datetime import datetime

def test_api_response():
    """Test the API response for customer AFR002"""
    
    # API endpoint
    url = "http://localhost:8000/customers/AFR002"
    
    print("=" * 80)
    print(f"Testing API response at {datetime.now()}")
    print(f"URL: {url}")
    print("=" * 80)
    
    try:
        # Make the API request
        response = requests.get(url)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            
            print("\nAPI Response (formatted):")
            print(json.dumps(data, indent=2))
            
            # Check for specific fields
            print("\n" + "=" * 80)
            print("Field Analysis:")
            print("=" * 80)
            
            # Check balance fields
            balance_fields = [f"balance_this_{i:02d}" for i in range(1, 14)]
            balance_fields += [f"balance_last_{i:02d}" for i in range(1, 14)]
            
            print("\nBalance Fields:")
            for field in balance_fields:
                value = data.get(field, "FIELD NOT FOUND")
                print(f"  {field}: {value}")
            
            # Check sales fields
            sales_fields = [f"sales_this_{i:02d}" for i in range(1, 14)]
            sales_fields += [f"sales_last_{i:02d}" for i in range(1, 14)]
            
            print("\nSales Fields:")
            for field in sales_fields:
                value = data.get(field, "FIELD NOT FOUND")
                print(f"  {field}: {value}")
            
            # Check postal address fields
            address_fields = [f"post_address_{i:02d}" for i in range(1, 6)]
            
            print("\nPostal Address Fields:")
            for field in address_fields:
                value = data.get(field, "FIELD NOT FOUND")
                print(f"  {field}: {value}")
                
            # Save full response to file
            output_file = f"api_response_AFR002_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n✓ Full API response saved to: {output_file}")
            
        else:
            print(f"\n✗ API returned error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to API. Is the service running?")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_response() 