"""ClickUp API client for task creation and management.

This module provides an enhanced API client with:
- GET, POST, PUT request support
- Custom field schema retrieval
- List and space discovery
- Error handling and retry logic
- Rate limit handling
- 30-second timeout for all requests
"""

import logging
import time
from typing import Any, Optional
from urllib.parse import urljoin

import requests

from config import CLICKUP_API_BASE_URL, API_TIMEOUT

logger = logging.getLogger("clickup_task_creator")


class APIError(Exception):
    """Base exception for API errors."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    pass


class ClickUpAPIClient:
    """Client for interacting with ClickUp API v2.
    
    Supports GET, POST, PUT operations with automatic retry logic
    and comprehensive error handling.
    """
    
    def __init__(self, api_key: str, base_url: str = CLICKUP_API_BASE_URL):
        """Initialize ClickUp API client.
        
        Args:
            api_key: ClickUp API authentication token
            base_url: Base URL for ClickUp API (default: v2 endpoint)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": api_key,
            "Content-Type": "application/json"
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        retries: int = 3
    ) -> Any:
        """Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            retries: Number of retries for transient failures
        
        Returns:
            Response JSON data
        
        Raises:
            APIError: On API errors
            RateLimitError: On rate limit exceeded
        """
        url = urljoin(self.base_url, endpoint)
        
        for attempt in range(retries):
            try:
                logger.debug(f"{method} {url} (attempt {attempt + 1}/{retries})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    timeout=API_TIMEOUT
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limit exceeded, retrying after {retry_after}s")
                    
                    if attempt < retries - 1:
                        time.sleep(retry_after)
                        continue
                    raise RateLimitError(f"Rate limit exceeded: {response.text}")
                
                # Handle other errors
                response.raise_for_status()
                
                return response.json() if response.content else {}
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise APIError(f"Request timeout after {retries} attempts")
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt < retries - 1 and response.status_code >= 500:
                    time.sleep(2 ** attempt)
                    continue
                raise APIError(f"API request failed: {e}")
        
        raise APIError(f"Request failed after {retries} attempts")
    
    def get(self, endpoint: str, params: Optional[dict] = None) -> Any:
        """Make GET request to ClickUp API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
        
        Returns:
            Response JSON data
        """
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: dict) -> Any:
        """Make POST request to ClickUp API.
        
        Args:
            endpoint: API endpoint path
            data: Request body data
        
        Returns:
            Response JSON data
        """
        return self._request("POST", endpoint, data=data)
    
    def put(self, endpoint: str, data: dict) -> Any:
        """Make PUT request to ClickUp API.
        
        Args:
            endpoint: API endpoint path
            data: Request body data
        
        Returns:
            Response JSON data
        """
        return self._request("PUT", endpoint, data=data)
    
    def get_workspaces(self) -> list[dict]:
        """Get all workspaces (teams) for the authenticated user.
        
        Returns:
            List of workspace dictionaries
        """
        response = self.get("/team")
        return response.get("teams", [])
    
    def get_spaces(self, team_id: str) -> list[dict]:
        """Get all spaces in a workspace.
        
        Args:
            team_id: Workspace/team ID
        
        Returns:
            List of space dictionaries
        """
        response = self.get(f"/team/{team_id}/space")
        return response.get("spaces", [])
    
    def get_lists(self, space_id: str) -> list[dict]:
        """Get all lists in a space.
        
        Args:
            space_id: Space ID
        
        Returns:
            List of list dictionaries
        """
        response = self.get(f"/space/{space_id}/list")
        return response.get("lists", [])
    
    def get_custom_fields(self, list_id: str) -> list[dict]:
        """Get custom field schema for a list.
        
        Args:
            list_id: List ID
        
        Returns:
            List of custom field definitions
        """
        response = self.get(f"/list/{list_id}/field")
        return response.get("fields", [])
    
    def create_task(self, list_id: str, task_data: dict) -> dict:
        """Create a new task in a list.
        
        Args:
            list_id: Target list ID
            task_data: Task payload with name, description, custom fields, etc.
        
        Returns:
            Created task data including ID and URL
        """
        return self.post(f"/list/{list_id}/task", task_data)
