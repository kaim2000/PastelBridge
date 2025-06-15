import pyodbc
from config import settings
import logging
from datetime import datetime

# Set up logging
log_filename = f"table_structures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(message)s'
)

try:
    conn = pyodbc.connect(f"DSN={settings.dsn_name}")
    cursor = conn.cursor()
    
    logging.info("Connected successfully!\n")
    
    # Read table names from tablesindb.txt
    with open('tablesindb.txt', 'r') as f:
        tables = []
        for line in f:
            # Don't strip the line first - we need to check for the leading spaces
            if line.startswith('  - '):
                # Extract table name after "  - "
                table_name = line[4:].strip()
                if table_name:  # Only add non-empty table names
                    tables.append(table_name)
    
    logging.info(f"Found {len(tables)} tables to process\n")
    
    # Check structure of each table
    for table_name in tables:
        logging.info(f"\n{'='*50}")
        logging.info(f"Checking table: {table_name}")
        logging.info(f"{'='*50}")
        
        try:
            cursor.execute(f"SELECT TOP 1 * FROM {table_name}")
            columns = [column[0] for column in cursor.description]
            logging.info("Columns:")
            for col in columns:
                logging.info(f"  - {col}")
                
            # Show a sample row
            row = cursor.fetchone()
            if row:
                logging.info("\nSample data:")
                for i, col in enumerate(columns):
                    logging.info(f"  {col}: {row[i]}")
        except Exception as e:
            logging.error(f"Error accessing {table_name}: {e}")
    
    conn.close()
    logging.info("\nDatabase connection closed.")
    
except Exception as e:
    logging.error(f"Connection error: {e}")