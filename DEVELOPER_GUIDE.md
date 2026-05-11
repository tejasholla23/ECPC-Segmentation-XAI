# Backend Integration Developer Guide

## Overview

This guide explains how the ECPC-IDS Dashboard integrates with backend services and how developers can work with the API client layer.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Gradio Web UI (app.py)                   │
│  - Patient ID input                                         │
│  - Medical image display                                    │
│  - Metrics visualization                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓ (function calls)
┌─────────────────────────────────────────────────────────────┐
│            Service Layer (services/api_client.py)            │
│  - load_patient_data()                                      │
│  - load_random_patient_data()                               │
│  - Error handling & retry logic                             │
│  - Response normalization                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ↓                         ↓
┌──────────────────┐    ┌──────────────────┐
│  Backend API     │    │  Fallback Dummy  │
│  (HTTP requests) │    │  Data Generator  │
└──────────────────┘    └──────────────────┘
```

---

## File Organization

### Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Gradio UI application |
| `config.py` | Configuration settings |
| `services/api_client.py` | Backend API client |
| `components/ui_components.py` | UI building blocks |
| `utils/helpers.py` | Utility functions |

---

## How the Integration Works

### 1. User Interaction

```python
# User enters patient ID in UI and clicks "Load Patient"
handle_load_patient(patient_id="PATIENT_001")
```

### 2. Validation

```python
# app.py validates the patient ID
is_valid, error_msg = validate_patient_id(patient_id)
if not is_valid:
    return error_response(error_msg)
```

### 3. API Call

```python
# app.py calls the service layer
from services.api_client import load_patient_data

success, data, status_msg = load_patient_data(
    patient_id="PATIENT_001",
    use_fallback=True  # Enable fallback to dummy data
)
```

### 4. Service Layer Processing

```python
# services/api_client.py:
# 1. Creates APIClient instance
# 2. Makes HTTP GET request to backend
# 3. Handles errors gracefully
# 4. Falls back to dummy data if needed
# 5. Returns normalized data
```

### 5. Response Handling

```python
# app.py extracts and displays data
if success:
    ct_image = data["ct_image"]
    metrics = data["metrics"]
    summary = f"Dice: {metrics['dice_score']}"
    # Update UI components
else:
    status = format_status_message(status_msg, "error")
    # Show error to user
```

---

## API Client API Reference

### Main Entry Points (Use These!)

#### `load_patient_data(patient_id, use_fallback=True)`

Load a specific patient's data with automatic fallback.

**Parameters:**
- `patient_id` (str): Patient ID to load
- `use_fallback` (bool): Use dummy data if backend fails

**Returns:**
- `success` (bool): True if data obtained (real or dummy)
- `data` (dict): Patient data with images and metrics
- `status_msg` (str): Status message for UI display

**Example:**
```python
success, data, status = load_patient_data("PATIENT_001")
if success:
    print(f"Loaded: {data['patient_id']}")
    print(f"Dice: {data['metrics']['dice_score']}")
```

#### `load_random_patient_data(use_fallback=True)`

Load a random patient's data (useful for demos).

**Returns:**
- Same as `load_patient_data()`

**Example:**
```python
success, data, status = load_random_patient_data()
if success:
    demo_patient = data['patient_id']
```

#### `check_backend_health()`

Check if backend API is available.

**Returns:**
- `is_healthy` (bool): True if backend is responsive
- `status_msg` (str): Descriptive message

**Example:**
```python
is_healthy, msg = check_backend_health()
if is_healthy:
    print("✓ Backend available")
else:
    print(f"✗ {msg}")
```

### Advanced Usage (Rarely Needed)

#### `get_api_client()`

Get the singleton API client instance.

```python
from services.api_client import get_api_client

client = get_api_client()
success, data, error = client.get_patient_data("PATIENT_001")
```

---

## Configuration (config.py)

### Backend Settings

```python
# API Server
BACKEND_BASE_URL = "http://localhost:8000/api"
REQUEST_TIMEOUT = 30

# Endpoints (relative to base URL)
HEALTH_CHECK_ENDPOINT = "/health"
PATIENT_DATA_ENDPOINT = "/patient"
RANDOM_PATIENT_ENDPOINT = "/patient/random"

# Fallback Behavior
DEMO_MODE = True  # Use dummy data when backend fails
RETRY_ATTEMPTS = 2
RETRY_DELAY = 1
```

### Development Configuration

```python
# For local development with mock backend
BACKEND_BASE_URL = "http://localhost:5000/api"
DEMO_MODE = True  # Still allow fallback

# For production with required backend
BACKEND_BASE_URL = "https://medical-api.example.com/api"
DEMO_MODE = False  # Disable fallback
REQUEST_TIMEOUT = 60  # More time for complex analysis
```

---

## Backend API Specification

Your backend should implement these endpoints:

### Health Check

```
GET /api/health

Response: 200 OK
{
    "status": "ok",
    "message": "Backend is running"
}
```

### Get Patient

```
GET /api/patient?patient_id=PATIENT_001

