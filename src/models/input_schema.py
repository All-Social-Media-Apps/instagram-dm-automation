"""
Input schema for Instagram DMs Automation
Replicates the exact input format of Apify Instagram DMs Automation actor
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class ProxyConfiguration(BaseModel):
    """Proxy configuration schema matching Apify format."""
    useApifyProxy: Optional[bool] = Field(False, description="Use Apify proxy")
    apifyProxyGroups: Optional[List[str]] = Field(None, description="Apify proxy groups")
    proxyUrls: Optional[List[str]] = Field(None, description="Custom proxy URLs")

class InputSchema(BaseModel):
    """
    Input schema for Instagram DMs Automation.
    Matches the exact format expected by Apify Instagram DMs Automation actor.
    """
    
    # Required fields
    sessionId: str = Field(..., description="Instagram session ID for authentication")
    usernames: List[str] = Field(..., description="List of Instagram usernames to send messages to")
    message: str = Field(..., description="Message content to send")
    
    # Rate limiting
    delayBetweenMessages: int = Field(default=60, ge=10, le=300, description="Delay between messages in seconds")
    maxMessagesPerHour: int = Field(default=10, ge=1, le=50, description="Maximum messages per hour")
    maxMessagesPerDay: int = Field(default=50, ge=1, le=200, description="Maximum messages per day")
    
    # Browser configuration
    headless: bool = Field(default=True, description="Run browser in headless mode")
    saveScreenshots: bool = Field(default=False, description="Save screenshots during execution")
    
    # Proxy configuration
    proxyConfiguration: Optional[ProxyConfiguration] = Field(None, description="Proxy configuration")
    
    # Testing and debugging
    testMode: bool = Field(default=False, description="Run in test mode (no actual messages sent)")
    debugMode: bool = Field(default=False, description="Enable debug logging")
    
    # Advanced options
    maxRetries: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts per message")
    timeoutSeconds: int = Field(default=30, ge=10, le=120, description="Timeout for each operation")
    
    @validator('usernames')
    def validate_usernames(cls, v):
        """Validate usernames list."""
        if not v or len(v) == 0:
            raise ValueError("At least one username is required")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_usernames = []
        for username in v:
            username = username.strip().replace('@', '')  # Remove @ if present
            if username and username not in seen:
                seen.add(username)
                unique_usernames.append(username)
        
        if not unique_usernames:
            raise ValueError("No valid usernames provided")
            
        return unique_usernames
    
    @validator('message')
    def validate_message(cls, v):
        """Validate message content."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        
        if len(v) > 1000:
            raise ValueError("Message content cannot exceed 1000 characters")
            
        return v.strip()
    
    @validator('sessionId')
    def validate_session_id(cls, v):
        """Validate session ID format."""
        if not v or not v.strip():
            raise ValueError("Session ID is required")
            
        # Basic validation - session ID should be non-empty string
        if len(v.strip()) < 10:
            raise ValueError("Session ID appears to be invalid (too short)")
            
        return v.strip()

def validate_input(input_data: Dict[str, Any]) -> InputSchema:
    """
    Validate input data against the schema.
    
    Args:
        input_data: Raw input dictionary
        
    Returns:
        InputSchema: Validated input object
        
    Raises:
        ValidationError: If input data is invalid
    """
    try:
        return InputSchema(**input_data)
    except Exception as e:
        raise ValueError(f"Input validation failed: {str(e)}")
