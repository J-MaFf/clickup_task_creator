"""Authentication module for ClickUp Task Creator.

This module handles API key retrieval with multiple fallback mechanisms:
1. CLI arguments
2. Environment variables
3. 1Password SDK
4. 1Password CLI
5. Manual prompt

Supports both ClickUp and Google Gemini API keys.
"""

import os
import subprocess
import logging
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt

console = Console()
logger = logging.getLogger("clickup_task_creator")


def load_secret_with_fallback(
    cli_value: Optional[str],
    env_var_name: str,
    onepassword_ref: str,
    secret_name: str,
    required: bool = True
) -> Optional[str]:
    """Load a secret with multiple fallback mechanisms.
    
    Args:
        cli_value: Value from CLI argument (highest priority)
        env_var_name: Environment variable name to check
        onepassword_ref: 1Password reference path
        secret_name: Human-readable name for prompts
        required: Whether the secret is required
    
    Returns:
        The secret value or None if not required and not found
    
    Raises:
        ValueError: If secret is required but not found
    """
    # Priority 1: CLI argument
    if cli_value:
        logger.debug(f"{secret_name} loaded from CLI argument")
        return cli_value
    
    # Priority 2: Environment variable
    env_value = os.getenv(env_var_name)
    if env_value:
        logger.debug(f"{secret_name} loaded from environment variable {env_var_name}")
        return env_value
    
    # Priority 3: 1Password SDK
    try:
        from onepassword import Client
        
        service_account_token = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
        if service_account_token:
            client = Client()
            secret = client.secrets.resolve(onepassword_ref)
            if secret:
                logger.debug(f"{secret_name} loaded from 1Password SDK")
                return secret
    except ImportError:
        logger.debug("1Password SDK not available")
    except Exception as e:
        logger.debug(f"1Password SDK failed: {e}")
    
    # Priority 4: 1Password CLI
    try:
        result = subprocess.run(
            ["op", "read", onepassword_ref],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            logger.debug(f"{secret_name} loaded from 1Password CLI")
            return result.stdout.strip()
    except FileNotFoundError:
        logger.debug("1Password CLI not available")
    except Exception as e:
        logger.debug(f"1Password CLI failed: {e}")
    
    # Priority 5: Manual prompt
    if required:
        console.print(f"[yellow]⚠ {secret_name} not found in CLI, environment, or 1Password[/yellow]")
        value = Prompt.ask(f"Please enter {secret_name}", password=True)
        if value:
            return value
        raise ValueError(f"{secret_name} is required but not provided")
    
    return None


def load_clickup_api_key(cli_value: Optional[str] = None) -> str:
    """Load ClickUp API key with fallback chain.
    
    Args:
        cli_value: Optional API key from CLI argument
    
    Returns:
        ClickUp API key
    
    Raises:
        ValueError: If API key cannot be found
    """
    return load_secret_with_fallback(
        cli_value=cli_value,
        env_var_name="CLICKUP_API_KEY",
        onepassword_ref="op://Home Server/ClickUp personal API token/credential",
        secret_name="ClickUp API Key",
        required=True
    )


def load_gemini_api_key(cli_value: Optional[str] = None) -> Optional[str]:
    """Load Google Gemini API key with fallback chain.
    
    Args:
        cli_value: Optional API key from CLI argument
    
    Returns:
        Gemini API key or None if not available
    """
    return load_secret_with_fallback(
        cli_value=cli_value,
        env_var_name="GEMINI_API_KEY",
        onepassword_ref="op://Home Server/nftoo3gsi3wpx7z5bdmcsvr7p4/credential",
        secret_name="Google Gemini API Key",
        required=False
    )
