"""
ECPC-IDS Endometriosis Segmentation XAI Dashboard
Main application file using Gradio Blocks for medical imaging visualization
"""

import gradio as gr
import numpy as np
from typing import Tuple
import config
from utils.helpers import (
    validate_patient_id,
    format_metric_value,
    format_status_message,
    safe_get_nested_value,
    create_placeholder_image,
    load_image_safe,
    load_mask_safe,
    overlay_mask,
    overlay_heatmap,
    create_mask_visual,
    generate_clinical_report_html
)
from components.ui_components import (
    create_patient_selector_section,
    create_image_display_section,
    create_metrics_cards_section,
    create_summary_section,
    create_dummy_image
)
from services.api_client import load_patient_data, load_random_patient_data


# ============================================================================
# Event Handlers
# ============================================================================

def _prepare_patient_images(patient_data: dict, show_overlay: bool = False) -> tuple:
    """
    Prepare all image outputs from backend data with safe conversion.
    """
    ct_img = load_image_safe(
        patient_data.get("ct_image"),
        target_size=(config.DEFAULT_IMAGE_WIDTH, config.DEFAULT_IMAGE_HEIGHT),
        as_rgb=False
    )
    ct_img_rgb = load_image_safe(
        patient_data.get("ct_image"),
        target_size=(config.DEFAULT_IMAGE_WIDTH, config.DEFAULT_IMAGE_HEIGHT),
        as_rgb=True
    )
    pet_img = load_image_safe(
        patient_data.get("pet_image"),
        target_size=(config.DEFAULT_IMAGE_WIDTH, config.DEFAULT_IMAGE_HEIGHT),
        as_rgb=True
    )
    gt_mask = load_mask_safe(
        patient_data.get("ground_truth"),
        target_size=(config.DEFAULT_IMAGE_WIDTH, config.DEFAULT_IMAGE_HEIGHT)
    )
    pred_mask = load_mask_safe(
        patient_data.get("prediction"),
        target_size=(config.DEFAULT_IMAGE_WIDTH, config.DEFAULT_IMAGE_HEIGHT)
    )
    heatmap_overlay = overlay_heatmap(
        ct_img_rgb,
        patient_data.get("heatmap"),
        target_size=(config.DEFAULT_IMAGE_WIDTH, config.DEFAULT_IMAGE_HEIGHT)
    )

    gt_img = create_mask_visual(
        gt_mask,
        target_size=(config.DEFAULT_IMAGE_WIDTH, config.DEFAULT_IMAGE_HEIGHT),
        color=(0, 220, 120)
    )
    pred_img = create_mask_visual(
        pred_mask,
        target_size=(config.DEFAULT_IMAGE_WIDTH, config.DEFAULT_IMAGE_HEIGHT),
        color=(220, 80, 80)
    )

    if show_overlay and ct_img_rgb is not None:
        overlay_img = overlay_mask(
            ct_img_rgb,
            pred_mask if pred_mask is not None else gt_mask,
            color=(255, 170, 35),
            alpha=0.35
        )
    else:
        overlay_img = create_placeholder_image(
            target_size=(config.DEFAULT_IMAGE_WIDTH, config.DEFAULT_IMAGE_HEIGHT),
            text="Overlay disabled"
        )

    return ct_img, pet_img, gt_img, pred_img, heatmap_overlay, overlay_img

