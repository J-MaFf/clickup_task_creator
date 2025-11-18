"""Tests for ai_summary module."""

import pytest
from unittest.mock import Mock, patch

from ai_summary import _basic_email_analysis, _parse_retry_delay
from config import EmailContent


def test_basic_email_analysis():
    """Test basic email analysis without AI."""
    email = EmailContent(
        subject="Test Email Subject",
        body="This is a test email body with some content.",
        sender="Test Sender",
        sender_email="test@example.com",
        date="2025-01-01"
    )
    
    analysis = _basic_email_analysis(email)
    
    assert analysis.title == "Test Email Subject"
    assert len(analysis.description) > 0
    assert analysis.priority == "Normal"
    assert analysis.confidence == 0.5


def test_parse_retry_delay():
    """Test parsing retry delay from error message."""
    error_msg = "Rate limit exceeded. Retry after 30 seconds"
    delay = _parse_retry_delay(error_msg)
    assert delay == 30


def test_parse_retry_delay_default():
    """Test default retry delay when not found in message."""
    error_msg = "Unknown error"
    delay = _parse_retry_delay(error_msg)
    assert delay == 60
