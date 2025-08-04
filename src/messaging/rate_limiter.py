"""
Rate Limiter for Instagram DM sending
"""

import time
from datetime import datetime, timedelta
from typing import List

class RateLimiter:
    def __init__(self, max_per_hour: int = 10, max_per_day: int = 50, delay_between: int = 60):
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.delay_between = delay_between
        self.sent_times: List[datetime] = []
        self.rate_limit_hits = 0
    
    def can_send_message(self) -> bool:
        """Check if we can send a message based on rate limits."""
        now = datetime.now()
        
        # Clean old entries
        self.sent_times = [t for t in self.sent_times if now - t < timedelta(days=1)]
        
        # Check daily limit
        if len(self.sent_times) >= self.max_per_day:
            return False
        
        # Check hourly limit
        recent_sends = [t for t in self.sent_times if now - t < timedelta(hours=1)]
        if len(recent_sends) >= self.max_per_hour:
            return False
        
        return True
    
    def record_message_sent(self):
        """Record that a message was sent."""
        self.sent_times.append(datetime.now())
    
    def get_next_delay(self) -> int:
        """Get delay before next message."""
        return self.delay_between
    
    def get_remaining_daily_quota(self) -> int:
        """Get remaining daily message quota."""
        return max(0, self.max_per_day - len(self.sent_times))
