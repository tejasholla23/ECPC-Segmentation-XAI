"""
ECPC-IDS Endometriosis Segmentation XAI Dashboard
Main application file using Gradio Blocks for medical imaging visualization
"""

import gradio as gr
import numpy as np
from typing import Tuple
import config
from utils.helpers import validate_patient_id, format_metric_value, format_status_message
from components.ui_components import (
    create_patient_selector_section,
    create_image_display_section,
    create_metrics_cards_section,
    create_summary_section,
    create_dummy_image,
    create_dummy_segmentation_image,
    create_dummy_heatmap
)
from services.api_client import load_patient_data, load_random_patient_data


# ============================================================================
# Event Handlers
# ============================================================================

def _get_image_or_placeholder(image_data: any, name: str) -> np.ndarray:
    """
    Get an image from data or return a placeholder if missing/invalid.
    
    Args:
        image_data: Image data (numpy array, file path, or None)
        name (str): Image name for error messages
        
    Returns:
        np.ndarray: Valid image array or placeholder
    """
    if image_data is None:
        # Return a placeholder image
        placeholder = create_dummy_image((400, 400, 3), "empty")
        return placeholder
    
    if isinstance(image_data, np.ndarray):
        # Already a numpy array
        if len(image_data.shape) == 3 and image_data.shape[2] in (3, 4):
            return image_data
        else:
            # Invalid shape, return placeholder
            return create_dummy_image((400, 400, 3), "empty")
    
    # If it's a string path, we'd need to load it
    # For now, return placeholder
    return create_dummy_image((400, 400, 3), "empty")

def handle_load_patient(patient_id: str) -> Tuple:
    """
    Handle loading a patient's data and populating all visualizations.
    Calls the backend API and handles errors gracefully.
    
    Args:
        patient_id (str): The patient ID to load
        
    Returns:
        Tuple: All outputs for the dashboard components
    """
    # Validate patient ID
    is_valid, error_msg = validate_patient_id(patient_id)
    if not is_valid:
        status = format_status_message(error_msg, "error")
        return generate_empty_outputs(status)
    
    # Load patient data from backend API (with fallback support)
    success, patient_data, status_msg = load_patient_data(
        patient_id,
        use_fallback=True
    )
    
    if not success:
        return generate_empty_outputs(status_msg)
    
    # Extract data from response
    ct_img = _get_image_or_placeholder(patient_data.get("ct_image"), "CT image")
    pet_img = _get_image_or_placeholder(patient_data.get("pet_image"), "PET image")
    gt_img = _get_image_or_placeholder(patient_data.get("ground_truth"), "Ground truth")
    pred_img = _get_image_or_placeholder(patient_data.get("prediction"), "Prediction")
    heatmap_img = _get_image_or_placeholder(patient_data.get("heatmap"), "Heatmap")
    analysis_img = create_dummy_image((400, 400, 3), "empty")
    
    # Extract metrics from response
    metrics = patient_data.get("metrics", {})
    dice = metrics.get("dice_score", 0.0)
    iou = metrics.get("iou_score", 0.0)
    hausdorff = metrics.get("hausdorff_distance", 0.0)
    sensitivity = metrics.get("sensitivity", 0.0)
    specificity = metrics.get("specificity", 0.0)
    
    # Create summary text with actual data
    summary = f"""
    **Patient ID:** {patient_data.get('patient_id', 'UNKNOWN')}
    **Status:** {patient_data.get('status', 'completed')}
    **Message:** {patient_data.get('message', 'Analysis completed')}
    
    **Imaging Data:**
    - CT Scan: Loaded and processed
    - PET Scan: Loaded and processed
    - Ground Truth Segmentation: Available
    
    **Model Performance:**
    - Dice Score: {format_metric_value(dice)}
    - IoU (Jaccard): {format_metric_value(iou)}
    - Hausdorff Distance: {format_metric_value(hausdorff)}
    - Sensitivity: {format_metric_value(sensitivity)}
    - Specificity: {format_metric_value(specificity)}
    
    **XAI Analysis:**
    - Explainability heatmap generated
    - High-attribution regions highlighted
    - Ready for clinical review
    """
    
    return (
        ct_img, pet_img, gt_img, pred_img, heatmap_img, analysis_img,  # images
        dice, iou, hausdorff, sensitivity, specificity,  # metrics
        status_msg, summary.strip()  # status and summary
    )


def handle_clear_data() -> Tuple:
    """
    Handle clearing all displayed data and returning to initial state.
    
    Returns:
        Tuple: All outputs reset to default/empty values
    """
    status = format_status_message("Data cleared", "info")
    return generate_empty_outputs(status)


