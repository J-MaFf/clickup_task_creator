"""Tests for auth module."""

import os
from unittest.mock import patch

import pytest

from auth import load_secret_with_fallback


def test_load_secret_from_cli():
    """Test loading secret from CLI argument."""
    result = load_secret_with_fallback(
        cli_value="cli_secret",
        env_var_name="TEST_ENV",
        onepassword_ref="op://test",
        secret_name="Test Secret",
        required=True
    )
    
    assert result == "cli_secret"


def test_load_secret_from_env():
    """Test loading secret from environment variable."""
    with patch.dict(os.environ, {"TEST_ENV": "env_secret"}):
        result = load_secret_with_fallback(
            cli_value=None,
            env_var_name="TEST_ENV",
            onepassword_ref="op://test",
            secret_name="Test Secret",
            required=True
        )
        
        assert result == "env_secret"


def test_load_secret_not_required():
    """Test loading optional secret."""
    result = load_secret_with_fallback(
        cli_value=None,
        env_var_name="NONEXISTENT_ENV",
        onepassword_ref="op://test",
        secret_name="Test Secret",
        required=False
    )
    
    assert result is None
