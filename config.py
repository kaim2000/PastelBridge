from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Explicitly load .env file BEFORE creating Settings
load_dotenv(override=True)

class Settings(BaseSettings):
    # Database
    dsn_name: str
    db_user: str = ""
    db_password: str = ""
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    
    # Security
    api_key: str
    allowed_ips: str = ""
    
    # Connection Pool - Following load reduction guidelines
    max_connections: int = 1  # Reduced from 3 to 1 per guidelines
    connection_timeout: int = 5  # Reduced from 30 to 5 seconds
    connection_acquire_timeout: float = 0.1  # 100ms to fail fast
    
    # Rate Limiting - Following load reduction guidelines  
    rate_limit_per_minute: int = 30  # Increased from 15 to 30 (above recommended 10-20 range)
    min_request_interval_ms: int = 500  # Minimum 500ms between requests
    
    # Pagination - Following load reduction guidelines
    max_page_size: int = 4500  # Temporarily increased for initial data load - reduce to 100-500 after
    default_page_size: int = 50  # Default page size
    
    # Circuit Breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 30
    query_timeout_seconds: int = 2  # Alert if queries exceed this
    
    # SSL - Optional strings
    ssl_cert_file: Optional[str] = ""
    ssl_key_file: Optional[str] = ""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }
        
    @property
    def allowed_ips_list(self):
        return [ip.strip() for ip in self.allowed_ips.split(',') if ip.strip()]

# Create settings instance
settings = Settings()