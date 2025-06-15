import pyodbc
from contextlib import contextmanager
from threading import Semaphore, Event
import logging
from config import settings
import time

logger = logging.getLogger(__name__)

# Connection pool semaphore to limit concurrent connections
connection_semaphore = Semaphore(settings.max_connections)

# Circuit breaker state
class CircuitBreaker:
    def __init__(self):
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False
        
circuit_breaker = CircuitBreaker()

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
        # Check circuit breaker
        if circuit_breaker.is_open:
            if time.time() - circuit_breaker.last_failure_time < settings.circuit_breaker_recovery_timeout:
                raise Exception("Database circuit breaker is open - too many failures")
            else:
                # Try to close circuit breaker
                circuit_breaker.is_open = False
                circuit_breaker.failure_count = 0
        
        # Try to acquire connection with timeout
        acquired = connection_semaphore.acquire(timeout=settings.connection_acquire_timeout)
        if not acquired:
            logger.warning("Failed to acquire database connection within timeout")
            raise Exception("Database connection pool exhausted")
            
        conn = None
        start_time = time.time()
        try:
            conn = pyodbc.connect(self.connection_string)
            # Set query timeout
            # conn.timeout = settings.query_timeout_seconds  # Commented out - Pervasive SQL driver doesn't support this
            yield conn
            
            # Reset failure count on success
            circuit_breaker.failure_count = 0
            
        except pyodbc.Error as e:
            query_time = time.time() - start_time
            logger.error(f"Database error after {query_time:.2f}s: {e}")
            
            # Update circuit breaker
            circuit_breaker.failure_count += 1
            circuit_breaker.last_failure_time = time.time()
            
            if circuit_breaker.failure_count >= settings.circuit_breaker_failure_threshold:
                circuit_breaker.is_open = True
                logger.error("Opening database circuit breaker due to repeated failures")
                
            raise
        finally:
            if conn:
                conn.close()
            connection_semaphore.release()
            
            # Log if query took too long
            query_time = time.time() - start_time
            if query_time > settings.query_timeout_seconds:
                logger.warning(f"Query exceeded timeout threshold: {query_time:.2f}s")

db_pool = DatabasePool()