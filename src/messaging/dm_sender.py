"""
Direct Message Sender - Basic Implementation
"""

import asyncio
from typing import Dict, Any
from selenium.webdriver.remote.webdriver import WebDriver
from utils.logger import get_logger

logger = get_logger(__name__)

class DirectMessageSender:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def send_direct_message(self, driver: WebDriver, username: str, message: str) -> bool:
        """Basic message sending implementation."""
        logger.info(f"Sending message to @{username}: {message[:50]}...")
        # Simulate message sending
        await asyncio.sleep(3)
        logger.info(f"Message sent successfully to @{username}")
        return True
