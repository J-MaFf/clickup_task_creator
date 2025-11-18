"""ClickUp Task Creator - Main entry point.

This module provides:
- CLI argument parsing
- Configuration assembly
- Authentication chain orchestration
- Main task creation workflow
- Rich console UI for user interaction
"""

import argparse
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from auth import load_clickup_api_key, load_gemini_api_key
from config import ClickUpTaskConfig, EmailPlatform
from logger_config import setup_logging
from task_creator import ClickUpTaskCreator, TaskCreationError
from version import __version__, __description__

console = Console()


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description=__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"ClickUp Task Creator v{__version__}"
    )
    
    # Email options
    parser.add_argument(
        "--email-url",
        type=str,
        help="Email URL to process"
    )
    
    parser.add_argument(
        "--email-platform",
        type=str,
        choices=["GMAIL", "OUTLOOK"],
        help="Email platform (auto-detected if not specified)"
    )
    
    # Authentication
    parser.add_argument(
        "--api-key",
        type=str,
        help="ClickUp API key"
    )
    
    parser.add_argument(
        "--gemini-api-key",
        type=str,
        help="Google Gemini API key for AI analysis"
    )
    
    # ClickUp workspace/space/list
    parser.add_argument(
        "--workspace",
        type=str,
        help="ClickUp workspace name"
    )
    
    parser.add_argument(
        "--space",
        type=str,
        help="ClickUp space name"
    )
    
    parser.add_argument(
        "--list",
        type=str,
        help="ClickUp list name"
    )
    
    # Features
    parser.add_argument(
        "--ai-summary",
        action="store_true",
        help="Enable AI email analysis"
    )
    
    parser.add_argument(
        "--no-ai-summary",
        action="store_true",
        help="Disable AI email analysis"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Show preview before creating task"
    )
    
    # Logging
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Optional log file path"
    )
    
    return parser.parse_args()


def show_welcome():
    """Display welcome banner."""
    welcome_text = """
[bold cyan]ClickUp Task Creator[/bold cyan] 📧➡️📋

Create ClickUp tasks directly from email URLs
with AI-powered field population.

Version: {version}
    """.format(version=__version__)
    
    console.print(Panel(welcome_text, border_style="cyan"))


def build_config(args: argparse.Namespace) -> ClickUpTaskConfig:
    """Build configuration from arguments and prompts.
    
    Args:
        args: Parsed command line arguments
    
    Returns:
        Complete configuration
    """
    console.print("\n[bold]🔧 Configuration[/bold]")
    
    # Load API keys
    clickup_api_key = load_clickup_api_key(args.api_key)
    
    # Determine if AI summary is enabled
    enable_ai = args.ai_summary
    if args.no_ai_summary:
        enable_ai = False
    elif not args.ai_summary:
        # Prompt user if not specified
        enable_ai = Confirm.ask(
            "[yellow]Enable AI email analysis?[/yellow]",
            default=True
        )
    
    # Load Gemini API key if AI is enabled
    gemini_api_key = None
    if enable_ai:
        gemini_api_key = load_gemini_api_key(args.gemini_api_key)
        if not gemini_api_key:
            console.print("[yellow]⚠ Gemini API key not available, AI analysis will be disabled[/yellow]")
            enable_ai = False
    
    # Get workspace/space/list (required)
    from rich.prompt import Prompt
    
    workspace_name = args.workspace or Prompt.ask("[yellow]Workspace name[/yellow]")
    space_name = args.space or Prompt.ask("[yellow]Space name[/yellow]")
    list_name = args.list or Prompt.ask("[yellow]List name[/yellow]")
    
    # Email platform
    email_platform = None
    if args.email_platform:
        email_platform = EmailPlatform(args.email_platform)
    
    return ClickUpTaskConfig(
        api_key=clickup_api_key,
        workspace_name=workspace_name,
        space_name=space_name,
        list_name=list_name,
        gemini_api_key=gemini_api_key,
        enable_ai_summary=enable_ai,
        email_platform=email_platform,
        interactive=args.interactive
    )


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = getattr(logging, args.log_level)
    setup_logging(level=log_level, log_file=args.log_file)
    
    logger = logging.getLogger("clickup_task_creator")
    logger.info(f"ClickUp Task Creator v{__version__} starting")
    
    try:
        # Show welcome
        show_welcome()
        
        # Build configuration
        config = build_config(args)
        
        # Get email URL
        email_url = args.email_url
        if not email_url:
            from mappers import get_email_url_input
            email_url = get_email_url_input()
        
        if not email_url:
            console.print("[red]❌ Email URL is required[/red]")
            sys.exit(1)
        
        # Create task
        console.print("\n[bold]🚀 Creating Task[/bold]")
        creator = ClickUpTaskCreator(config)
        
        # Interactive preview if enabled
        if config.interactive:
            console.print("[yellow]⚠ Interactive mode - preview will be shown before creation[/yellow]")
        
        # Create task
        task = creator.create_task_from_email(email_url)
        
        # Show success
        console.print(Panel(
            f"[green]✅ Task created successfully![/green]\n\n"
            f"Task ID: {task.get('id', 'N/A')}\n"
            f"Task URL: {task.get('url', 'N/A')}",
            title="Success",
            border_style="green"
        ))
        
        logger.info("Task creation completed successfully")
        
    except TaskCreationError as e:
        console.print(Panel(
            f"[red]❌ Task creation failed:[/red]\n{e}",
            title="Error",
            border_style="red"
        ))
        logger.error(f"Task creation error: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Operation cancelled by user[/yellow]")
        sys.exit(0)
    
    except Exception as e:
        console.print(Panel(
            f"[red]❌ Unexpected error:[/red]\n{e}",
            title="Error",
            border_style="red"
        ))
        logger.exception("Unexpected error")
        sys.exit(1)


if __name__ == "__main__":
    main()
