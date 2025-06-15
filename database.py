import pyodbc
from contextlib import contextmanager
from threading import Semaphore
import logging
from config import settings

logger = logging.getLogger(__name__)

# Connection pool semaphore to limit concurrent connections
connection_semaphore = Semaphore(settings.max_connections)

class DatabasePool:
    def __init__(self):
        self.connection_string = self._build_connection_string()
        
    def _build_connection_string(self):
        base = f"DSN={settings.dsn_name}"
        if settings.db_user:
            base += f";UID={settings.db_user}"
        if settings.db_password:
            base += f";PWD={settings.db_password}"
        base += f";Timeout={settings.connection_timeout}"
        return base
    
    @contextmanager
    def get_connection(self):
        with connection_semaphore:
            conn = None
            try:
                conn = pyodbc.connect(self.connection_string)
                yield conn
            except pyodbc.Error as e:
                logger.error(f"Database error: {e}")
                raise
            finally:
                if conn:
                    conn.close()

db_pool = DatabasePool()