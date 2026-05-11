# ECPC-IDS Endometriosis Segmentation XAI Dashboard

A Gradio-based web dashboard for interactive visualization of CT/PET medical imaging with AI segmentation predictions and explainability (XAI) heatmaps.

## Project Structure

```
├── app.py                  # Main Gradio application
├── config.py               # Configuration and settings
├── requirements.txt        # Python dependencies
├── components/             # UI component functions
│   ├── __init__.py
│   └── ui_components.py   # Reusable UI building blocks
├── utils/                  # Helper utilities
│   ├── __init__.py
│   └── helpers.py         # Validation, formatting, data handling
├── services/              # Backend API integration (future)
│   ├── __init__.py
│   └── README.md
└── assets/                # Static assets (future)
```

## Features

- **Patient Management**: Load and manage patient imaging data by ID
- **Multi-Modal Imaging**: Display CT and PET scans side-by-side
- **Segmentation Results**: Visualize ground truth vs model predictions
- **XAI Heatmaps**: Explainability visualizations showing model attribution
- **Performance Metrics**: Real-time display of segmentation quality metrics
  - Dice Score, IoU (Jaccard), Hausdorff Distance
  - Sensitivity, Specificity
- **Responsive UI**: Clean, medical-themed interface with good spacing and readability
- **Backend Integration**: Full API client for connecting to medical imaging backend
- **Fallback System**: Works without backend using dummy data for development/testing
- **Error Handling**: Graceful handling of network errors and invalid data

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
cd ECPC-Segmentation-XAI
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python app.py
```

The dashboard will launch at `http://127.0.0.1:7860`

## Usage

1. **Enter Patient ID**: Input a patient identifier (e.g., PATIENT_001)
2. **Load Patient**: Click the "Load Patient" button to fetch and display data
3. **Review Results**: 
   - View CT/PET scans and segmentation results
   - Check performance metrics
   - Examine XAI heatmap for model interpretability
4. **Adjust Settings**: Use display options to customize visualization
5. **Clear Data**: Click "Clear" to reset and load a new patient

## Configuration

Edit `config.py` to customize:
- Backend API URL and timeout
- Default patient ID
- Image display dimensions
- Metric precision and thresholds
- UI theme colors
- Dummy data settings

## Development Notes

### Current Status
- ✅ Frontend UI structure implemented
- ✅ Backend API client layer created
- ✅ Dummy data generation for testing
- ✅ Error handling and fallback support
- 🔄 Backend server integration (ready for connection)
- 🔄 Database connectivity (to be implemented)
- 🔄 Advanced visualization options (to be implemented)

### Next Steps
1. Implement backend API client in `services/api_client.py`
2. Add database models and data access layer
3. Integrate real medical imaging data loading
4. Add export/report generation functionality
5. Implement user authentication and audit logging

## API Integration (Ready)

The dashboard includes a complete backend API client layer (`services/api_client.py`):

- Automatic fallback to dummy data if backend is unavailable
- Comprehensive error handling for network issues
- Health check endpoint for backend status
- Support for fetching specific or random patient data
- Response data normalization for consistent format

### Quick Setup

```python
# In app.py, the UI already calls the API client:
from services.api_client import load_patient_data

success, data, status = load_patient_data(patient_id)
```

### Backend Configuration

Update `config.py` to connect to your backend:

```python
BACKEND_BASE_URL = "http://your-backend:8000/api"
DEMO_MODE = False  # Disable fallback when backend is ready
```

For detailed integration instructions, see [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md).

## Contributing

Standard Python practices:
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include type hints where possible
- Test changes before committing

## License

[To be specified]

## Contact

[Project maintainers]
