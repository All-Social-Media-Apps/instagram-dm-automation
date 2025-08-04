"""
Custom exceptions for Instagram DM Automation
"""


class InstagramDMError(Exception):
    """Base exception for Instagram DM automation errors"""
    pass


class AuthenticationError(InstagramDMError):
    """Raised when authentication fails"""
    pass


class SessionError(InstagramDMError):
    """Raised when session-related errors occur"""
    pass


class RateLimitError(InstagramDMError):
    """Raised when rate limits are exceeded"""
    pass


class ProxyError(InstagramDMError):
    """Raised when proxy-related errors occur"""
    pass


class BrowserError(InstagramDMError):
    """Raised when browser automation errors occur"""
    pass


class ValidationError(InstagramDMError):
    """Raised when input validation fails"""
    pass


class MessageSendError(InstagramDMError):
    """Raised when message sending fails"""
    pass


class UserNotFoundError(InstagramDMError):
    """Raised when target user is not found"""
    pass


class NetworkError(InstagramDMError):
    """Raised when network-related errors occur"""
    pass
