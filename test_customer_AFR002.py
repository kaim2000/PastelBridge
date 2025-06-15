import pyodbc
from config import settings
from datetime import datetime
import json

def test_customer_AFR002():
    """Test reading customer code AFR002 from CustomerMaster table"""
    
    print("=" * 80)
    print(f"Testing CustomerMaster table read at {datetime.now()}")
    print("=" * 80)
    
    try:
        # Connect to database
        conn_string = f"DSN={settings.dsn_name}"
        if settings.db_user:
            conn_string += f";UID={settings.db_user}"
        if settings.db_password:
            conn_string += f";PWD={settings.db_password}"
            
        print(f"\nConnecting to database with DSN: {settings.dsn_name}")
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()
        print("✓ Connected successfully!")
        
        # Query for customer AFR002
        query = "SELECT * FROM CustomerMaster WHERE CustomerCode = ?"
        print(f"\nExecuting query: {query}")
        print(f"Parameter: 'AFR002'")
        
        cursor.execute(query, 'AFR002')
        
        # Get column names
        columns = [column[0] for column in cursor.description]
        print(f"\n✓ Query executed successfully!")
        print(f"Number of columns: {len(columns)}")
        
        # Fetch the result
        row = cursor.fetchone()
        
        if row:
            print(f"\n✓ Found customer AFR002!")
            print("\n" + "=" * 80)
            print("CUSTOMER DATA:")
            print("=" * 80)
            
            # Display all fields with their values
            for i, column_name in enumerate(columns):
                value = row[i]
                # Format dates and None values nicely
                if value is None:
                    display_value = "NULL"
                elif isinstance(value, datetime):
                    display_value = value.strftime("%Y-%m-%d %H:%M:%S")
                elif hasattr(value, 'date') and callable(getattr(value, 'date')):
                    display_value = value.strftime("%Y-%m-%d")
                else:
                    display_value = str(value)
                    
                print(f"{column_name:30s}: {display_value}")
            
            # Also save to a JSON file for easier review
            print("\n" + "=" * 80)
            
            # Convert row to dictionary
            row_dict = {}
            for i, column_name in enumerate(columns):
                value = row[i]
                if value is None:
                    row_dict[column_name] = None
                elif isinstance(value, datetime):
                    row_dict[column_name] = value.strftime("%Y-%m-%d %H:%M:%S")
                elif hasattr(value, 'date') and callable(getattr(value, 'date')):
                    row_dict[column_name] = value.strftime("%Y-%m-%d")
                else:
                    row_dict[column_name] = str(value)
            
            # Save to JSON file
            output_file = f"customer_AFR002_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(row_dict, f, indent=2)
            
            print(f"✓ Data also saved to: {output_file}")
            
        else:
            print("\n✗ No customer found with code 'AFR002'")
            
            # Let's check if there are any customers at all
            print("\nChecking if CustomerMaster table has any data...")
            cursor.execute("SELECT COUNT(*) FROM CustomerMaster")
            count = cursor.fetchone()[0]
            print(f"Total customers in table: {count}")
            
            if count > 0:
                # Show some sample customer codes
                print("\nSample customer codes in the table:")
                cursor.execute("SELECT TOP 10 CustomerCode FROM CustomerMaster ORDER BY CustomerCode")
                for row in cursor.fetchall():
                    print(f"  - {row[0]}")
        
        cursor.close()
        conn.close()
        print("\n✓ Database connection closed.")
        
    except pyodbc.Error as e:
        print(f"\n✗ Database error: {e}")
        if hasattr(e, 'args'):
            for arg in e.args:
                print(f"  Details: {arg}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_customer_AFR002() 