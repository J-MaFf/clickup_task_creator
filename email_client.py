"""Email content extraction module.

This module provides:
- EmailClient protocol for structural typing
- Platform-specific email client implementations (Gmail, Outlook)
- Email URL parsing and content extraction
- Fallback strategies for email extraction
- Email metadata extraction (sender, subject, body, date, attachments)
"""

import logging
from typing import Protocol
from urllib.parse import parse_qs, urlparse

from config import EmailContent, EmailPlatform

logger = logging.getLogger("clickup_task_creator")


class EmailExtractionError(Exception):
    """Raised when email extraction fails."""
    pass


class EmailClient(Protocol):
    """Protocol for email content extraction.
    
    All email client implementations must implement these methods.
    """
    
    def extract_email(self, url: str) -> EmailContent:
        """Extract email content from URL.
        
        Args:
            url: Email URL to extract content from
        
        Returns:
            Extracted email content
        
        Raises:
            EmailExtractionError: If extraction fails
        """
        ...


class GmailClient:
    """Extract email content from Gmail URLs.
    
    Supports Gmail web interface URLs in format:
    https://mail.google.com/mail/u/0/#inbox/message_id
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gmail client.
        
        Args:
            api_key: Optional Gmail API key for authenticated access
        """
        self.api_key = api_key
    
    def extract_email(self, url: str) -> EmailContent:
        """Extract email content from Gmail URL.
        
        Args:
            url: Gmail email URL
        
        Returns:
            Extracted email content
        
        Raises:
            EmailExtractionError: If extraction fails
        """
        logger.info(f"Extracting email from Gmail URL: {url}")
        
        # Parse message ID from URL
        message_id = self._parse_message_id(url)
        if not message_id:
            raise EmailExtractionError("Could not parse message ID from Gmail URL")
        
        # TODO: Implement Gmail API or web scraping extraction
        # For now, return placeholder
        raise NotImplementedError("Gmail email extraction not yet implemented")
    
    def _parse_message_id(self, url: str) -> str:
        """Parse message ID from Gmail URL.
        
        Args:
            url: Gmail URL
        
        Returns:
            Message ID
        """
        # Gmail URLs: https://mail.google.com/mail/u/0/#inbox/message_id
        parsed = urlparse(url)
        fragment = parsed.fragment
        
        if "/" in fragment:
            parts = fragment.split("/")
            if len(parts) >= 2:
                return parts[-1]
        
        return ""


class OutlookClient:
    """Extract email content from Outlook URLs.
    
    Supports Outlook web interface URLs in format:
    https://outlook.office.com/mail/...
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Outlook client.
        
        Args:
            api_key: Optional Outlook API key for authenticated access
        """
        self.api_key = api_key
    
    def extract_email(self, url: str) -> EmailContent:
        """Extract email content from Outlook URL.
        
        Args:
            url: Outlook email URL
        
        Returns:
            Extracted email content
        
        Raises:
            EmailExtractionError: If extraction fails
        """
        logger.info(f"Extracting email from Outlook URL: {url}")
        
        # Parse message ID from URL
        message_id = self._parse_message_id(url)
        if not message_id:
            raise EmailExtractionError("Could not parse message ID from Outlook URL")
        
        # TODO: Implement Outlook API or web scraping extraction
        # For now, return placeholder
        raise NotImplementedError("Outlook email extraction not yet implemented")
    
    def _parse_message_id(self, url: str) -> str:
        """Parse message ID from Outlook URL.
        
        Args:
            url: Outlook URL
        
        Returns:
            Message ID
        """
        # Outlook URLs vary by format
        parsed = urlparse(url)
        # TODO: Implement proper Outlook URL parsing
        return ""


def create_email_client(platform: EmailPlatform, api_key: Optional[str] = None) -> EmailClient:
    """Factory function to create appropriate email client.
    
    Args:
        platform: Email platform type
        api_key: Optional API key for authenticated access
    
    Returns:
        Email client instance
    
    Raises:
        ValueError: If platform is not supported
    """
    if platform == EmailPlatform.GMAIL:
        return GmailClient(api_key=api_key)
    elif platform == EmailPlatform.OUTLOOK:
        return OutlookClient(api_key=api_key)
    else:
        raise ValueError(f"Unsupported email platform: {platform}")


def detect_email_platform(url: str) -> EmailPlatform:
    """Detect email platform from URL.
    
    Args:
        url: Email URL
    
    Returns:
        Detected email platform
    
    Raises:
        ValueError: If platform cannot be detected
    """
    url_lower = url.lower()
    
    if "mail.google.com" in url_lower or "gmail.com" in url_lower:
        return EmailPlatform.GMAIL
    elif "outlook.office.com" in url_lower or "outlook.com" in url_lower:
        return EmailPlatform.OUTLOOK
    else:
        raise ValueError(f"Could not detect email platform from URL: {url}")
