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
    
    # Connection Pool
    max_connections: int = 3
    connection_timeout: int = 30
    
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