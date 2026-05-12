"""
Configuration file for ECPC-IDS Endometriosis Segmentation XAI Dashboard.
Defines backend URLs, default values, and application settings.
"""

# Backend API Configuration
BACKEND_BASE_URL = "http://localhost:8000/api"
REQUEST_TIMEOUT = 30  # seconds
DEMO_MODE = True  # Use dummy data if backend unavailable
HEALTH_CHECK_ENDPOINT = "/health"
PATIENT_DATA_ENDPOINT = "/patient"
RANDOM_PATIENT_ENDPOINT = "/patient/random"

# Default Application Settings
DEFAULT_PATIENT_ID = "PATIENT_001"
MAX_PATIENT_ID_LENGTH = 50
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # seconds

# Clinical Metric Constants
METRIC_DICE = "dice_score"
METRIC_IOU = "iou_score"
METRIC_HAUSDORFF = "hausdorff_distance"
METRIC_SENSITIVITY = "sensitivity"
METRIC_SPECIFICITY = "specificity"
METRIC_CONFIDENCE = "confidence"
METRIC_LESION_VOLUME = "lesion_volume"
METRIC_SPHERICITY = "sphericity"
METRIC_MAX_DIAMETER = "max_diameter"
METRIC_MEAN_DENSITY = "mean_density"

# Placeholder Text Values
TITLE = "Diagnostic Dashboard"
SUBTITLE = "Interactive visualization of CT/PET imaging with AI predictions and explainability heatmaps"

STATUS_PLACEHOLDER = "Ready to analyze imaging data"
ERROR_MESSAGE_PREFIX = "⚠️ Error: "
SUCCESS_MESSAGE_PREFIX = "✓ Success: "

# Image Display Settings
DEFAULT_IMAGE_HEIGHT = 400
DEFAULT_IMAGE_WIDTH = 400
IMAGE_QUALITY = 95  # JPEG quality (0-100)

# Metrics Display Settings
METRIC_DECIMAL_PLACES = 3
CONFIDENCE_THRESHOLD = 0.5

# Output Folder Paths (for future use)
OUTPUT_FOLDER_PREDICTIONS = "./outputs/predictions"
OUTPUT_FOLDER_HEATMAPS = "./outputs/heatmaps"
OUTPUT_FOLDER_REPORTS = "./outputs/reports"

# UI Theme Configuration (Premium Medical Palette)
THEME_PRIMARY_COLOR = "#0066CC"
THEME_SECONDARY_COLOR = "#64748b"  # Slate
THEME_BACKGROUND_DARK = "#0f172a"  # Very dark slate
THEME_ACCENT_COLOR = "#38bdf8"     # Light blue
THEME_SUCCESS_COLOR = "#10b981"    # Emerald
THEME_ERROR_COLOR = "#ef4444"      # Red
THEME_WARNING_COLOR = "#f59e0b"    # Amber

# Image Modal Options
MODALITIES = ["CT", "PET", "Ground Truth", "Prediction", "Heatmap"]
DEFAULT_MODALITY = "CT"

# Dummy Data Configuration (for development/testing without backend)
USE_DUMMY_DATA = True
DUMMY_DATA_SEED = 42
