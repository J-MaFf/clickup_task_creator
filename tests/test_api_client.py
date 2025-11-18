"""Tests for api_client module."""

import pytest
from unittest.mock import Mock, patch

from api_client import ClickUpAPIClient, APIError, RateLimitError


def test_api_client_initialization():
    """Test ClickUp API client initialization."""
    client = ClickUpAPIClient(api_key="test_key")
    
    assert client.api_key == "test_key"
    assert "Authorization" in client.session.headers


@patch("api_client.requests.Session.request")
def test_get_request(mock_request):
    """Test GET request."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_request.return_value = mock_response
    
    client = ClickUpAPIClient(api_key="test_key")
    result = client.get("/test")
    
    assert result == {"data": "test"}
    mock_request.assert_called_once()


@patch("api_client.requests.Session.request")
def test_post_request(mock_request):
    """Test POST request."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "123"}
    mock_request.return_value = mock_response
    
    client = ClickUpAPIClient(api_key="test_key")
    result = client.post("/test", {"name": "test"})
    
    assert result == {"id": "123"}
