"""Configuration module for ClickUp Task Creator.

This module contains:
- ClickUpTaskConfig dataclass for runtime configuration
- EmailPlatform enum for supported email systems
- CustomFieldType enum for ClickUp custom field types
- EmailContent dataclass for parsed email data
- EmailAnalysis dataclass for AI-extracted insights
- Custom field mapping definitions
- Constants for API endpoints and configuration
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class EmailPlatform(str, Enum):
    """Supported email platforms for content extraction."""
    
    GMAIL = "GMAIL"
    OUTLOOK = "OUTLOOK"


class CustomFieldType(str, Enum):
    """ClickUp custom field types."""
    
    TEXT = "TEXT"
    DATE = "DATE"
    DROPDOWN = "DROPDOWN"
    CHECKBOX = "CHECKBOX"
    NUMBER = "NUMBER"


@dataclass
class EmailContent:
    """Structured email content extracted from email URL."""
    
    subject: str
    body: str
    sender: str
    sender_email: str
    date: str
    attachments: list[str] = field(default_factory=list)
    raw_html: Optional[str] = None


@dataclass
class EmailAnalysis:
    """AI-generated analysis of email content."""
    
    title: str
    description: str
    priority: str
    due_date: Optional[str] = None
    key_points: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ClickUpTaskConfig:
    """Configuration for ClickUp task creation."""
    
    api_key: str
    workspace_name: str
    space_name: str
    list_name: str
    gemini_api_key: Optional[str] = None
    custom_field_mappings: dict = field(default_factory=dict)
    enable_ai_summary: bool = False
    email_platform: EmailPlatform = EmailPlatform.GMAIL
    interactive: bool = False


# API Configuration
CLICKUP_API_BASE_URL = "https://api.clickup.com/api/v2"

# API Endpoint Constants
API_ENDPOINT_TEAMS = "/team"
API_ENDPOINT_SPACES = "/team/{team_id}/space"
API_ENDPOINT_LISTS = "/space/{space_id}/list"
API_ENDPOINT_FIELDS = "/list/{list_id}/field"
API_ENDPOINT_TASKS = "/list/{list_id}/task"
API_ENDPOINT_TASK = "/task/{task_id}"

# Timeout and Retry Constants
API_TIMEOUT = 30  # seconds
MAX_RETRIES = 3  # Maximum number of retry attempts
DEFAULT_RETRY_AFTER = 60  # Default retry delay in seconds for rate limiting
EXPONENTIAL_BACKOFF_BASE = 2  # Base for exponential backoff calculation

# AI Configuration
AI_MAX_RETRIES = 3  # Maximum retries for AI API calls
AI_DEFAULT_RETRY_DELAY = 60  # Default retry delay for AI rate limiting

# Custom field mapping definitions (to be implemented)
CUSTOM_FIELD_MAPPINGS = {}
