"""Tests for email_client module."""

import pytest

from config import EmailPlatform
from email_client import (
    GmailClient,
    OutlookClient,
    create_email_client,
    detect_email_platform,
)


def test_detect_gmail_platform():
    """Test detecting Gmail platform from URL."""
    url = "https://mail.google.com/mail/u/0/#inbox/12345"
    platform = detect_email_platform(url)
    assert platform == EmailPlatform.GMAIL


def test_detect_outlook_platform():
    """Test detecting Outlook platform from URL."""
    url = "https://outlook.office.com/mail/inbox/12345"
    platform = detect_email_platform(url)
    assert platform == EmailPlatform.OUTLOOK


def test_create_gmail_client():
    """Test creating Gmail client."""
    client = create_email_client(EmailPlatform.GMAIL)
    assert isinstance(client, GmailClient)


def test_create_outlook_client():
    """Test creating Outlook client."""
    client = create_email_client(EmailPlatform.OUTLOOK)
    assert isinstance(client, OutlookClient)


def test_gmail_parse_message_id():
    """Test parsing Gmail message ID from URL."""
    client = GmailClient()
    url = "https://mail.google.com/mail/u/0/#inbox/12345abcdef"
    message_id = client._parse_message_id(url)
    assert message_id == "12345abcdef"
