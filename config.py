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
RETRY_ATTEMPTS = 2
RETRY_DELAY = 1  # seconds

# Placeholder Text Values
TITLE = "ECPC-IDS Endometriosis Segmentation XAI Dashboard"
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

# UI Theme Configuration
THEME_PRIMARY_COLOR = "#0066CC"
THEME_SUCCESS_COLOR = "#28A745"
THEME_ERROR_COLOR = "#DC3545"
THEME_WARNING_COLOR = "#FFC107"

# Image Modal Options
MODALITIES = ["CT", "PET", "Ground Truth", "Prediction", "Heatmap"]
DEFAULT_MODALITY = "CT"

# Dummy Data Configuration (for development/testing without backend)
USE_DUMMY_DATA = True
DUMMY_DATA_SEED = 42
