"""Google Gemini AI integration for email analysis.

This module provides:
- Email analysis using Google Gemini AI
- Structured JSON output parsing
- Retry logic for rate limiting
- Graceful fallback when AI is unavailable
- EmailAnalysis dataclass with title, description, priority, due date, key points
"""

import json
import logging
import time
from typing import Optional

from config import EmailAnalysis, EmailContent

logger = logging.getLogger("clickup_task_creator")


class AIAnalysisError(Exception):
    """Raised when AI analysis fails."""
    pass


def analyze_email(
    email_content: EmailContent,
    gemini_api_key: str,
    max_retries: int = 3
) -> EmailAnalysis:
    """Analyze email content using Google Gemini AI.
    
    Args:
        email_content: Email content to analyze
        gemini_api_key: Google Gemini API key
        max_retries: Maximum number of retries for rate limiting
    
    Returns:
        Structured email analysis with title, description, priority, etc.
    
    Raises:
        AIAnalysisError: If analysis fails after retries
    """
    logger.info("Analyzing email content with Google Gemini AI")
    
    try:
        import google.generativeai as genai
    except ImportError:
        logger.warning("google-generativeai package not installed, falling back to basic extraction")
        return _basic_email_analysis(email_content)
    
    # Configure Gemini
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    
    # Build analysis prompt
    prompt = _build_analysis_prompt(email_content)
    
    # Retry loop for rate limiting
    for attempt in range(max_retries):
        try:
            logger.debug(f"Sending analysis request to Gemini (attempt {attempt + 1}/{max_retries})")
            
            response = model.generate_content(prompt)
            
            # Parse JSON response
            analysis = _parse_gemini_response(response.text)
            
            logger.info("Email analysis completed successfully")
            return analysis
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle rate limiting (429)
            if "429" in error_msg or "rate limit" in error_msg.lower():
                if attempt < max_retries - 1:
                    # Parse retry delay from error message if available
                    retry_delay = _parse_retry_delay(error_msg)
                    logger.warning(f"Rate limit hit, retrying after {retry_delay}s")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error("Rate limit exceeded, max retries reached")
                    return _basic_email_analysis(email_content)
            
            # Other errors
            logger.error(f"Gemini analysis failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                logger.warning("Falling back to basic email analysis")
                return _basic_email_analysis(email_content)
    
    # Fallback if all retries failed
    return _basic_email_analysis(email_content)


def _build_analysis_prompt(email_content: EmailContent) -> str:
    """Build analysis prompt for Gemini.
    
    Args:
        email_content: Email content to analyze
    
    Returns:
        Formatted prompt string
    """
    prompt = f"""Analyze this email and extract task information.

Email Subject: {email_content.subject}
Email From: {email_content.sender}
Email Date: {email_content.date}
Email Body:
{email_content.body}

Please extract:
1. A concise task title (5-10 words)
2. Task description (1-2 sentences summarizing the action needed)
3. Priority level (Low, Normal, High, or Urgent)
4. Due date (if mentioned in the email, format as YYYY-MM-DD)
5. Key action items or points (3-5 bullet points)

Return ONLY valid JSON in this exact format:
{{
    "title": "Task title here",
    "description": "Brief description here",
    "priority": "Normal",
    "due_date": "2025-01-01",
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "confidence": 0.85
}}
"""
    return prompt


def _parse_gemini_response(response_text: str) -> EmailAnalysis:
    """Parse Gemini JSON response into EmailAnalysis.
    
    Args:
        response_text: Raw response text from Gemini
    
    Returns:
        Parsed EmailAnalysis object
    
    Raises:
        AIAnalysisError: If response cannot be parsed
    """
    try:
        # Extract JSON from response (may have markdown code blocks)
        json_text = response_text.strip()
        if json_text.startswith("```json"):
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif json_text.startswith("```"):
            json_text = json_text.split("```")[1].split("```")[0].strip()
        
        data = json.loads(json_text)
        
        return EmailAnalysis(
            title=data.get("title", "Email Task"),
            description=data.get("description", ""),
            priority=data.get("priority", "Normal"),
            due_date=data.get("due_date"),
            key_points=data.get("key_points", []),
            confidence=data.get("confidence", 0.0)
        )
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse Gemini response: {e}")
        raise AIAnalysisError(f"Invalid response format: {e}")


def _parse_retry_delay(error_msg: str) -> int:
    """Parse retry delay from error message.
    
    Args:
        error_msg: Error message potentially containing retry delay
    
    Returns:
        Retry delay in seconds (default: 60)
    """
    # Try to extract retry delay from error message
    # Example: "Retry after 30 seconds"
    import re
    
    match = re.search(r"retry.*?(\d+)", error_msg, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    return 60  # Default retry delay


def _basic_email_analysis(email_content: EmailContent) -> EmailAnalysis:
    """Fallback basic email analysis without AI.
    
    Args:
        email_content: Email content to analyze
    
    Returns:
        Basic EmailAnalysis with extracted fields
    """
    logger.info("Using basic email analysis (AI unavailable)")
    
    # Use subject as title, truncate if too long
    title = email_content.subject[:100] if email_content.subject else "Email Task"
    
    # Use first few lines of body as description
    description_lines = email_content.body.split("\n")[:3]
    description = " ".join(line.strip() for line in description_lines if line.strip())
    if len(description) > 200:
        description = description[:197] + "..."
    
    return EmailAnalysis(
        title=title,
        description=description,
        priority="Normal",
        due_date=None,
        key_points=[],
        confidence=0.5
    )
