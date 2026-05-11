# Backend API Integration Guide

## Overview

The ECPC-IDS Dashboard integrates with a backend medical imaging API through a dedicated service layer (`services/api_client.py`). This document explains how to use, extend, and troubleshoot the backend integration.

---

## Architecture

### Data Flow

```
User Input (Patient ID)
    ↓
app.py (UI Layer)
    ↓
services/api_client.py (Service Layer)
    ↓
Backend API Server
    ↓
Response Data
    ↓
Normalize & Extract
    ↓
Update Gradio UI
```

### Key Components

- **APIClient Class**: Handles HTTP requests and error management
- **load_patient_data()**: High-level function to load a specific patient
- **load_random_patient_data()**: Load random patient for demos
- **check_backend_health()**: Health check endpoint
- **Fallback System**: Automatic dummy data when backend is unavailable

---

## Configuration

### config.py Settings

```python
# Backend API Configuration
BACKEND_BASE_URL = "http://localhost:8000/api"    # API server URL
REQUEST_TIMEOUT = 30                               # Request timeout (seconds)
DEMO_MODE = True                                   # Enable fallback dummy data
HEALTH_CHECK_ENDPOINT = "/health"                 # Health check path
PATIENT_DATA_ENDPOINT = "/patient"                # Patient data path
RANDOM_PATIENT_ENDPOINT = "/patient/random"       # Random patient path
RETRY_ATTEMPTS = 2                                # Retry on failure
RETRY_DELAY = 1                                   # Delay between retries
```

### Updating for Your Backend

```python
# Example: Connect to a production backend
BACKEND_BASE_URL = "https://medical-imaging.example.com/api"
REQUEST_TIMEOUT = 60
DEMO_MODE = False  # Disable fallback (require real backend)
```

---

## API Usage

### Basic Usage in app.py

```python
from services.api_client import load_patient_data

# Load a specific patient
success, data, status_msg = load_patient_data("PATIENT_001")

if success:
    # Use the data
    ct_image = data["ct_image"]
    metrics = data["metrics"]
    print(f"Dice Score: {metrics['dice_score']}")
else:
    print(f"Error: {status_msg}")
```

### Response Data Structure

```python
{
    "patient_id": "PATIENT_001",
    "ct_image": numpy_array,                  # (H, W, 3) or None
    "pet_image": numpy_array,                 # (H, W, 3) or None
    "ground_truth": numpy_array,              # Segmentation mask
    "prediction": numpy_array,                # Model prediction
    "heatmap": numpy_array,                   # XAI attribution
    "metrics": {
        "dice_score": 0.89,
        "iou_score": 0.80,
        "hausdorff_distance": 8.5,
        "sensitivity": 0.92,
        "specificity": 0.95
    },
    "status": "completed",
    "message": "Analysis completed successfully"
}
```

### Advanced Usage

#### Check Backend Health

```python
from services.api_client import check_backend_health

is_healthy, message = check_backend_health()
if is_healthy:
    print("✓ Backend is available")
else:
    print(f"✗ Backend issue: {message}")
```

#### Direct Client Usage

```python
from services.api_client import get_api_client

client = get_api_client()

# Get patient data
success, data, error = client.get_patient_data("PATIENT_002")
if success:
    print(f"Loaded {data['patient_id']}")

# Random patient
success, data, error = client.get_random_patient_data()
if success:
    print(f"Random patient: {data['patient_id']}")
```

---

## Backend API Specification

The backend should provide these endpoints:

### GET /health

**Purpose**: Health check endpoint

**Response (200 OK):**
```json
{
    "status": "ok",
    "message": "Backend is running"
}
```

### GET /patient?patient_id=PATIENT_001

**Purpose**: Fetch a specific patient's data

**Query Parameters:**
- `patient_id` (required): Patient identifier

**Response (200 OK):**
```json
{
    "patient_id": "PATIENT_001",
    "ct_image": "base64_encoded_image_or_url",
    "pet_image": "base64_encoded_image_or_url",
    "ground_truth": "base64_encoded_mask_or_url",
    "prediction": "base64_encoded_mask_or_url",
    "heatmap": "base64_encoded_heatmap_or_url",
    "metrics": {
        "dice_score": 0.89,
        "iou_score": 0.80,
        "hausdorff_distance": 8.5,
        "sensitivity": 0.92,
        "specificity": 0.95
    },
    "status": "completed",
    "message": "Analysis completed successfully"
}
```

**Response (404 Not Found):**
```json
{
    "error": "Patient not found",
    "patient_id": "PATIENT_001"
}
```

### GET /patient/random

**Purpose**: Fetch a random patient's data (for demos)

**Response (200 OK):**
Same as `/patient` endpoint, with a random patient_id

---

## Error Handling

### Error Types Handled

The API client gracefully handles:

- **Connection Errors**: Backend server unreachable
- **Timeout Errors**: Request takes too long
- **Invalid JSON**: Response is not valid JSON
- **HTTP Errors**: 4xx, 5xx status codes
- **Invalid Data**: Missing required fields

### Fallback Behavior

When `DEMO_MODE = True` and an error occurs:

1. Log the error
2. Generate dummy patient data
3. Return success with demo data
4. Show warning message to user

**Example:**

```
⚠️ Backend unavailable - using demo data for PATIENT_001
```

### Disabling Fallback

To require the backend:

```python
# In config.py
DEMO_MODE = False

# In app.py, use:
success, data, status = load_patient_data(patient_id, use_fallback=False)
if not success:
    # Handle error appropriately
    show_error(status)
```

---

## Development & Testing

