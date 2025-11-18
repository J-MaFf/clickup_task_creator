"""Logging configuration for ClickUp Task Creator.

This module sets up Rich-enhanced logging with:
- Colorful console output
- Optional file logging
- Debug/Info/Error levels
- Rich tracebacks for better error debugging
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    use_rich: bool = True
) -> logging.Logger:
    """Set up logging with Rich console handler and optional file handler.
    
    Args:
        level: Logging level (logging.DEBUG, logging.INFO, etc.)
        log_file: Optional path to log file for persistent logging
        use_rich: Whether to use Rich formatting (default: True)
    
    Returns:
        Configured logger instance
    """
    # Install Rich tracebacks for better error messages
    if use_rich:
        install(show_locals=True)
    
    # Create logger
    logger = logging.getLogger("clickup_task_creator")
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler with Rich formatting
    if use_rich:
        console_handler = RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=True,
            show_level=True,
            show_path=True
        )
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
    
    console_handler.setLevel(level)
    logger.addHandler(console_handler)
    
    # File handler if log_file is specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
    
    return logger
