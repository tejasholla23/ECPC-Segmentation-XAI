"""
Utility functions for the ECPC-IDS Dashboard.
Includes validation, formatting, and data handling functions.
"""

import re
from typing import Any, Optional, Tuple
from config import MAX_PATIENT_ID_LENGTH, METRIC_DECIMAL_PLACES


def validate_patient_id(patient_id: str) -> Tuple[bool, str]:
    """
    Validate patient ID input.
    
    Args:
        patient_id (str): The patient ID to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - is_valid: True if valid, False otherwise
            - error_message: Empty string if valid, else error description
    """
    if not patient_id:
        return False, "Patient ID cannot be empty"
    
    if len(patient_id) > MAX_PATIENT_ID_LENGTH:
        return False, f"Patient ID exceeds maximum length of {MAX_PATIENT_ID_LENGTH} characters"
    
    # Allow alphanumeric characters, underscores, and hyphens
    if not re.match(r"^[a-zA-Z0-9_-]+$", patient_id):
        return False, "Patient ID can only contain alphanumeric characters, hyphens, and underscores"
    
    return True, ""


def format_metric_value(value: Optional[float], decimal_places: int = METRIC_DECIMAL_PLACES) -> str:
    """
    Format a metric value to a specified number of decimal places.
    Handles None and missing values safely.
    
    Args:
        value (Optional[float]): The metric value to format
        decimal_places (int): Number of decimal places to display
        
    Returns:
        str: Formatted value or placeholder text for empty values
    """
    if value is None:
        return "N/A"
    
    try:
        return f"{float(value):.{decimal_places}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_percentage(value: Optional[float], decimal_places: int = 2) -> str:
    """
    Format a value as a percentage.
    
    Args:
        value (Optional[float]): The value to format (should be 0-1 or 0-100)
        decimal_places (int): Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    if value is None:
        return "N/A"
    
    try:
        val = float(value)
        # Convert to 0-100 range if between 0-1
        if 0 <= val <= 1:
            val = val * 100
        return f"{val:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "N/A"


def safe_get_nested_value(data: dict, keys: list, default: Any = "N/A") -> Any:
    """
    Safely retrieve a nested value from a dictionary.
    
    Args:
        data (dict): The dictionary to search
        keys (list): List of keys to traverse (e.g., ['results', 'metrics', 'dice'])
        default (Any): Default value if key path not found
        
    Returns:
        Any: The nested value or default
    """
    if not isinstance(data, dict):
        return default
    
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def handle_missing_image(placeholder_text: str = "Image not available") -> str:
    """
    Create a placeholder message for missing images.
    
    Args:
        placeholder_text (str): Custom placeholder text
        
    Returns:
        str: Formatted placeholder message
    """
    return f"⚠️ {placeholder_text}"


def format_status_message(message: str, status_type: str = "info") -> str:
    """
    Format a status message with appropriate prefix and styling.
    
    Args:
        message (str): The message content
        status_type (str): Type of message ('success', 'error', 'warning', 'info')
        
    Returns:
        str: Formatted message with emoji prefix
    """
    prefixes = {
        "success": "✓",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️"
    }
    prefix = prefixes.get(status_type, "ℹ️")
    return f"{prefix} {message}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length with ellipsis.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text with ellipsis if needed
    """
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text
