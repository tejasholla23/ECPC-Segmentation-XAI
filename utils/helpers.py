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


def interpret_dice_score(dice: float) -> Tuple[str, str]:
    """Interpret Dice score and return assessment + color code."""
    if dice >= 0.85: return "Excellent Agreement", "#10b981"
    if dice >= 0.70: return "Clinically Acceptable", "#3b82f6"
    if dice >= 0.50: return "Fair / Requires Review", "#f59e0b"
    return "Low Reliability", "#ef4444"

def interpret_confidence(conf: float) -> Tuple[str, str]:
    """Interpret model confidence."""
    if conf >= 0.90: return "High Confidence", "#10b981"
    if conf >= 0.75: return "Stable Prediction", "#3b82f6"
    if conf >= 0.50: return "Moderate Uncertainty", "#f59e0b"
    return "Low Confidence / Manual Audit Required", "#ef4444"

def interpret_lesion_volume(volume: float) -> str:
    """Interpret lesion volume burden."""
    if volume > 5000: return "Significant lesion burden detected (>5000 mm³)."
    if volume > 1000: return "Moderate lesion burden detected."
    if volume > 0: return "Localized lesion burden."
    return "No significant lesion volume detected."

def generate_clinical_report_html(patient_data: dict) -> str:
    """Generate a structured, styled clinical report in HTML format."""
    if not patient_data or not patient_data.get("patient_id"):
        return """
        <div style="padding: 40px; text-align: center; color: #64748b;">
            <div style="font-size: 3em; margin-bottom: 20px;">📋</div>
            <div style="font-size: 1.2em;">Waiting for patient analysis...</div>
            <div style="font-size: 0.9em; margin-top: 10px;">Select a patient to generate AI diagnostic report.</div>
        </div>
        """
    
    patient_id = patient_data.get("patient_id", "UNKNOWN")
    metrics = patient_data.get("metrics", {})
    dice = float(metrics.get("dice_score", 0.0))
    conf = float(metrics.get("confidence", 0.0))
    volume = float(metrics.get("lesion_volume", 0.0))
    density = float(metrics.get("mean_density", 0.0))
    
    dice_label, dice_color = interpret_dice_score(dice)
    conf_label, conf_color = interpret_confidence(conf)
    volume_desc = interpret_lesion_volume(volume)
    
    # Radiomics observation
    density_obs = "Tissue density within expected range."
    if density > 250: density_obs = "Hyperdense region observed; may indicate focal irregularity."
    elif density < -50: density_obs = "Hypodense region observed; check for cystic components."
    
    # Recommendation logic
    recommendation = "Proceed with standard clinical workflow."
    if dice < 0.60 or conf < 0.60:
        recommendation = "<strong>Action Required:</strong> Discrepancy or low confidence detected. Immediate radiologist audit recommended."
    elif volume > 5000:
        recommendation = "<strong>Recommendation:</strong> Consider multi-slice volumetric review for surgical planning."

    xai_status = "Available & Integrated" if patient_data.get("heatmap") is not None else "Not Available"
    xai_color = "#10b981" if xai_status == "Available & Integrated" else "#94a3b8"

    html = f"""
    <div class="clinical-report-container">
        <div class="report-header">
            <span class="patient-badge">PATIENT ID: {patient_id}</span>
            <span class="status-badge" style="background-color: {dice_color}22; color: {dice_color}; border: 1px solid {dice_color}44;">
                {dice_label}
            </span>
        </div>
        
        <div class="report-section">
            <h4><span class="icon">🎯</span> AI Segmentation Assessment</h4>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="label">Dice Score</div>
                    <div class="value" style="color: {dice_color}">{dice:.3f}</div>
                </div>
                <div class="metric-item">
                    <div class="label">Confidence</div>
                    <div class="value" style="color: {conf_color}">{conf:.1%}</div>
                </div>
            </div>
            <p class="summary-text">AI analysis suggests a <strong>{dice_label.lower()}</strong> based on spatial overlap metrics. Model prediction is categorized as <strong>{conf_label.lower()}</strong>.</p>
        </div>
        
        <div class="report-section">
            <h4><span class="icon">📐</span> Lesion Characteristics</h4>
            <ul class="report-list">
                <li><strong>Estimated Volume:</strong> {volume:.1f} mm³</li>
                <li><strong>Observation:</strong> {volume_desc}</li>
            </ul>
        </div>
        
        <div class="report-section">
            <h4><span class="icon">📊</span> Radiomics & XAI Overview</h4>
            <ul class="report-list">
                <li><strong>Mean Density:</strong> {density:.1f} HU ({density_obs})</li>
                <li><strong>XAI Attribution:</strong> <span style="color: {xai_color}">{xai_status}</span></li>
            </ul>
        </div>
        
        <div class="report-footer">
            <div class="recommendation-box">
                <span class="rec-title">💡 Clinical Recommendation</span>
                <p>{recommendation}</p>
            </div>
            <div class="report-timestamp">Report generated by ECPC-AI Pipeline v1.0</div>
        </div>
    </div>
    """
    return html

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
