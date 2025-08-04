"""
WebDriver Manager for browser automation
"""

import asyncio
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from utils.logger import get_logger

logger = get_logger(__name__)

class WebDriverManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def create_driver(self, headless: bool = True, proxy_config: Optional[Dict] = None, save_screenshots: bool = False) -> WebDriver:
        """Create and configure WebDriver instance."""
        logger.info("Creating WebDriver instance...")
        
        options = ChromeOptions()
        
        if headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add proxy if configured
        if proxy_config:
            proxy_url = f"{proxy_config['host']}:{proxy_config['port']}"
            options.add_argument(f'--proxy-server={proxy_url}')
        
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Execute script to hide automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("WebDriver created successfully")
        return driver
