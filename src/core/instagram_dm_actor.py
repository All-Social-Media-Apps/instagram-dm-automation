"""
Core Instagram DMs Actor
Main orchestrator class that replicates Apify Instagram DMs Automation functionality
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Optional, Callable, Dict, Any
from selenium.webdriver.remote.webdriver import WebDriver

from models.input_schema import InputSchema
from models.output_schema import OutputSchema, MessageResult, MessageStatus
from auth.instagram_auth import InstagramAuthenticator
from messaging.dm_sender import DirectMessageSender
from messaging.rate_limiter import RateLimiter
from browser.webdriver_manager import WebDriverManager
from proxy.proxy_manager import ProxyManager
from utils.logger import get_logger
from utils.config import load_config

logger = get_logger(__name__)

class InstagramDMsActor:
    """
    Main actor class that orchestrates the Instagram DM automation process.
    Replicates the exact functionality of Apify Instagram DMs Automation actor.
    """
    
    def __init__(self, input_data: InputSchema, config: Dict[str, Any]):
        self.input = input_data
        self.config = config
        self.results: List[MessageResult] = []
        self.start_time = None
        self.end_time = None
        
        # Initialize components
        self.authenticator = InstagramAuthenticator(config)
        self.dm_sender = DirectMessageSender(config)
        self.rate_limiter = RateLimiter(
            max_per_hour=input_data.maxMessagesPerHour,
            max_per_day=input_data.maxMessagesPerDay,
            delay_between=input_data.delayBetweenMessages
        )
        self.webdriver_manager = WebDriverManager(config)
        self.proxy_manager = ProxyManager(input_data.proxyConfiguration, config)
        
        self.driver: Optional[WebDriver] = None
        self.session_valid = True
        
    async def run(self, progress_callback: Optional[Callable[[int], None]] = None) -> OutputSchema:
        """Execute the complete Instagram DM automation process."""
        self.start_time = datetime.now()
        logger.info(f"Starting Instagram DMs automation for {len(self.input.usernames)} users")
        
        try:
            # Step 1: Initialize browser and authentication (20% progress)
            if progress_callback:
                progress_callback(10)
            
            await self._initialize_browser()
            
            if progress_callback:
                progress_callback(20)
            
            # Step 2: Authenticate with Instagram (40% progress)
            auth_success = await self._authenticate()
            if not auth_success:
                return self._create_failure_output("Authentication failed")
            
            if progress_callback:
                progress_callback(40)
            
            # Step 3: Process messages (40-90% progress)
            await self._process_messages(progress_callback)
            
            # Step 4: Cleanup and finalize (90-100% progress)
            if progress_callback:
                progress_callback(90)
            
            await self._cleanup()
            
            if progress_callback:
                progress_callback(100)
            
            return self._create_success_output()
            
        except Exception as e:
            logger.error(f"Actor execution failed: {str(e)}")
            await self._cleanup()
            return self._create_failure_output(str(e))
    
    async def _initialize_browser(self):
        """Initialize browser with proxy and anti-detection settings."""
        logger.info("Initializing browser...")
        
        # Get proxy if configured
        proxy_config = None
        if self.input.proxyConfiguration:
            proxy_config = await self.proxy_manager.get_proxy()
        
        # Initialize webdriver
        self.driver = await self.webdriver_manager.create_driver(
            headless=self.input.headless,
            proxy_config=proxy_config,
            save_screenshots=self.input.saveScreenshots
        )
        
        logger.info("Browser initialized successfully")
    
    async def _authenticate(self) -> bool:
        """Authenticate with Instagram using session ID."""
        logger.info("Authenticating with Instagram...")
        
        try:
            # Set session cookies
            success = await self.authenticator.authenticate_with_session(
                self.driver, 
                self.input.sessionId
            )
            
            if success:
                logger.info("Instagram authentication successful")
                # Validate session is working
                self.session_valid = await self.authenticator.validate_session(self.driver)
                return self.session_valid
            else:
                logger.error("Instagram authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    async def _process_messages(self, progress_callback: Optional[Callable[[int], None]] = None):
        """Process all messages with rate limiting and error handling."""
        logger.info(f"Processing {len(self.input.usernames)} messages...")
        
        total_users = len(self.input.usernames)
        base_progress = 40  # Starting progress after authentication
        progress_range = 50  # Progress range for message processing (40-90%)
        
        for i, username in enumerate(self.input.usernames):
            # Update progress
            if progress_callback:
                current_progress = base_progress + int((i / total_users) * progress_range)
                progress_callback(current_progress)
            
            # Check if we should continue
            if not self._should_continue_processing():
                logger.warning("Stopping message processing due to rate limits or errors")
                break
            
            # Process single message
            result = await self._process_single_message(username, i + 1, total_users)
            self.results.append(result)
            
            # Apply delay between messages (except for the last one)
            if i < total_users - 1:
                delay = self.rate_limiter.get_next_delay()
                logger.info(f"Waiting {delay} seconds before next message...")
                await asyncio.sleep(delay)
    
    async def _process_single_message(self, username: str, current: int, total: int) -> MessageResult:
        """Process a single message with full error handling and retries."""
        start_time = time.time()
        logger.info(f"({current}/{total}) Processing message for @{username}")
        
        # Check rate limits
        if not self.rate_limiter.can_send_message():
            logger.warning(f"Rate limit exceeded for @{username}")
            return MessageResult(
                username=username,
                message=self.input.message,
                status=MessageStatus.RATE_LIMITED,
                success=False,
                timestamp=datetime.now(),
                error_message="Rate limit exceeded",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Test mode - don't send actual messages
        if self.input.testMode:
            logger.info(f"Test mode: Simulating message send to @{username}")
            await asyncio.sleep(2)  # Simulate processing time
            return MessageResult(
                username=username,
                message=self.input.message,
                status=MessageStatus.SUCCESS,
                success=True,
                timestamp=datetime.now(),
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Attempt to send message with retries
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Send the message
                success = await self.dm_sender.send_direct_message(
                    self.driver,
                    username,
                    self.input.message
                )
                
                if success:
                    self.rate_limiter.record_message_sent()
                    logger.info(f"✅ Message sent successfully to @{username}")
                    
                    return MessageResult(
                        username=username,
                        message=self.input.message,
                        status=MessageStatus.SUCCESS,
                        success=True,
                        timestamp=datetime.now(),
                        retry_count=attempt,
                        processing_time_ms=int((time.time() - start_time) * 1000)
                    )
                else:
                    last_error = "Message sending failed"
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} failed for @{username}: {last_error}")
                
                # Wait before retry
                if attempt < max_retries - 1:
                    await asyncio.sleep(5 * (attempt + 1))  # Exponential backoff
        
        # All attempts failed
        logger.error(f"❌ Failed to send message to @{username} after {max_retries} attempts")
        
        return MessageResult(
            username=username,
            message=self.input.message,
            status=MessageStatus.FAILED,
            success=False,
            timestamp=datetime.now(),
            error_message=last_error,
            retry_count=max_retries - 1,
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
    
    def _should_continue_processing(self) -> bool:
        """Check if we should continue processing messages."""
        # Check if session is still valid
        if not self.session_valid:
            logger.error("Instagram session is no longer valid")
            return False
        
        # Check if we've hit daily limits
        if not self.rate_limiter.can_send_message():
            logger.warning("Daily/hourly rate limits reached")
            return False
        
        return True
    
    async def _cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up resources...")
        
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing browser: {str(e)}")
    
    def _create_success_output(self) -> OutputSchema:
        """Create successful output schema."""
        self.end_time = datetime.now()
        runtime = (self.end_time - self.start_time).total_seconds()
        
        successful = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success and r.status != MessageStatus.SKIPPED)
        skipped = sum(1 for r in self.results if r.status == MessageStatus.SKIPPED)
        
        avg_processing_time = 0
        if self.results:
            avg_processing_time = sum(r.processing_time_ms for r in self.results) / len(self.results)
        
        return OutputSchema(
            success=True,
            total_attempted=len(self.results),
            successful_sends=successful,
            failed_sends=failed,
            skipped_sends=skipped,
            start_time=self.start_time,
            end_time=self.end_time,
            runtime_seconds=runtime,
            results=self.results,
            average_processing_time_ms=avg_processing_time,
            rate_limit_hits=self.rate_limiter.rate_limit_hits,
            session_valid=self.session_valid,
            messages_remaining_today=self.rate_limiter.get_remaining_daily_quota()
        )
    
    def _create_failure_output(self, error_message: str) -> OutputSchema:
        """Create failure output schema."""
        self.end_time = datetime.now()
        runtime = 0
        if self.start_time:
            runtime = (self.end_time - self.start_time).total_seconds()
        
        successful = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        
        return OutputSchema(
            success=False,
            total_attempted=len(self.results),
            successful_sends=successful,
            failed_sends=failed,
            skipped_sends=0,
            start_time=self.start_time or datetime.now(),
            end_time=self.end_time,
            runtime_seconds=runtime,
            results=self.results,
            error=error_message,
            average_processing_time_ms=0,
            rate_limit_hits=0,
            session_valid=False
        )
