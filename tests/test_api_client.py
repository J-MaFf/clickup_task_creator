"""Tests for api_client module."""

import pytest
import requests
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


@patch("api_client.time.sleep")
@patch("api_client.requests.Session.request")
def test_connection_error_raises_api_error(mock_request, mock_sleep):
    """Test that a failure before any response exists raises APIError."""
    mock_request.side_effect = requests.exceptions.ConnectionError("no route to host")

    client = ClickUpAPIClient(api_key="test_key")

    with pytest.raises(APIError, match="API request failed"):
        client.get("/team")


@patch("api_client.time.sleep")
@patch("api_client.requests.Session.request")
def test_connection_error_after_server_error_does_not_reuse_response(mock_request, mock_sleep):
    """Test that a connection error does not retry based on a prior attempt's status."""
    server_error = Mock()
    server_error.status_code = 503
    server_error.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "503 Server Error"
    )

    mock_request.side_effect = [
        server_error,
        requests.exceptions.ConnectionError("connection reset"),
    ]

    client = ClickUpAPIClient(api_key="test_key")

    with pytest.raises(APIError, match="API request failed"):
        client.get("/team")

    # The 503 is retried; the connection error that follows is not
    assert mock_request.call_count == 2