### Running Without Backend

```bash
# With DEMO_MODE = True (default)
python app.py
# ✓ App runs with dummy data
```

### Testing with Mock Backend

```python
# Create a simple test backend
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/patient', methods=['GET'])
def get_patient():
    patient_id = request.args.get('patient_id', 'UNKNOWN')
    return jsonify({
        "patient_id": patient_id,
        "ct_image": None,  # Use None for now
        "metrics": {
            "dice_score": 0.85,
            "iou_score": 0.75,
            "hausdorff_distance": 10.0,
            "sensitivity": 0.90,
            "specificity": 0.92
        },
        "status": "completed",
        "message": "Test data"
    })

if __name__ == '__main__':
    app.run(port=8000)
```

### Running with Mock Backend

```bash
# Terminal 1: Start mock backend
python mock_backend.py

# Terminal 2: Run dashboard (with DEMO_MODE = False if you want)
python app.py
# ✓ Dashboard calls mock backend
```

---

## Logging

The API client logs all requests and errors. Check the application logs for:

```
INFO: Making GET request to http://localhost:8000/api/patient?patient_id=PATIENT_001
INFO: Successfully received response from http://localhost:8000/api/patient?patient_id=PATIENT_001
WARNING: Backend unavailable, using fallback dummy data for PATIENT_001
ERROR: Connection error: [Errno 10061] No connection could be made because...
```

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Extending the API Client

### Adding New Endpoints

```python
# In services/api_client.py

def get_patient_comparison(patient_id1: str, patient_id2: str) -> Tuple[bool, Dict, str]:
    """Compare two patients' analyses."""
    client = get_api_client()
    endpoint = f"/patient/compare?p1={patient_id1}&p2={patient_id2}"
    success, data, error = client._make_request(endpoint)
    
    if success:
        return True, data, ""
    else:
        return False, {}, error
```

### Custom Error Handling

```python
# Override error handling in APIClient subclass

class CustomAPIClient(APIClient):
    def _make_request(self, endpoint, method="GET", params=None, json_data=None):
        try:
            # Custom logic here
            return super()._make_request(endpoint, method, params, json_data)
        except CustomException as e:
            # Custom handling
            logger.custom_error(e)
            return False, {}, str(e)
```

### Caching Responses

```python
# In services/api_client.py

from functools import lru_cache

class CachedAPIClient(APIClient):
    @lru_cache(maxsize=128)
    def get_patient_data(self, patient_id: str):
        """Cached version - same patient returns cached result."""
        return super().get_patient_data(patient_id)
```

---

## Troubleshooting

### "Connection refused" Error

**Problem:**
```
Connection error: [Errno 10061] No connection could be made because the target machine actively refused it
```

**Solution:**
1. Check if backend server is running
2. Verify `BACKEND_BASE_URL` in config.py
3. Check firewall/network settings
4. Use `check_backend_health()` to verify

### Timeout Error

**Problem:**
```
Request timeout (30s) connecting to http://localhost:8000/api/patient
```

**Solution:**
1. Increase `REQUEST_TIMEOUT` in config.py
2. Check backend server performance
3. Check network connectivity
4. Look for slow queries in backend logs

### Invalid JSON Response

**Problem:**
```
Invalid JSON in response: Expecting value
```

**Solution:**
1. Verify backend returns valid JSON
2. Check response Content-Type header
3. Look for HTML error pages instead of JSON
4. Enable logging to see raw response

### Missing Fields

**Problem:**
```
Metrics missing required fields
```

**Solution:**
1. Check backend response format
2. Verify backend updated to new schema
3. Use `normalize_response_data()` to handle gracefully
4. Check backend API documentation

---

## Best Practices

✅ **DO:**
- Use the high-level functions (`load_patient_data()`) in the UI
- Check `success` flag before using data
- Log errors for debugging
- Use `DEMO_MODE` for development
- Validate patient IDs before API calls

❌ **DON'T:**
- Call `_make_request()` directly (use high-level functions)
- Ignore `error_msg` return values
- Assume backend is always available
- Mix API calls with dummy data logic
- Cache large images without size limits

---

## Example: Adding Patient Search

```python
def search_patients(query: str, limit: int = 10) -> Tuple[bool, list, str]:
    """Search for patients by ID or name."""
    client = get_api_client()
    endpoint = f"/patient/search?q={query}&limit={limit}"
    success, data, error = client._make_request(endpoint)
    
    if success and isinstance(data, dict) and "results" in data:
        return True, data["results"], ""
    elif not success:
        if config.DEMO_MODE:
            # Generate dummy search results
            dummy_results = [
                "PATIENT_001", "PATIENT_002", "PATIENT_003"
            ]
            return True, dummy_results, "Using demo data"
    
    return False, [], error
```

---

## API Evolution & Versioning

### Future Compatibility

If your backend API changes:

1. **Add version support:**
```python
API_VERSION = "v1"
PATIENT_DATA_ENDPOINT = f"/{API_VERSION}/patient"
```

2. **Add migration logic:**
```python
def normalize_response_data(response, api_version="v1"):
    if api_version == "v1":
        # v1 format handling
    elif api_version == "v2":
        # v2 format handling
```

3. **Plan backwards compatibility:**
```python
# Support both old and new formats
old_format = convert_to_v1(data)
```

---

## Support & Resources

- Check logs with: `tail -f app.log`
- Test API endpoints with: `curl http://localhost:8000/api/health`
- Use Postman for API testing
- Review backend API documentation
- Check browser console for frontend errors

---

**Last Updated:** May 11, 2026  
**Version:** 1.0
