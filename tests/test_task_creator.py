"""Tests for task_creator module."""

import pytest
from unittest.mock import Mock

from config import ClickUpTaskConfig, EmailContent
from task_creator import TaskBuilder


def test_task_builder_initialization():
    """Test TaskBuilder initialization."""
    config = ClickUpTaskConfig(
        api_key="test_key",
        workspace_name="Test",
        space_name="Test",
        list_name="Test"
    )
    
    builder = TaskBuilder(config)
    assert builder.config == config


def test_build_task_payload():
    """Test building task payload."""
    config = ClickUpTaskConfig(
        api_key="test_key",
        workspace_name="Test",
        space_name="Test",
        list_name="Test"
    )
    
    email = EmailContent(
        subject="Test Subject",
        body="Test Body",
        sender="Test Sender",
        sender_email="test@example.com",
        date="2025-01-01"
    )
    
    builder = TaskBuilder(config)
    payload = builder.build_task_payload(email)
    
    assert payload["name"] == "Test Subject"
    assert "description" in payload


def test_validate_payload_valid():
    """Test validating valid payload."""
    config = ClickUpTaskConfig(
        api_key="test_key",
        workspace_name="Test",
        space_name="Test",
        list_name="Test"
    )
    
    builder = TaskBuilder(config)
    payload = {"name": "Test Task", "description": "Test"}
    
    assert builder.validate_payload(payload) is True


def test_validate_payload_missing_name():
    """Test validating payload with missing name."""
    config = ClickUpTaskConfig(
        api_key="test_key",
        workspace_name="Test",
        space_name="Test",
        list_name="Test"
    )
    
    builder = TaskBuilder(config)
    payload = {"description": "Test"}
    
    assert builder.validate_payload(payload) is False
