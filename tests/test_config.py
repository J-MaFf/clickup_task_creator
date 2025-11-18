"""Tests for config module."""

import pytest

from config import (
    AI_DEFAULT_RETRY_DELAY,
    AI_MAX_RETRIES,
    API_ENDPOINT_FIELDS,
    API_ENDPOINT_LISTS,
    API_ENDPOINT_SPACES,
    API_ENDPOINT_TASK,
    API_ENDPOINT_TASKS,
    API_ENDPOINT_TEAMS,
    API_TIMEOUT,
    CLICKUP_API_BASE_URL,
    ClickUpTaskConfig,
    CustomFieldType,
    DEFAULT_RETRY_AFTER,
    EmailAnalysis,
    EmailContent,
    EmailPlatform,
    EXPONENTIAL_BACKOFF_BASE,
    MAX_RETRIES,
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
    assert CustomFieldType.CHECKBOX == "CHECKBOX"
    assert CustomFieldType.NUMBER == "NUMBER"


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


def test_api_base_url_constant():
    """Test API base URL constant."""
    assert CLICKUP_API_BASE_URL == "https://api.clickup.com/api/v2"


def test_api_endpoint_constants():
    """Test API endpoint constants."""
    assert API_ENDPOINT_TEAMS == "/team"
    assert API_ENDPOINT_SPACES == "/team/{team_id}/space"
    assert API_ENDPOINT_LISTS == "/space/{space_id}/list"
    assert API_ENDPOINT_FIELDS == "/list/{list_id}/field"
    assert API_ENDPOINT_TASKS == "/list/{list_id}/task"
    assert API_ENDPOINT_TASK == "/task/{task_id}"


def test_timeout_and_retry_constants():
    """Test timeout and retry constants."""
    assert API_TIMEOUT == 30
    assert MAX_RETRIES == 3
    assert DEFAULT_RETRY_AFTER == 60
    assert EXPONENTIAL_BACKOFF_BASE == 2


def test_ai_configuration_constants():
    """Test AI configuration constants."""
    assert AI_MAX_RETRIES == 3
    assert AI_DEFAULT_RETRY_DELAY == 60
