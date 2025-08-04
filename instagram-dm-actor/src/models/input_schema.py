"""
Input validation schema
"""
from pydantic import BaseModel
from typing import List

class InputSchema(BaseModel):
    sessionId: str
    usernames: List[str]
    message: str
    testMode: bool = True
    delayBetweenMessages: int = 60
    maxRetries: int = 3 