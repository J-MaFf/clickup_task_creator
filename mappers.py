"""Field mapping and extraction utilities.

This module provides:
- Email field extraction functions
- Custom field mapping logic
- Type conversion utilities
- Data transformation helpers
- Rich prompt helpers for user input
"""

import logging
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from config import CustomFieldType, EmailContent

console = Console()
logger = logging.getLogger("clickup_task_creator")


def get_email_url_input() -> str:
    """Prompt user for email URL input.
    
    Returns:
        Email URL
    """
    console.print("\n[bold cyan]📧 Email URL Input[/bold cyan]")
    
    url = Prompt.ask(
        "[yellow]Enter the email URL[/yellow]",
        default=""
    )
    
    return url.strip()


def get_task_title_input(suggestion: str = "") -> str:
    """Prompt user for task title with optional suggestion.
    
    Args:
        suggestion: Suggested title (from AI or email subject)
    
    Returns:
        Task title
    """
    if suggestion:
        console.print(f"\n[dim]Suggested title: {suggestion}[/dim]")
        use_suggestion = Confirm.ask("Use this title?", default=True)
        
        if use_suggestion:
            return suggestion
    
    title = Prompt.ask("[yellow]Enter task title[/yellow]")
    return title.strip()


def get_confirmation_input(task_payload: dict) -> bool:
    """Show task preview and get user confirmation.
    
    Args:
        task_payload: Task data to preview
    
    Returns:
        True if user confirms, False otherwise
    """
    console.print("\n[bold cyan]📋 Task Preview[/bold cyan]")
    
    # Create preview table
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Title", task_payload.get("name", "N/A"))
    table.add_row("Description", task_payload.get("description", "N/A")[:100] + "...")
    
    # Show custom fields if present
    if "custom_fields" in task_payload:
        for field in task_payload["custom_fields"]:
            table.add_row(
                f"  {field.get('name', 'Unknown')}",
                str(field.get('value', 'N/A'))
            )
    
    console.print(table)
    console.print()
    
    return Confirm.ask("[yellow]Create this task?[/yellow]", default=True)


def extract_priority(email_content: EmailContent) -> str:
    """Extract priority level from email content.
    
    Args:
        email_content: Email content to analyze
    
    Returns:
        Priority level (Low, Normal, High, Urgent)
    """
    # TODO: Implement priority extraction logic
    # For now, return default
    return "Normal"


def extract_due_date(email_content: EmailContent) -> Optional[str]:
    """Extract due date from email content.
    
    Args:
        email_content: Email content to analyze
    
    Returns:
        Due date in YYYY-MM-DD format or None
    """
    # TODO: Implement due date extraction logic
    # For now, return None
    return None


def map_email_field(
    email_field: str,
    field_type: CustomFieldType,
    email_content: EmailContent
) -> Any:
    """Map email field to ClickUp custom field value.
    
    Args:
        email_field: Name of email field to extract
        field_type: Type of custom field
        email_content: Email content source
    
    Returns:
        Mapped field value
    """
    # TODO: Implement field mapping logic
    # For now, return None
    return None


def build_custom_field_value(value: Any, field_type: CustomFieldType) -> Any:
    """Convert value to appropriate type for custom field.
    
    Args:
        value: Raw value to convert
        field_type: Target custom field type
    
    Returns:
        Converted value
    """
    if field_type == CustomFieldType.TEXT:
        return str(value)
    elif field_type == CustomFieldType.NUMBER:
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    elif field_type == CustomFieldType.CHECKBOX:
        return bool(value)
    elif field_type == CustomFieldType.DATE:
        # TODO: Implement date conversion
        return value
    elif field_type == CustomFieldType.DROPDOWN:
        return str(value)
    
    return value
