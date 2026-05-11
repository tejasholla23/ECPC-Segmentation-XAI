"""
Utility functions for the ECPC-IDS Dashboard.
Includes validation, formatting, and data handling functions.
"""

import base64
import io
import os
import re
from typing import Any, Optional, Tuple

import numpy as np
import requests
from PIL import Image, ImageOps

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


def decode_base64_image(data: str) -> bytes:
    """
    Decode a base64 image string to raw bytes.
    """
    if "," in data:
        data = data.split(",", 1)[1]
    data = re.sub(r"\s+", "", data)
    padding = -len(data) % 4
    if padding:
        data += "=" * padding
    return base64.b64decode(data)


def create_placeholder_image(
    target_size: Tuple[int, int] = (400, 400),
    error: bool = False,
    text: Optional[str] = None
) -> np.ndarray:
    """
    Create a simple placeholder image for missing or invalid image data.
    """
    width, height = target_size
    background = np.ones((height, width, 3), dtype=np.uint8) * (220 if not error else 200)
    tint = np.array([80, 120, 180], dtype=np.uint8) if not error else np.array([180, 60, 60], dtype=np.uint8)
    stripe = np.indices((height, width))[0] // 20 % 2 == 0
    background[stripe] = np.clip(background[stripe] + tint, 0, 255)
    return background


def _is_base64_string(data: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9+/=\s]+", data)) and len(data) > 100


def _pil_to_numpy(image: Image.Image, target_size: Tuple[int, int]) -> np.ndarray:
    image = image.convert("RGB")
    image = image.resize(target_size, Image.LANCZOS)
    return np.asarray(image, dtype=np.uint8)


def load_image_safe(
    image_data: Any,
    target_size: Tuple[int, int] = (400, 400),
    as_rgb: bool = True
) -> np.ndarray:
    """
    Load and normalize an image from a variety of inputs.

    Supports local file paths, URLs, base64 strings, bytes, PIL images,
    and numpy arrays.
    """
    if image_data is None:
        return create_placeholder_image(target_size=target_size, error=False)

    try:
        if isinstance(image_data, np.ndarray):
            array = image_data
            if array.ndim == 2:
                array = np.stack([array] * 3, axis=-1)
            if array.dtype != np.uint8:
                array = np.clip(array, 0, 255).astype(np.uint8)
            image = Image.fromarray(array)
        elif isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, Image.Image):
            image = image_data
        elif isinstance(image_data, str):
            source = image_data.strip()
            if source.startswith("http://") or source.startswith("https://"):
                response = requests.get(source, timeout=10)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
            elif source.startswith("data:image/") or _is_base64_string(source):
                image_bytes = decode_base64_image(source)
                image = Image.open(io.BytesIO(image_bytes))
            elif os.path.exists(source):
                image = Image.open(source)
            else:
                return create_placeholder_image(target_size=target_size, error=True)
        else:
            return create_placeholder_image(target_size=target_size, error=True)

        if not as_rgb and image.mode in ("L", "I", "F"):
            image = image.convert("L")
        elif as_rgb:
            if image.mode != "RGB":
                image = image.convert("RGB")

        image = image.resize(target_size, Image.LANCZOS)
        return np.asarray(image, dtype=np.uint8)

    except Exception:
        return create_placeholder_image(target_size=target_size, error=True)


def load_mask_safe(
    mask_data: Any,
    target_size: Tuple[int, int] = (400, 400)
) -> Optional[np.ndarray]:
    """
    Load a segmentation mask or mask-like image and convert it to a binary mask.
    """
    raw = load_image_safe(mask_data, target_size=target_size, as_rgb=False)
    if raw is None or raw.size == 0:
        return None

    if raw.ndim == 3:
        raw = np.mean(raw, axis=2)

    if raw.max() == 0:
        return None

    threshold = max(1, raw.max() * 0.15)
    return (raw >= threshold).astype(np.uint8)


