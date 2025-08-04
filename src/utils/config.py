"""
Configuration management for Instagram DMs Automation
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Logging configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'logs/instagram_dm.log')
        
        # Browser configuration
        self.HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'
        self.BROWSER_TYPE = os.getenv('BROWSER_TYPE', 'chrome')
        
        # Rate limiting
        self.DEFAULT_DELAY_SECONDS = int(os.getenv('DEFAULT_DELAY_SECONDS', '60'))
        self.MAX_DAILY_MESSAGES = int(os.getenv('MAX_DAILY_MESSAGES', '50'))
        self.MAX_HOURLY_MESSAGES = int(os.getenv('MAX_HOURLY_MESSAGES', '10'))

def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config()
