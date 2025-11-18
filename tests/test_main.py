"""Tests for main module."""

import pytest
from unittest.mock import patch

from main import parse_arguments


def test_parse_arguments_defaults():
    """Test parsing arguments with defaults."""
    with patch("sys.argv", ["main.py"]):
        args = parse_arguments()
        
        assert args.log_level == "INFO"
        assert args.interactive is False
        assert args.ai_summary is False


def test_parse_arguments_with_options():
    """Test parsing arguments with options."""
    with patch("sys.argv", [
        "main.py",
        "--email-url", "https://mail.google.com/test",
        "--api-key", "test_key",
        "--workspace", "Test",
        "--interactive"
    ]):
        args = parse_arguments()
        
        assert args.email_url == "https://mail.google.com/test"
        assert args.api_key == "test_key"
        assert args.workspace == "Test"
        assert args.interactive is True
