"""
Backend API Client for ECPC-IDS Dashboard.
Handles all communication with the backend server including patient data fetching,
error handling, and fallback to dummy data when backend is unavailable.
"""

import requests
from typing import Dict, Optional, Tuple, Any
import logging
import config
import numpy as np
from utils.helpers import format_status_message

# Configure logging
logger = logging.getLogger(__name__)


class APIClient:
    """
    API Client for communicating with the ECPC backend server.
    Handles patient data requests, error handling, and fallback mechanisms.
    """
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url (Optional[str]): Backend API base URL. Uses config.BACKEND_BASE_URL if None.
            timeout (int): Request timeout in seconds
        """
        self.base_url = base_url or config.BACKEND_BASE_URL
        self.timeout = timeout
        self.backend_available = None  # Track backend status
    
    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Tuple[bool, Dict, str]:
        """
        Make an HTTP request to the backend API.
        
        Args:
            endpoint (str): API endpoint (e.g., '/patient' or '/patient/random')
            method (str): HTTP method ('GET' or 'POST')
            params (Optional[Dict]): Query parameters
            json_data (Optional[Dict]): JSON payload for POST requests
            
        Returns:
            Tuple[bool, Dict, str]: (success, response_dict, error_message)
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"Making {method} request to {url}")
            
            if method == "GET":
                response = requests.get(
                    url,
                    params=params,
                    timeout=self.timeout
                )
            elif method == "POST":
                response = requests.post(
                    url,
                    json=json_data,
                    timeout=self.timeout
                )
            else:
                return False, {}, f"Unsupported HTTP method: {method}"
            
            # Check response status
            response.raise_for_status()
            
            # Parse JSON response
            try:
                data = response.json()
                self.backend_available = True
                logger.info(f"Successfully received response from {url}")
                return True, data, ""
            
            except ValueError as e:
                error_msg = f"Invalid JSON in response: {str(e)}"
                logger.error(error_msg)
                return False, {}, error_msg
        
        except requests.exceptions.Timeout:
            error_msg = f"Request timeout ({self.timeout}s) connecting to {url}"
            logger.warning(error_msg)
            self.backend_available = False
            return False, {}, error_msg
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: {str(e)}"
            logger.warning(error_msg)
            self.backend_available = False
            return False, {}, error_msg
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            self.backend_available = False
            return False, {}, error_msg
    
    def health_check(self) -> bool:
        """
        Check if the backend API is healthy and responsive.
        
        Returns:
            bool: True if backend is available, False otherwise
        """
        success, _, _ = self._make_request(config.HEALTH_CHECK_ENDPOINT)
        return success
    
    def get_patient_data(self, patient_id: str) -> Tuple[bool, Dict, str]:
        """
        Fetch patient data from the backend API.
        
        Args:
            patient_id (str): The patient ID to fetch
            
        Returns:
            Tuple[bool, Dict, str]: (success, data_dict, error_message)
                - success: True if request succeeded
                - data_dict: Patient data or empty dict on failure
                - error_message: Empty string on success, error description on failure
        """
        if not patient_id:
            return False, {}, "Patient ID cannot be empty"
        
        endpoint = f"{config.PATIENT_DATA_ENDPOINT}?patient_id={patient_id}"
        success, data, error_msg = self._make_request(endpoint)
        
        if not success:
            return False, {}, error_msg
        
        # Normalize the response data
        normalized_data = self.normalize_response_data(data)
        return True, normalized_data, ""
    
    def get_random_patient_data(self) -> Tuple[bool, Dict, str]:
        """
        Fetch a random patient's data from the backend API (useful for demos).
        
        Returns:
            Tuple[bool, Dict, str]: (success, data_dict, error_message)
        """
        success, data, error_msg = self._make_request(config.RANDOM_PATIENT_ENDPOINT)
        
        if not success:
            return False, {}, error_msg
        
        # Normalize the response data
        normalized_data = self.normalize_response_data(data)
        return True, normalized_data, ""
    
    @staticmethod
    def normalize_response_data(response: Dict) -> Dict:
        """
        Normalize API response data to a consistent format.
        Ensures all expected keys are present with safe defaults.
        
        Args:
            response (Dict): Raw API response data
            
        Returns:
            Dict: Normalized data with all expected fields
        """
        normalized = {
            "patient_id": response.get("patient_id", "UNKNOWN"),
            "ct_image": response.get("ct_image", None),
            "pet_image": response.get("pet_image", None),
            "ground_truth": response.get("ground_truth", None),
            "prediction": response.get("prediction", None),
            "heatmap": response.get("heatmap", None),
            "metrics": {
                config.METRIC_DICE: float(response.get("metrics", {}).get(config.METRIC_DICE, 0.0)),
                config.METRIC_IOU: float(response.get("metrics", {}).get(config.METRIC_IOU, 0.0)),
                config.METRIC_HAUSDORFF: float(response.get("metrics", {}).get(config.METRIC_HAUSDORFF, 0.0)),
                config.METRIC_SENSITIVITY: float(response.get("metrics", {}).get(config.METRIC_SENSITIVITY, 0.0)),
                config.METRIC_SPECIFICITY: float(response.get("metrics", {}).get(config.METRIC_SPECIFICITY, 0.0)),
                config.METRIC_CONFIDENCE: float(response.get("metrics", {}).get(config.METRIC_CONFIDENCE, 0.0)),
                config.METRIC_LESION_VOLUME: float(response.get("metrics", {}).get(config.METRIC_LESION_VOLUME, 0.0)),
                config.METRIC_SPHERICITY: float(response.get("metrics", {}).get(config.METRIC_SPHERICITY, 0.0)),
                config.METRIC_MAX_DIAMETER: float(response.get("metrics", {}).get(config.METRIC_MAX_DIAMETER, 0.0)),
                config.METRIC_MEAN_DENSITY: float(response.get("metrics", {}).get(config.METRIC_MEAN_DENSITY, 0.0)),
            },
            "status": response.get("status", "completed"),
            "message": response.get("message", "Analysis completed")
        }
        return normalized


