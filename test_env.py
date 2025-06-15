import os
from pathlib import Path

print("=== Environment Debug ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {__file__}")

# Check multiple possible locations
locations = [
    ".env",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
    "C:\\PastelBridge\\.env",
    Path(__file__).parent / ".env"
]

for loc in locations:
    exists = os.path.exists(loc) if isinstance(loc, str) else loc.exists()
    print(f"\nChecking: {loc}")
    print(f"Exists: {exists}")
    
    if exists:
        try:
            with open(loc, 'r') as f:
                print("First few lines:")
                for i, line in enumerate(f):
                    if i < 5:
                        print(f"  {line.strip()}")
                    else:
                        break
        except Exception as e:
            print(f"Error reading: {e}")

# Try to load dotenv manually
try:
    from dotenv import load_dotenv
    
    # Try different methods
    result1 = load_dotenv()
    print(f"\nload_dotenv() result: {result1}")
    
    result2 = load_dotenv(dotenv_path=".env")
    print(f"load_dotenv('.env') result: {result2}")
    
    result3 = load_dotenv(dotenv_path="C:\\PastelBridge\\.env")
    print(f"load_dotenv with full path result: {result3}")
    
    # Check if variables are loaded
    import os
    print(f"\nDSN_NAME from env: {os.getenv('DSN_NAME')}")
    print(f"API_KEY from env: {os.getenv('API_KEY')}")
    
except ImportError:
    print("\npython-dotenv not installed")