def create_mask_visual(
    mask: Optional[np.ndarray],
    target_size: Tuple[int, int] = (400, 400),
    color: Tuple[int, int, int] = (0, 220, 120),
    background_gray: int = 40
) -> np.ndarray:
    """
    Render a binary mask as a visually distinct RGB image.
    """
    if mask is None:
        return create_placeholder_image(target_size=target_size, error=False)

    if mask.ndim == 3:
        mask = np.mean(mask, axis=2)
    mask = (mask > 0).astype(np.uint8)

    height, width = target_size[1], target_size[0]
    base = np.ones((height, width, 3), dtype=np.uint8) * background_gray
    overlay = np.zeros_like(base)
    overlay[mask == 1] = color
    alpha = 0.45
    blended = np.asarray(base * (1 - alpha) + overlay * alpha, dtype=np.uint8)
    return blended


def overlay_mask(
    base_image: np.ndarray,
    mask: Optional[np.ndarray],
    color: Tuple[int, int, int] = (0, 255, 0),
    alpha: float = 0.35
) -> np.ndarray:
    """
    Overlay a segmentation mask onto a base image.
    """
    if mask is None or base_image is None:
        return create_placeholder_image(target_size=(base_image.shape[1], base_image.shape[0]))

    if mask.ndim == 3:
        mask = np.mean(mask, axis=2)
    mask_bool = mask > 0
    color_layer = np.zeros_like(base_image, dtype=np.uint8)
    color_layer[..., 0] = color[0]
    color_layer[..., 1] = color[1]
    color_layer[..., 2] = color[2]

    base = base_image.astype(np.float32)
    alpha_layer = np.expand_dims(mask_bool.astype(np.float32) * alpha, axis=-1)
    blended = base * (1 - alpha_layer) + color_layer.astype(np.float32) * alpha_layer
    return np.clip(blended, 0, 255).astype(np.uint8)


def overlay_heatmap(
    base_image: np.ndarray,
    heatmap_data: Any,
    target_size: Tuple[int, int] = (400, 400),
    alpha: float = 0.55
) -> np.ndarray:
    """
    Blend a heatmap onto a CT image using a medically clear colormap.
    """
    base = load_image_safe(base_image, target_size=target_size, as_rgb=True)
    if base is None:
        return create_placeholder_image(target_size=target_size, error=True)

    heatmap = load_image_safe(heatmap_data, target_size=target_size, as_rgb=False)
    if heatmap is None:
        return create_placeholder_image(target_size=target_size, error=True)

    if heatmap.ndim == 3:
        heatmap = np.mean(heatmap, axis=2)

    heatmap = heatmap.astype(np.float32)
    heatmap -= heatmap.min()
    if heatmap.max() > 0:
        heatmap /= heatmap.max()

    colormap = np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)
    colormap[..., 0] = np.clip(255 * heatmap, 0, 255).astype(np.uint8)
    colormap[..., 1] = np.clip(80 + 120 * (1 - heatmap), 0, 255).astype(np.uint8)
    colormap[..., 2] = np.clip(220 * (1 - heatmap), 0, 255).astype(np.uint8)

    alpha_layer = np.expand_dims(heatmap * alpha, axis=-1)
    base_float = base.astype(np.float32)
    blended = base_float * (1 - alpha_layer) + colormap.astype(np.float32) * alpha_layer
    return np.clip(blended, 0, 255).astype(np.uint8)


def resize_image(
    image: np.ndarray,
    target_size: Tuple[int, int] = (400, 400),
    preserve_aspect_ratio: bool = True
) -> np.ndarray:
    """
    Resize an image to the target size while preserving aspect ratio with padding.
    """
    if image is None:
        return create_placeholder_image(target_size=target_size)

    if image.ndim == 2:
        image = np.stack([image] * 3, axis=-1)
    pil_image = Image.fromarray(image.astype(np.uint8))

    if preserve_aspect_ratio:
        pil_image.thumbnail(target_size, Image.LANCZOS)
        background = Image.new("RGB", target_size, (30, 30, 30))
        offset = ((target_size[0] - pil_image.width) // 2, (target_size[1] - pil_image.height) // 2)
        background.paste(pil_image, offset)
        result = background
    else:
        result = pil_image.resize(target_size, Image.LANCZOS)

    return np.asarray(result, dtype=np.uint8)