# Global API client instance
_api_client = None


def get_api_client() -> APIClient:
    """
    Get or create the global API client instance.
    
    Returns:
        APIClient: Singleton API client instance
    """
    global _api_client
    if _api_client is None:
        _api_client = APIClient(
            base_url=config.BACKEND_BASE_URL,
            timeout=config.REQUEST_TIMEOUT
        )
    return _api_client


def load_patient_data(patient_id: str, use_fallback: bool = True) -> Tuple[bool, Dict, str]:
    """
    Load patient data from the backend API with optional fallback to dummy data.
    
    Args:
        patient_id (str): Patient ID to load
        use_fallback (bool): If True, returns dummy data on API failure
        
    Returns:
        Tuple[bool, Dict, str]: (success, data_dict, status_message)
    """
    client = get_api_client()
    success, data, error_msg = client.get_patient_data(patient_id)
    
    if success:
        status = format_status_message(
            f"Loaded patient {patient_id} from backend",
            "success"
        )
        return True, data, status
    
    # Handle failure
    if use_fallback and config.DEMO_MODE:
        logger.warning(f"Backend unavailable, using fallback dummy data for {patient_id}")
        dummy_data = _generate_dummy_patient_data(patient_id)
        status = format_status_message(
            f"Backend unavailable - using demo data for {patient_id}",
            "warning"
        )
        return True, dummy_data, status
    else:
        status = format_status_message(f"Error: {error_msg}", "error")
        return False, {}, status


def load_random_patient_data(use_fallback: bool = True) -> Tuple[bool, Dict, str]:
    """
    Load a random patient's data (useful for demos).
    
    Args:
        use_fallback (bool): If True, returns dummy data on API failure
        
    Returns:
        Tuple[bool, Dict, str]: (success, data_dict, status_message)
    """
    client = get_api_client()
    success, data, error_msg = client.get_random_patient_data()
    
    if success:
        patient_id = data.get("patient_id", "UNKNOWN")
        status = format_status_message(
            f"Loaded random patient {patient_id} from backend",
            "success"
        )
        return True, data, status
    
    # Handle failure
    if use_fallback and config.DEMO_MODE:
        logger.warning("Backend unavailable, using fallback dummy data")
        dummy_data = _generate_dummy_patient_data(config.DEFAULT_PATIENT_ID)
        status = format_status_message(
            "Backend unavailable - using demo data",
            "warning"
        )
        return True, dummy_data, status
    else:
        status = format_status_message(f"Error: {error_msg}", "error")
        return False, {}, status


def _generate_dummy_patient_data(patient_id: str) -> Dict:
    """
    Generate dummy patient data for development/demo purposes.
    
    Args:
        patient_id (str): The patient ID for the dummy data
        
    Returns:
        Dict: Dummy patient data in normalized format
    """
    # Import here to avoid circular imports
    from components.ui_components import (
        create_dummy_image,
        create_dummy_segmentation_image,
        create_dummy_heatmap
    )
    
    return {
        "patient_id": patient_id,
        "ct_image": create_dummy_image((400, 400, 3), "gradient"),
        "pet_image": create_dummy_image((400, 400, 3), "checkerboard"),
        "ground_truth": create_dummy_segmentation_image((400, 400, 3)),
        "prediction": create_dummy_segmentation_image((400, 400, 3)),
        "heatmap": create_dummy_heatmap((400, 400, 3)),
        "metrics": {
            config.METRIC_DICE: np.random.uniform(0.75, 0.95),
            config.METRIC_IOU: np.random.uniform(0.65, 0.90),
            config.METRIC_HAUSDORFF: np.random.uniform(5.0, 15.0),
            config.METRIC_SENSITIVITY: np.random.uniform(0.75, 0.95),
            config.METRIC_SPECIFICITY: np.random.uniform(0.80, 0.98),
            config.METRIC_CONFIDENCE: np.random.uniform(0.70, 0.99),
            config.METRIC_LESION_VOLUME: np.random.uniform(100.0, 5000.0),
            config.METRIC_SPHERICITY: np.random.uniform(0.40, 0.90),
            config.METRIC_MAX_DIAMETER: np.random.uniform(5.0, 50.0),
            config.METRIC_MEAN_DENSITY: np.random.uniform(-100.0, 300.0),
        },
        "status": "completed",
        "message": "Analysis completed (demo data)"
    }


def check_backend_health() -> Tuple[bool, str]:
    """
    Check if the backend API is available and healthy.
    
    Returns:
        Tuple[bool, str]: (is_healthy, status_message)
    """
    client = get_api_client()
    is_healthy = client.health_check()
    
    if is_healthy:
        return True, "Backend API is available"
    else:
        if config.DEMO_MODE:
            return False, "Backend API unavailable - using demo mode"
        else:
            return False, "Backend API unavailable"
