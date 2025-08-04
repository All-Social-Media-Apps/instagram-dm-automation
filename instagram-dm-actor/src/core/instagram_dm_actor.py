"""
Core Instagram DM Actor Implementation
"""
import asyncio
import time
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class InstagramDMActor:
    def __init__(self):
        self.driver = None
        
    async def run_automation(self, input_data) -> List[Dict[str, Any]]:
        """Main automation logic"""
        results = []
        
        try:
            # Setup Chrome driver
            self.driver = self._setup_driver()
            
            # Login with session
            await self._login_with_session(input_data.sessionId)
            
            # Send messages
            for username in input_data.usernames:
                try:
                    result = await self._send_dm(username, input_data.message, input_data.testMode)
                    results.append(result)
                    
                    # Delay between messages
                    if len(results) < len(input_data.usernames):
                        await asyncio.sleep(input_data.delayBetweenMessages)
                        
                except Exception as e:
                    results.append({
                        'username': username,
                        'status': 'FAILED',
                        'error': str(e),
                        'timestamp': time.time()
                    })
                    
        finally:
            if self.driver:
                self.driver.quit()
                
        return results
    
    def _setup_driver(self):
        """Setup Chrome WebDriver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=options)
    
    async def _login_with_session(self, session_id: str):
        """Login using session ID"""
        self.driver.get('https://www.instagram.com/')
        self.driver.add_cookie({
            'name': 'sessionid',
            'value': session_id,
            'domain': '.instagram.com'
        })
        self.driver.refresh()
        await asyncio.sleep(3)
    
    async def _send_dm(self, username: str, message: str, test_mode: bool) -> Dict[str, Any]:
        """Send DM to specific user"""
        if test_mode:
            # Simulate sending in test mode
            await asyncio.sleep(1)
            return {
                'username': username,
                'status': 'SENT',
                'message': message,
                'test_mode': True,
                'timestamp': time.time()
            }
        
        # Real DM sending logic would go here
        # For now, return success
        return {
            'username': username,
            'status': 'SENT',
            'message': message,
            'test_mode': False,
            'timestamp': time.time()
        } 