def generate_empty_outputs(status_message: str) -> Tuple:
    """
    Generate empty/default outputs for all dashboard components.
    
    Args:
        status_message (str): Status message to display
        
    Returns:
        Tuple: All empty/default outputs
    """
    empty_img = create_dummy_image((400, 400, 3), "empty")
    
    return (
        empty_img, empty_img, empty_img, empty_img, empty_img, empty_img,  # images
        0.0, 0.0, 0.0, 0.0, 0.0,  # metrics
        status_message,  # status
        "No patient data loaded. Use the Patient Selection panel to load a patient."  # summary
    )


# ============================================================================
# Main Application
# ============================================================================

def create_app() -> gr.Blocks:
    """
    Create and configure the main Gradio Blocks application.
    
    Returns:
        gr.Blocks: Configured Gradio application
    """
    
    with gr.Blocks(
        title=config.TITLE,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate"
        ),
        css="""
        .header-title {
            text-align: center;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #0066CC;
        }
        .header-subtitle {
            text-align: center;
            font-size: 1.1em;
            color: #666;
            margin-bottom: 30px;
        }
        .medical-card {
            border-radius: 12px;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .metric-card {
            border-radius: 8px;
            padding: 15px;
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
        }
        """
    ) as app:
        
        # ====================================================================
        # Header Section
        # ====================================================================
        gr.HTML(f"""
        <div class="header-title">{config.TITLE}</div>
        <div class="header-subtitle">{config.SUBTITLE}</div>
        """)
        
        # ====================================================================
        # Main Content Layout
        # ====================================================================
        with gr.Row(equal_height=False):
            
            # ================================================================
            # Left Panel - Controls
            # ================================================================
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### ⚙️ Controls")
                
                # Patient Selector
                patient_id_input, load_button, clear_button = create_patient_selector_section()
                
                gr.Markdown("---")
                
                # Additional Settings (placeholder)
                with gr.Group(label="⚙️ Settings", scale=1):
                    gr.Markdown("#### Display Options")
                    show_overlay = gr.Checkbox(
                        label="Show overlay comparison",
                        value=False,
                        interactive=True
                    )
                    confidence_threshold = gr.Slider(
                        label="Confidence Threshold",
                        minimum=0.0,
                        maximum=1.0,
                        value=0.5,
                        step=0.05,
                        interactive=True
                    )
                
                gr.Markdown("---")
                
                # Info Panel
                with gr.Group(label="ℹ️ Information"):
                    gr.Markdown("""
                    **Instructions:**
                    1. Enter a patient ID (e.g., PATIENT_001)
                    2. Click "Load Patient" to fetch imaging data
                    3. Review the segmentation results and metrics
                    4. Check the heatmap for XAI insights
                    5. Use "Clear" to reset and load another patient
                    """)
            
            # ================================================================
            # Right Panel - Displays
            # ================================================================
            with gr.Column(scale=2):
                gr.Markdown("### 📊 Analysis & Results")
                
                # Image Display Section
                (ct_image, pet_image, gt_image, pred_image, 
                 heatmap_image, analysis_image) = create_image_display_section()
                
                # Metrics Section
                (dice_score, iou_score, hausdorff_dist, 
                 sensitivity, specificity) = create_metrics_cards_section()
                
                # Status & Summary Section
                status_output, summary_output = create_summary_section()
        
        # ====================================================================
        # Event Handlers
        # ====================================================================
        
        # Load patient button click handler
        load_button.click(
            fn=handle_load_patient,
            inputs=[patient_id_input],
            outputs=[
                ct_image, pet_image, gt_image, pred_image, heatmap_image, analysis_image,
                dice_score, iou_score, hausdorff_dist, sensitivity, specificity,
                status_output, summary_output
            ],
            queue=False
        )
        
        # Clear button click handler
        clear_button.click(
            fn=handle_clear_data,
            inputs=[],
            outputs=[
                ct_image, pet_image, gt_image, pred_image, heatmap_image, analysis_image,
                dice_score, iou_score, hausdorff_dist, sensitivity, specificity,
                status_output, summary_output
            ],
            queue=False
        )
        
        # Load default patient on app start
        app.load(
            fn=handle_load_patient,
            inputs=[patient_id_input],
            outputs=[
                ct_image, pet_image, gt_image, pred_image, heatmap_image, analysis_image,
                dice_score, iou_score, hausdorff_dist, sensitivity, specificity,
                status_output, summary_output
            ]
        )
    
    return app


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    app = create_app()
    
    # Launch the application
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        debug=True
    )
