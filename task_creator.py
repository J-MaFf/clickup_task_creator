"""Task creation workflow and field mapping.

This module provides:
- ClickUpTaskCreator: Main orchestrator for task creation from emails
- TaskBuilder: Helper for constructing ClickUp task payloads
- Field validation and custom field mapping
- Integration with email extraction and AI analysis
"""

import logging
from typing import Optional

from api_client import ClickUpAPIClient
from config import ClickUpTaskConfig, EmailAnalysis, EmailContent
from email_client import create_email_client, detect_email_platform

logger = logging.getLogger("clickup_task_creator")


class TaskCreationError(Exception):
    """Raised when task creation fails."""
    pass


class ClickUpTaskCreator:
    """Orchestrator for creating ClickUp tasks from email URLs.
    
    Workflow:
    1. Parse email URL
    2. Extract email content
    3. Run AI analysis (optional)
    4. Build custom fields dict
    5. Validate task data
    6. Call ClickUp API to create task
    7. Return task details/link
    """
    
    def __init__(self, config: ClickUpTaskConfig):
        """Initialize task creator with configuration.
        
        Args:
            config: ClickUp task configuration
        """
        self.config = config
        self.api_client = ClickUpAPIClient(config.api_key)
    
    def create_task_from_email(self, email_url: str) -> dict:
        """Create ClickUp task from email URL.
        
        Args:
            email_url: URL of email to convert to task
        
        Returns:
            Created task data with ID, URL, etc.
        
        Raises:
            TaskCreationError: If task creation fails
        """
        logger.info(f"Creating task from email URL: {email_url}")
        
        # Step 1: Detect email platform
        if not self.config.email_platform:
            self.config.email_platform = detect_email_platform(email_url)
        
        # Step 2: Extract email content
        email_client = create_email_client(
            self.config.email_platform,
            api_key=None  # TODO: Support email API keys
        )
        email_content = email_client.extract_email(email_url)
        
        # Step 3: AI analysis (optional)
        email_analysis = None
        if self.config.enable_ai_summary and self.config.gemini_api_key:
            from ai_summary import analyze_email
            email_analysis = analyze_email(email_content, self.config.gemini_api_key)
        
        # Step 4: Build task payload
        task_builder = TaskBuilder(self.config)
        task_payload = task_builder.build_task_payload(email_content, email_analysis)
        
        # Step 5: Validate payload
        if not task_builder.validate_payload(task_payload):
            raise TaskCreationError("Invalid task payload")
        
        # Step 6: Get list ID
        list_id = self._get_list_id()
        
        # Step 7: Create task
        logger.info(f"Creating task in list {list_id}")
        created_task = self.api_client.create_task(list_id, task_payload)
        
        logger.info(f"Task created successfully: {created_task.get('id')}")
        return created_task
    
    def _get_list_id(self) -> str:
        """Get ClickUp list ID from workspace/space/list names.
        
        Returns:
            List ID
        
        Raises:
            TaskCreationError: If list cannot be found
        """
        # TODO: Implement list discovery
        # For now, raise not implemented
        raise NotImplementedError("List discovery not yet implemented")


class TaskBuilder:
    """Helper for constructing ClickUp task payloads.
    
    Handles:
    - Mapping email fields to ClickUp custom fields
    - Type conversions
    - Field validation
    """
    
    def __init__(self, config: ClickUpTaskConfig):
        """Initialize task builder with configuration.
        
        Args:
            config: ClickUp task configuration
        """
        self.config = config
    
    def build_task_payload(
        self,
        email_content: EmailContent,
        email_analysis: Optional[EmailAnalysis] = None
    ) -> dict:
        """Build ClickUp task payload from email data.
        
        Args:
            email_content: Extracted email content
            email_analysis: Optional AI analysis results
        
        Returns:
            Task payload dict ready for ClickUp API
        """
        logger.debug("Building task payload")
        
        # Use AI analysis if available, otherwise use email content
        if email_analysis:
            task_name = email_analysis.title
            task_description = email_analysis.description
        else:
            task_name = email_content.subject
            task_description = email_content.body[:500]  # Truncate body
        
        payload = {
            "name": task_name,
            "description": task_description,
            "markdown_description": task_description,
        }
        
        # Add custom fields if configured
        if self.config.custom_field_mappings:
            payload["custom_fields"] = self._build_custom_fields(
                email_content,
                email_analysis
            )
        
        logger.debug(f"Task payload built: {payload.get('name')}")
        return payload
    
    def _build_custom_fields(
        self,
        email_content: EmailContent,
        email_analysis: Optional[EmailAnalysis] = None
    ) -> list[dict]:
        """Build custom fields list from email data.
        
        Args:
            email_content: Extracted email content
            email_analysis: Optional AI analysis results
        
        Returns:
            List of custom field dicts
        """
        custom_fields = []
        
        # TODO: Implement custom field mapping logic
        # For now, return empty list
        
        return custom_fields
    
    def validate_payload(self, payload: dict) -> bool:
        """Validate task payload before submission.
        
        Args:
            payload: Task payload to validate
        
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if not payload.get("name"):
            logger.error("Task name is required")
            return False
        
        # Check name length
        if len(payload["name"]) > 500:
            logger.error("Task name too long (max 500 characters)")
            return False
        
        logger.debug("Task payload is valid")
        return True
