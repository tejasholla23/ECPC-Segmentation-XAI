# ECPC-IDS Dashboard - Quick Start Guide

## 🚀 Get Started in 2 Minutes

### Step 1: Verify Setup
```bash
cd ECPC-Segmentation-XAI
python test_setup.py
```

Expected output: ✓ All dependencies OK!

### Step 2: Run the Application
```bash
python app.py
```

The dashboard will open at: **http://127.0.0.1:7860**

---

## 📋 What You'll See

1. **Header Section**
   - Dashboard title and subtitle
   - Clear description of functionality

2. **Left Control Panel**
   - Patient ID input field (default: PATIENT_001)
   - "Load Patient" button to fetch data
   - "Clear" button to reset
   - Display options (overlay, confidence threshold)
   - Instructions panel

3. **Right Display Area**
   - **CT Scan** - Computed tomography image
   - **PET Scan** - Positron emission tomography image
   - **Ground Truth** - Reference segmentation mask
   - **Prediction** - AI model's predicted segmentation
   - **Heatmap** - Explainability attribution map
   - **Performance Metrics**:
     - Dice Score
     - IoU (Jaccard Index)
     - Hausdorff Distance
     - Sensitivity (Recall)
     - Specificity
   - **Status & Summary** - Detailed analysis results

---

## 🎮 How to Use

1. **Load Default Patient**
   - App loads PATIENT_001 automatically on startup

2. **Load Different Patient**
   - Enter a patient ID (e.g., PATIENT_002)
   - Click "🔄 Load Patient"
   - Wait for analysis to complete

3. **Examine Results**
   - Review medical imaging side-by-side
   - Check segmentation quality metrics
   - Study the XAI heatmap for model insights

4. **Reset for New Patient**
   - Click "🗑️ Clear" to clear current data
   - Enter new patient ID and load

---

## 🔧 Customization

Edit `config.py` to customize:

```python
# Backend API Connection (NEW!)
BACKEND_BASE_URL = "http://localhost:8000/api"   # Backend server URL
REQUEST_TIMEOUT = 30                              # Request timeout
DEMO_MODE = True                                  # Use dummy data if backend fails

# Application Settings
DEFAULT_PATIENT_ID = "PATIENT_002"                # Change default patient
DEFAULT_IMAGE_HEIGHT = 500                        # Display dimensions
DEFAULT_IMAGE_WIDTH = 500

# Metric Display
METRIC_DECIMAL_PLACES = 4                         # Precision for metrics
```

### Connecting to Your Backend

1. **Update config.py:**
```python
BACKEND_BASE_URL = "http://your-backend:8000/api"
DEMO_MODE = False  # Require backend (no fallback)
```

2. **Ensure backend provides endpoints:**
   - `GET /health` - Health check
   - `GET /patient?patient_id=PATIENT_001` - Fetch patient data
   - `GET /patient/random` - Random patient (for demos)

3. **Verify response format** - See [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md)

---

## 📁 Project Structure Overview

```
app.py                  ← Main application (run this!)
config.py               ← Settings and constants
test_setup.py           ← Verify setup
├── components/
│   └── ui_components.py    ← UI building blocks
├── utils/
│   └── helpers.py          ← Validation, formatting
├── services/           ← Backend integration (future)
└── assets/             ← Static files (future)
```

---

## ✨ Features Demonstrated

✅ Gradient-based responsive Gradio layout  
✅ Multi-image display with medical theme  
✅ Real-time metric calculations  
✅ Input validation  
✅ Error handling with user-friendly messages  
✅ Dummy data for testing without backend  
✅ Clean, professional UI with semantic HTML  

---

## 🔄 Next Steps (Future Enhancements)

- [ ] Connect to backend API (`services/api_client.py`)
- [ ] Load real patient data from database
- [ ] Add comparison view between predictions
- [ ] Export results to PDF/report format
- [ ] Add batch processing for multiple patients
- [ ] Implement user authentication
- [ ] Add advanced visualization filters

---

## 💡 Tips

- **Patient ID Validation**: Only alphanumeric characters, hyphens, and underscores
- **Responsive Design**: Works well on different screen sizes
- **Development Mode**: Dummy data loads instantly for testing UI
- **Console Output**: Check terminal for debugging information

---

## 🆘 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Port 7860 already in use
Edit `app.py` and change the port:
```python
app.launch(server_port=7861)
```

### Images not displaying
- Ensure numpy is installed: `pip install numpy`
- Check that dummy_data is enabled in config.py

---

## 📞 Support

Refer to:
- [README.md](README.md) - Full documentation
- [Gradio Docs](https://www.gradio.app/docs) - UI framework reference
- [config.py](config.py) - All configuration options

---

**Dashboard ready! 🎉 Run `python app.py` to start exploring endometriosis imaging data.**
