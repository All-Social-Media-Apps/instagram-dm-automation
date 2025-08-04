"""
Output schema for Instagram DMs Automation
Defines the structure of automation results and individual message results
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageStatus(str, Enum):
    """Status of individual message sending attempt."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    RATE_LIMITED = "RATE_LIMITED"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    BLOCKED = "BLOCKED"

class MessageResult(BaseModel):
    """Result of sending a message to a specific user."""
    username: str = Field(..., description="Target username")
    message: str = Field(..., description="Message content that was sent")
    status: MessageStatus = Field(..., description="Status of the message sending attempt")
    success: bool = Field(..., description="Whether the message was sent successfully")
    timestamp: datetime = Field(..., description="When the message was processed")
    error_message: Optional[str] = Field(None, description="Error message if sending failed")
    retry_count: int = Field(default=0, description="Number of retry attempts made")
    processing_time_ms: int = Field(..., description="Time taken to process this message in milliseconds")

class OutputSchema(BaseModel):
    """
    Complete output schema for Instagram DMs Automation.
    Contains summary statistics and detailed results for each message.
    """
    
    # Overall execution results
    success: bool = Field(..., description="Whether the overall automation run was successful")
    total_attempted: int = Field(..., description="Total number of messages attempted")
    successful_sends: int = Field(..., description="Number of messages sent successfully")
    failed_sends: int = Field(..., description="Number of messages that failed to send")
    skipped_sends: int = Field(default=0, description="Number of messages skipped (e.g., due to rate limits)")
    
    # Timing information
    start_time: datetime = Field(..., description="When the automation started")
    end_time: datetime = Field(..., description="When the automation completed")
    runtime_seconds: float = Field(..., description="Total runtime in seconds")
    
    # Detailed results
    results: List[MessageResult] = Field(default_factory=list, description="Detailed results for each message")
    
    # Error information
    error: Optional[str] = Field(None, description="Overall error message if automation failed")
    warnings: List[str] = Field(default_factory=list, description="Any warnings generated during execution")
    
    # Performance statistics
    average_processing_time_ms: float = Field(..., description="Average time to process each message")
    rate_limit_hits: int = Field(default=0, description="Number of times rate limits were encountered")
    
    # Session information
    session_valid: bool = Field(..., description="Whether the Instagram session was valid")
    messages_remaining_today: Optional[int] = Field(None, description="Estimated messages remaining for today")
    
    def add_result(self, result: MessageResult):
        """Add a message result to the output."""
        self.results.append(result)
        
        if result.success:
            self.successful_sends += 1
        else:
            self.failed_sends += 1
            
        self.total_attempted += 1
        
        # Update average processing time
        if self.results:
            total_time = sum(r.processing_time_ms for r in self.results)
            self.average_processing_time_ms = total_time / len(self.results)
    
    def finalize(self, end_time: datetime):
        """Finalize the output schema with end time and calculated values."""
        self.end_time = end_time
        self.runtime_seconds = (self.end_time - self.start_time).total_seconds()
        
        # Determine overall success
        self.success = (self.failed_sends == 0 and self.total_attempted > 0)
        
        # Calculate final statistics
        if self.results:
            total_time = sum(r.processing_time_ms for r in self.results)
            self.average_processing_time_ms = total_time / len(self.results)
        else:
            self.average_processing_time_ms = 0.0

    def get_summary_dict(self) -> Dict[str, Any]:
        """Get a summary dictionary for quick overview."""
        return {
            "success": self.success,
            "total_attempted": self.total_attempted,
            "successful_sends": self.successful_sends,
            "failed_sends": self.failed_sends,
            "runtime_seconds": self.runtime_seconds,
            "average_processing_time_ms": self.average_processing_time_ms,
            "session_valid": self.session_valid
        }