Response: 200 OK
{
    "patient_id": "PATIENT_001",
    "ct_image": "base64_string_or_url",
    "pet_image": "base64_string_or_url",
    "ground_truth": "base64_string_or_url",
    "prediction": "base64_string_or_url",
    "heatmap": "base64_string_or_url",
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

### Get Random Patient

```
GET /api/patient/random

Response: Same as /api/patient
```

---

## Error Handling Strategy

### Errors Handled Automatically

| Error | Handling |
|-------|----------|
| Connection refused | Fallback to dummy data (if enabled) |
| Timeout (>30s) | Fallback to dummy data |
| Invalid JSON | Fallback to dummy data |
| Missing fields | Use safe defaults |
| 404 Not Found | Return error message |
| 500 Server Error | Fallback to dummy data |

### Error Messages Shown to User

```
✓ Loaded patient PATIENT_001 from backend
⚠️ Backend unavailable - using demo data for PATIENT_001
❌ Error: Invalid patient ID format
❌ Error: Connection error to backend server
```

---

## Testing the Integration

### Test with Real Backend

```bash
# 1. Start your backend server
python backend_server.py

# 2. Update config.py
BACKEND_BASE_URL = "http://localhost:8000/api"
DEMO_MODE = False  # Require backend

# 3. Run dashboard
python app.py

# 4. Load a patient - should call your backend
```

### Test with Mock Backend

```python
# mock_backend.py
from flask import Flask, jsonify, request
import base64
import numpy as np

app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/patient')
def get_patient():
    patient_id = request.args.get('patient_id', 'UNKNOWN')
    return jsonify({
        "patient_id": patient_id,
        "metrics": {
            "dice_score": 0.87,
            "iou_score": 0.78,
            "hausdorff_distance": 9.2,
            "sensitivity": 0.89,
            "specificity": 0.93
        },
        "status": "completed",
        "message": "Mock data"
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)
```

```bash
# Terminal 1: Start mock backend
python mock_backend.py

# Terminal 2: Start dashboard
python app.py
```

### Test Without Backend (Fallback)

```python
# config.py
DEMO_MODE = True  # Enable fallback

# Run without starting any backend
python app.py
# ✓ Should work with dummy data
```

---

## Debugging Tips

### Enable Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your code - see detailed logs
```

### Check API Connectivity

```bash
# Test endpoint directly
curl http://localhost:8000/api/health

# Test with specific patient
curl "http://localhost:8000/api/patient?patient_id=PATIENT_001"
```

### Inspect Response Data

```python
from services.api_client import get_api_client

client = get_api_client()
success, data, error = client.get_patient_data("PATIENT_001")

if success:
    print("Keys in response:", data.keys())
    print("Metrics:", data["metrics"])
    print("Patient ID:", data["patient_id"])
else:
    print(f"Error: {error}")
```

### Check Backend Availability

```python
from services.api_client import check_backend_health

is_healthy, msg = check_backend_health()
print(f"Backend healthy: {is_healthy}")
print(f"Message: {msg}")
```

---

## Common Integration Scenarios

### Scenario 1: Connect to Existing REST API

```python
# config.py
BACKEND_BASE_URL = "https://your-api.example.com/v1"
DEMO_MODE = False
```

**That's it!** If your API matches the expected format, it works.

### Scenario 2: Transform Legacy Backend Format

```python
# services/api_client.py - override normalize_response_data()

@staticmethod
def normalize_response_data(response: Dict) -> Dict:
    # Handle legacy format
    return {
        "patient_id": response.get("id"),  # Note: different key
        "ct_image": response.get("CT"),    # Different format
        "metrics": transform_metrics(response.get("results")),
        # ...
    }
```

### Scenario 3: Add Caching

```python
# services/cache_layer.py
from functools import lru_cache

@lru_cache(maxsize=100)
def get_patient_cached(patient_id: str):
    return load_patient_data(patient_id)
```

### Scenario 4: Async Loading

```python
# For long-running backend operations
import asyncio

async def load_patient_async(patient_id: str):
    # Use asyncio for non-blocking I/O
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, 
        load_patient_data, 
        patient_id
    )
    return result
```

---

## Production Checklist

- [ ] Backend server is running and tested
- [ ] `BACKEND_BASE_URL` is set correctly
- [ ] API endpoints match specification
- [ ] `DEMO_MODE` set appropriately (False for production)
- [ ] Logging configured for monitoring
- [ ] Error handling tested for all failure modes
- [ ] Response times acceptable
- [ ] Sensitive data is not exposed in logs
- [ ] SSL/TLS enabled for HTTPS endpoints
- [ ] API authentication configured if needed

---

## Extending the API Client

### Adding New Endpoints

```python
# In services/api_client.py

class APIClient:
    def get_patient_comparison(self, patient_id1: str, patient_id2: str):
        """Compare two patients."""
        endpoint = f"/patient/compare?p1={patient_id1}&p2={patient_id2}"
        return self._make_request(endpoint)
    
    def submit_feedback(self, patient_id: str, feedback: str):
        """Submit user feedback."""
        endpoint = "/feedback"
        return self._make_request(
            endpoint,
            method="POST",
            json_data={"patient_id": patient_id, "feedback": feedback}
        )
```

### Custom Error Handling

```python
class ProductionAPIClient(APIClient):
    def _make_request(self, *args, **kwargs):
        try:
            return super()._make_request(*args, **kwargs)
        except Exception as e:
            # Send alert to monitoring system
            send_alert(f"API Error: {str(e)}")
            raise
```

### Request/Response Logging

```python
import json

class LoggingAPIClient(APIClient):
    def _make_request(self, endpoint, **kwargs):
        logger.info(f"Request: {endpoint} {json.dumps(kwargs)}")
        success, data, error = super()._make_request(endpoint, **kwargs)
        if success:
            logger.info(f"Response: {json.dumps(data, default=str)}")
        else:
            logger.error(f"Error: {error}")
        return success, data, error
```

---

## Support & Resources

- **API Integration Guide**: [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md)
- **Main README**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Configuration**: [config.py](config.py)
- **Source Code**: [services/api_client.py](services/api_client.py)

---

**Last Updated:** May 11, 2026  
**Version:** 1.0
