#!/usr/bin/env python3
"""
Test script to query customers and show their fields including addresses
"""

import pyodbc
from config import settings
import logging
from datetime import datetime

# Set up logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_customer_query():
    """Query customers and show their available fields"""
    try:
        # Connect to database
        conn = pyodbc.connect(f"DSN={settings.dsn_name}")
        cursor = conn.cursor()
        
        logger.info("Connected to database successfully!")
        
        # First, let's see all columns in CustomerMaster table
        logger.info("\n" + "="*60)
        logger.info("Checking CustomerMaster table structure:")
        logger.info("="*60)
        
        # Get column information
        cursor.execute("""
            SELECT * FROM CustomerMaster LIMIT 1
        """)
        
        columns = [column[0] for column in cursor.description]
        logger.info(f"\nTotal columns found: {len(columns)}")
        logger.info("\nAll available columns:")
        for col in columns:
            logger.info(f"  - {col}")
        
        # Look for address-related columns
        logger.info("\n" + "="*60)
        logger.info("Address-related columns:")
        logger.info("="*60)
        address_columns = [col for col in columns if any(word in col.lower() for word in ['address', 'postal', 'street', 'city', 'state', 'zip', 'country'])]
        for col in address_columns:
            logger.info(f"  - {col}")
        
        # Now query 10 customers with key fields including address
        logger.info("\n" + "="*60)
        logger.info("Querying 10 customers with key fields:")
        logger.info("="*60)
        
        # Construct query with available address fields
        query_fields = ['CustomerCode', 'CustomerDesc']
        
        # Add address fields if they exist
        if 'PostAddress01' in columns:
            query_fields.append('PostAddress01')
        elif 'PostalAddress1' in columns:
            query_fields.append('PostalAddress1')
        elif 'Address1' in columns:
            query_fields.append('Address1')
            
        # Add other potential address fields
        for field in ['PostAddress02', 'PostAddress03', 'PostAddress04', 'PostAddress05']:
            if field in columns:
                query_fields.append(field)
        
        # Build and execute query
        field_list = ', '.join(query_fields)
        query = f"""
            SELECT {field_list}
            FROM CustomerMaster
            ORDER BY CustomerCode
            LIMIT 10
        """
        
        logger.info(f"\nExecuting query:\n{query}")
        cursor.execute(query)
        
        # Display results
        customers = cursor.fetchall()
        logger.info(f"\nRetrieved {len(customers)} customers:")
        
        for i, customer in enumerate(customers, 1):
            logger.info(f"\nCustomer #{i}:")
            for j, field in enumerate(query_fields):
                value = customer[j]
                # Truncate long values for display
                if value and isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                logger.info(f"  {field}: {value}")
        
        # Close connection
        cursor.close()
        conn.close()
        logger.info("\n" + "="*60)
        logger.info("Database connection closed successfully!")
        
    except Exception as e:
        logger.error(f"Error occurred: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    logger.info("Starting customer query test...")
    test_customer_query()
    logger.info("\nTest completed!") 