def handle_load_patient(patient_id: str, show_overlay: bool = False) -> Tuple:
    """
    Handle loading a patient's data and populating all visualizations.
    Calls the backend API and handles errors gracefully.
    
    Args:
        patient_id (str): The patient ID to load
        show_overlay (bool): Whether to render the overlay visualization
        
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
    
    ct_img, pet_img, gt_img, pred_img, heatmap_img, overlay_img = _prepare_patient_images(
        patient_data,
        show_overlay=show_overlay
    )

    # Extract metrics from response
    metrics = patient_data.get("metrics", {})
    dice = float(safe_get_nested_value(metrics, ["dice_score"], 0.0))
    iou = float(safe_get_nested_value(metrics, ["iou_score"], 0.0))
    hausdorff = float(safe_get_nested_value(metrics, ["hausdorff_distance"], 0.0))
    sensitivity = float(safe_get_nested_value(metrics, ["sensitivity"], 0.0))
    specificity = float(safe_get_nested_value(metrics, ["specificity"], 0.0))
    confidence = float(safe_get_nested_value(metrics, ["confidence"], 0.0))
    lesion_volume = float(safe_get_nested_value(metrics, ["lesion_volume"], 0.0))
    sphericity = float(safe_get_nested_value(metrics, ["sphericity"], 0.0))
    max_diameter = float(safe_get_nested_value(metrics, ["max_diameter"], 0.0))
    mean_density = float(safe_get_nested_value(metrics, ["mean_density"], 0.0))
    
    summary_html = generate_clinical_report_html(patient_data)
    
    return (
        ct_img, pet_img, gt_img, pred_img, heatmap_img, overlay_img,
        dice, iou, hausdorff, sensitivity, specificity,
        confidence, lesion_volume, sphericity, max_diameter, mean_density,
        status_msg, summary_html, patient_data
    )


def handle_overlay_toggle(patient_data: dict, show_overlay: bool) -> Tuple:
    """
    Handle toggling the overlay visualization without re-fetching data.
    Uses the stored patient data state.
    """
    if not patient_data:
        return (None,) * 6  # Return empty images if no data
        
    ct_img, pet_img, gt_img, pred_img, heatmap_img, overlay_img = _prepare_patient_images(
        patient_data,
        show_overlay=show_overlay
    )
    
    return ct_img, pet_img, gt_img, pred_img, heatmap_img, overlay_img


def handle_clear_data() -> Tuple:
    """
    Handle clearing all displayed data and returning to initial state.
    
    Returns:
        Tuple: All outputs reset to default/empty values
    """
    status = format_status_message("Data cleared", "info")
    return generate_empty_outputs(status)


def handle_load_random_patient(show_overlay: bool = False) -> Tuple:
    """
    Handle loading a random patient using the backend API or demo fallback.
    
    Args:
        show_overlay (bool): Whether to render the overlay visualization
        
    Returns:
        Tuple: All outputs for the dashboard components
    """
    success, patient_data, status_msg = load_random_patient_data(use_fallback=True)
    
    if not success:
        return generate_empty_outputs(status_msg)
    
    ct_img, pet_img, gt_img, pred_img, heatmap_img, overlay_img = _prepare_patient_images(
        patient_data,
        show_overlay=show_overlay
    )
    
    metrics = patient_data.get("metrics", {})
    dice = float(safe_get_nested_value(metrics, ["dice_score"], 0.0))
    iou = float(safe_get_nested_value(metrics, ["iou_score"], 0.0))
    hausdorff = float(safe_get_nested_value(metrics, ["hausdorff_distance"], 0.0))
    sensitivity = float(safe_get_nested_value(metrics, ["sensitivity"], 0.0))
    specificity = float(safe_get_nested_value(metrics, ["specificity"], 0.0))
    confidence = float(safe_get_nested_value(metrics, ["confidence"], 0.0))
    lesion_volume = float(safe_get_nested_value(metrics, ["lesion_volume"], 0.0))
    sphericity = float(safe_get_nested_value(metrics, ["sphericity"], 0.0))
    max_diameter = float(safe_get_nested_value(metrics, ["max_diameter"], 0.0))
    mean_density = float(safe_get_nested_value(metrics, ["mean_density"], 0.0))
    
    summary_html = generate_clinical_report_html(patient_data)
    
    return (
        ct_img, pet_img, gt_img, pred_img, heatmap_img, overlay_img,
        dice, iou, hausdorff, sensitivity, specificity,
        confidence, lesion_volume, sphericity, max_diameter, mean_density,
        status_msg, summary_html, patient_data
    )


def generate_empty_outputs(status_message: str) -> Tuple:
    """
    Generate empty/default outputs for all dashboard components.
    
    Args:
        status_message (str): Status message to display
        
    Returns:
        Tuple: All empty/default outputs
    """
    empty_img = create_placeholder_image(
        target_size=(config.DEFAULT_IMAGE_WIDTH, config.DEFAULT_IMAGE_HEIGHT)
    )
    
    return (
        empty_img, empty_img, empty_img, empty_img, empty_img, empty_img,
        0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0,
        status_message,
        generate_clinical_report_html({}),
        {}
    )



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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        :root {
            --medical-blue: #0066CC;
            --medical-slate: #64748b;
            --medical-emerald: #10b981;
        }
        
        .gradio-container {
            font-family: 'Inter', -apple-system, sans-serif !important;
            background-color: #f8fafc !important;
        }
        
        .header-title {
            text-align: center;
            font-size: 2.8em !important;
            font-weight: 700 !important;
            margin-bottom: 5px !important;
            background: linear-gradient(135deg, #0066CC 0%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.02em;
        }
        
        .header-subtitle {
            text-align: center;
            font-size: 1.2em !important;
            color: #64748b !important;
            margin-bottom: 40px !important;
            font-weight: 400;
        }
        
        #metrics-container, #image-display-container {
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            background-color: white !important;
            padding: 24px !important;
            transition: transform 0.2s ease-in-out;
        }
        
        #metrics-container:hover {
            transform: translateY(-2px);
        }
        
        .metric-card {
            border: none !important;
            background-color: #f1f5f9 !important;
            border-radius: 10px !important;
            padding: 10px !important;
            transition: all 0.2s ease;
        }
        
        .metric-card:hover {
            background-color: #e2e8f0 !important;
            box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.05) !important;
        }
        
        .metric-card label {
            font-size: 0.85em !important;
            color: #475569 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600 !important;
        }
        
        .metric-card input {
            font-size: 1.4em !important;
            font-weight: 700 !important;
            color: #0f172a !important;
        }
        
        button.primary {
            background: linear-gradient(135deg, #0066CC 0%, #2563eb 100%) !important;
            border: none !important;
            box-shadow: 0 10px 15px -3px rgba(0, 102, 204, 0.3) !important;
        }
        
        button.primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 20px 25px -5px rgba(0, 102, 204, 0.4) !important;
        }
        
        .gr-check-radio {
            accent-color: #0066CC !important;
        }
        
        /* Loading animation */
        .loading {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: .7; }
        /* Clinical Report Styles */
        .clinical-report-container {
            padding: 5px;
            color: #1e293b;
        }
        
        .report-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .patient-badge {
            font-weight: 700;
            color: #64748b;
            font-size: 0.9em;
        }
        
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
        }
        
        .report-section {
            margin-bottom: 25px;
        }
        
        .report-section h4 {
            margin: 0 0 10px 0;
            color: #0f172a;
            font-size: 1.1em;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 12px;
        }
        
        .metric-item {
            background: #f8fafc;
            padding: 10px;
            border-radius: 8px;
            border-left: 3px solid #3b82f6;
        }
        
        .metric-item .label {
            font-size: 0.75em;
            color: #64748b;
            text-transform: uppercase;
            font-weight: 600;
        }
        
        .metric-item .value {
            font-size: 1.2em;
            font-weight: 700;
        }
        
        .summary-text {
            font-size: 0.95em;
            line-height: 1.5;
            color: #475569;
        }
        
        .report-list {
            margin: 0;
            padding-left: 20px;
            font-size: 0.95em;
            color: #475569;
        }
        
        .report-list li {
            margin-bottom: 5px;
        }
        
        .recommendation-box {
            background: #f0f9ff;
            border: 1px solid #bae6fd;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .rec-title {
            display: block;
            font-weight: 700;
            color: #0369a1;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        
        .report-timestamp {
            margin-top: 15px;
            font-size: 0.75em;
            color: #94a3b8;
            text-align: right;
        }
        """
    ) as app:
        
        # Patient data state to store loaded data
        patient_data_state = gr.State({})
        
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
            with gr.Column(scale=1, min_width=320):
                gr.Markdown("### ⚙️ Controls")
                
                # Patient Selector
                patient_id_input, load_button, random_button, clear_button = create_patient_selector_section()
                
                gr.Markdown("---")
                
                # Status Output
                status_output = gr.Textbox(
                    label="Status",
                    value=config.STATUS_PLACEHOLDER,
                    interactive=False,
                    lines=3
                )
                
                gr.Markdown("---")
                
                # Additional Settings
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
                    2. Click "Load Patient" or "Random Patient"
                    3. Review CT, PET, ground truth, prediction, and XAI heatmap
                    4. Inspect the clinical metrics below
                    5. Use "Clear" to reset all outputs
                    """)
            
            # ================================================================
            # Right Panel - Displays
            # ================================================================
            with gr.Column(scale=2):
                gr.Markdown("### 📊 Analysis & Results")
                
                # Image Display Section
                ct_image, pet_image, gt_image, pred_image, heatmap_image, overlay_image = create_image_display_section()
                
                # Metrics Section
                (dice_score, iou_score, hausdorff_dist, 
                 sensitivity, specificity, confidence_score,
                 lesion_volume, sphericity, max_diameter, mean_density) = create_metrics_cards_section()
                
                # Summary Section
                summary_output = create_summary_section()
        
        # ====================================================================
        # Event Handlers
        # ====================================================================
        
        # Load patient button click handler
        load_button.click(
            fn=handle_load_patient,
            inputs=[patient_id_input, show_overlay],
            outputs=[
                ct_image, pet_image, gt_image, pred_image, heatmap_image, overlay_image,
                dice_score, iou_score, hausdorff_dist, sensitivity, specificity,
                confidence_score, lesion_volume, sphericity, max_diameter, mean_density,
                status_output, summary_output, patient_data_state
            ],
            queue=False
        )
        
        # Random patient button click handler
        random_button.click(
            fn=handle_load_random_patient,
            inputs=[show_overlay],
            outputs=[
                ct_image, pet_image, gt_image, pred_image, heatmap_image, overlay_image,
                dice_score, iou_score, hausdorff_dist, sensitivity, specificity,
                confidence_score, lesion_volume, sphericity, max_diameter, mean_density,
                status_output, summary_output, patient_data_state
            ],
            queue=False
        )
        
        # Clear button click handler
        clear_button.click(
            fn=handle_clear_data,
            inputs=[],
            outputs=[
                ct_image, pet_image, gt_image, pred_image, heatmap_image, overlay_image,
                dice_score, iou_score, hausdorff_dist, sensitivity, specificity,
                confidence_score, lesion_volume, sphericity, max_diameter, mean_density,
                status_output, summary_output, patient_data_state
            ],
            queue=False
        )
        
        # Update overlay visibility when the toggle changes
        show_overlay.change(
            fn=handle_overlay_toggle,
            inputs=[patient_data_state, show_overlay],
            outputs=[
                ct_image, pet_image, gt_image, pred_image, heatmap_image, overlay_image
            ],
            queue=False
        )
        
        # Load default patient on app start
        app.load(
            fn=handle_load_patient,
            inputs=[patient_id_input, show_overlay],
            outputs=[
                ct_image, pet_image, gt_image, pred_image, heatmap_image, overlay_image,
                dice_score, iou_score, hausdorff_dist, sensitivity, specificity,
                confidence_score, lesion_volume, sphericity, max_diameter, mean_density,
                status_output, summary_output, patient_data_state
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
