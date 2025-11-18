"""Tests for config module."""

import pytest

from config import (
    ClickUpTaskConfig,
    CustomFieldType,
    EmailAnalysis,
    EmailContent,
    EmailPlatform,
)


def test_email_platform_enum():
    """Test EmailPlatform enum values."""
    assert EmailPlatform.GMAIL == "GMAIL"
    assert EmailPlatform.OUTLOOK == "OUTLOOK"


def test_custom_field_type_enum():
    """Test CustomFieldType enum values."""
    assert CustomFieldType.TEXT == "TEXT"
    assert CustomFieldType.DATE == "DATE"
    assert CustomFieldType.DROPDOWN == "DROPDOWN"


def test_email_content_dataclass():
    """Test EmailContent dataclass creation."""
    content = EmailContent(
        subject="Test Subject",
        body="Test Body",
        sender="Test Sender",
        sender_email="test@example.com",
        date="2025-01-01"
    )
    
    assert content.subject == "Test Subject"
    assert content.body == "Test Body"
    assert content.attachments == []


def test_email_analysis_dataclass():
    """Test EmailAnalysis dataclass creation."""
    analysis = EmailAnalysis(
        title="Test Task",
        description="Test Description",
        priority="High",
        due_date="2025-01-01",
        key_points=["Point 1", "Point 2"],
        confidence=0.9
    )
    
    assert analysis.title == "Test Task"
    assert analysis.priority == "High"
    assert len(analysis.key_points) == 2


def test_clickup_task_config():
    """Test ClickUpTaskConfig dataclass."""
    config = ClickUpTaskConfig(
        api_key="test_key",
        workspace_name="Test Workspace",
        space_name="Test Space",
        list_name="Test List"
    )
    
    assert config.api_key == "test_key"
    assert config.enable_ai_summary is False
    assert config.email_platform == EmailPlatform.GMAIL
