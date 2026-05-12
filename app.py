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
    generate_clinical_report_html,
    export_report_to_file
)
from components.ui_components import (
    create_patient_selector_section,
    create_image_display_section,
    create_metrics_cards_section,
    create_summary_section,
    create_dummy_image
)
from services.api_client import load_patient_data, load_random_patient_data


DASHBOARD_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #0066CC;
    --bg-app: #f8fafc;
    --bg-sidebar: #ffffff;
    --bg-card: #ffffff;
    --text-main: #0f172a;
    --text-muted: #64748b;
    --border: #e2e8f0;
    --sidebar-active: linear-gradient(90deg, #8b5cf6 0%, #3b82f6 100%);
    --accent-cyan: #06b6d4;
    --status-bar: #f1f5f9;
}

.dark {
    --bg-app: #0b0f19;
    --bg-sidebar: #0b0f19;
    --bg-card: #161e2e;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --border: #1f2937;
    --sidebar-active: linear-gradient(90deg, #8b5cf6 0%, #3b82f6 100%);
    --accent-cyan: #06b6d4;
    --status-bar: #0f172a;
}

.gradio-container {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg-app) !important;
    color: var(--text-main) !important;
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Sidebar Styling */
#sidebar-column {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
    height: 100vh !important;
    padding: 20px !important;
    position: sticky !important;
    top: 0;
}

.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.5em;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 40px;
}

.sidebar-logo span {
    color: #06b6d4;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 8px;
    color: var(--text-muted);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.nav-item.active {
    background: var(--sidebar-active);
    color: white !important;
}

.nav-item:hover:not(.active) {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-main);
}

.upload-button {
    background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px !important;
    font-weight: 700 !important;
    width: 100% !important;
    margin-top: auto !important;
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3) !important;
}

/* Top Bar Styling */
#top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 15px 40px;
    background: var(--bg-app);
    border-bottom: 1px solid var(--border);
}

.patient-badge {
    background: var(--bg-card);
    border: 1px solid #06b6d4;
    color: #06b6d4;
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.9em;
}

/* Main Dashboard Styling */
#main-dashboard-content {
    padding: 40px !important;
}

.dashboard-title {
    font-size: 2.8em !important;
    font-weight: 700 !important;
    margin-bottom: 10px !important;
    color: var(--text-main) !important;
}

.dashboard-subtitle {
    color: var(--text-muted) !important;
    font-size: 1.1em !important;
    margin-bottom: 30px !important;
}

.status-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
}

.status-chip .dot {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10b981;
}

/* Imaging Grid Styling */
#image-display-container {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.image-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 15px !important;
    overflow: hidden;
}

.image-card-title {
    font-size: 0.9em;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 10px;
}

.accuracy-badge {
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75em;
    font-weight: 700;
}

/* Bottom Bar */
#bottom-status-bar {
    background: var(--status-bar);
    border-top: 1px solid var(--border);
    padding: 10px 40px;
    display: flex;
    justify-content: space-between;
    font-size: 0.8em;
    color: var(--text-muted);
}

/* Animations */
.gradio-container, .nav-item, .image-card {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Gradio Component Overrides */
.gr-input, .gr-button:not(.primary, .upload-button) {
    background-color: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text-main) !important;
}

.dark .gr-input, .dark .gr-button:not(.primary, .upload-button) {
    background-color: #1e293b !important;
    border-color: var(--border) !important;
}

.image-card .gr-image {
    border: none !important;
    background: transparent !important;
}

/* Clinical Report Enhancements */
.clinical-report-container {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    padding: 24px !important;
    border: 1px solid var(--border) !important;
}

.report-section {
    margin-bottom: 25px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 15px;
}

.report-section:last-child {
    border-bottom: none;
}

.report-section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 700;
    color: var(--text-main);
    font-size: 1.1em;
    margin-bottom: 15px;
}

.metric-item {
    background: var(--bg-app);
    padding: 12px;
    border-radius: 8px;
    border-left: 4px solid #cbd5e1;
    margin-bottom: 10px;
}

.metric-item.green { border-left-color: #10b981; }
.metric-item.blue { border-left-color: #3b82f6; }
.metric-item.amber { border-left-color: #f59e0b; }
.metric-item.red { border-left-color: #ef4444; }

.status-badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75em;
    font-weight: 600;
}

.status-badge.green { background: #dcfce7; color: #166534; }
.status-badge.blue { background: #dbeafe; color: #1e40af; }
.status-badge.amber { background: #fef3c7; color: #92400e; }
.status-badge.red { background: #fee2e2; color: #991b1b; }

.dark .status-badge.green { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.dark .status-badge.blue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.dark .status-badge.amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.dark .status-badge.red { background: rgba(239, 68, 68, 0.15); color: #f87171; }

/* Metric Card Styles */
.metric-card {
    border: none !important;
    background-color: var(--bg-app) !important;
    border-radius: 10px !important;
    padding: 10px !important;
}

.metric-card label {
    font-size: 0.85em !important;
    color: var(--text-muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600 !important;
}

.metric-card input {
    font-size: 1.4em !important;
    font-weight: 700 !important;
    color: var(--text-main) !important;
}
"""
# ============================================================================
# Theme & Styling (Gradio 6.0 compatibility)
# ============================================================================

DASHBOARD_THEME = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate"
)

# ============================================================================
# Event Handlers
# ============================================================================

def _prepare_patient_images(patient_data: dict, show_overlay: bool = False, overlay_alpha: float = 0.35) -> tuple:
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
            alpha=overlay_alpha
        )
    else:
        overlay_img = create_placeholder_image(
            target_size=(config.DEFAULT_IMAGE_WIDTH, config.DEFAULT_IMAGE_HEIGHT),
            text="Overlay disabled"
        )

    return ct_img, pet_img, gt_img, pred_img, heatmap_overlay, overlay_img

def handle_load_patient(patient_id: str, show_overlay: bool = False, overlay_opacity: float = 0.35, progress=gr.Progress()) -> Tuple:
    """
    Handle loading a patient's data and populating all visualizations.
    Calls the backend API and handles errors gracefully.
    """
    progress(0.1, desc="Validating patient ID...")
    # Validate patient ID
    is_valid, error_msg = validate_patient_id(patient_id)
    if not is_valid:
        status = format_status_message(error_msg, "error")
        return generate_empty_outputs(status)
    
    progress(0.3, desc="Fetching imaging data from backend...")
    # Load patient data from backend API (with fallback support)
    success, patient_data, status_msg = load_patient_data(
        patient_id,
        use_fallback=True
    )
    
    if not success:
        return generate_empty_outputs(status_msg)
    
    progress(0.6, desc="Rendering multimodal visualizations...")
    ct_img, pet_img, gt_img, pred_img, heatmap_img, overlay_img = _prepare_patient_images(
        patient_data,
        show_overlay=show_overlay,
        overlay_alpha=overlay_opacity
    )

    progress(0.8, desc="Generating AI clinical report...")

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


def handle_overlay_toggle(patient_data: dict, show_overlay: bool, overlay_opacity: float = 0.35) -> Tuple:
    """
    Handle toggling the overlay visualization without re-fetching data.
    Uses the stored patient data state.
    """
    if not patient_data:
        return (None,) * 6  # Return empty images if no data
        
    ct_img, pet_img, gt_img, pred_img, heatmap_img, overlay_img = _prepare_patient_images(
        patient_data,
        show_overlay=show_overlay,
        overlay_alpha=overlay_opacity
    )
    
    return ct_img, pet_img, gt_img, pred_img, heatmap_img, overlay_img


def handle_export_report(patient_data: dict) -> str:
    """
    Handle exporting the current clinical report.
    """
    if not patient_data or not patient_data.get("patient_id"):
        return None
        
    return export_report_to_file(patient_data, file_format="markdown")


def handle_clear_data() -> Tuple:
    """
    Handle clearing all displayed data and returning to initial state.
    
    Returns:
        Tuple: All outputs reset to default/empty values
    """
    status = format_status_message("Data cleared", "info")
    return generate_empty_outputs(status)


def handle_load_random_patient(show_overlay: bool = False, overlay_opacity: float = 0.35, progress=gr.Progress()) -> Tuple:
    """
    Handle loading a random patient using the backend API or demo fallback.
    """
    progress(0.2, desc="Selecting random case...")
    success, patient_data, status_msg = load_random_patient_data(use_fallback=True)
    
    if not success:
        return generate_empty_outputs(status_msg)
    
    progress(0.5, desc="Preparing multimodal views...")
    ct_img, pet_img, gt_img, pred_img, heatmap_img, overlay_img = _prepare_patient_images(
        patient_data,
        show_overlay=show_overlay,
        overlay_alpha=overlay_opacity
    )
    
    progress(0.8, desc="Finalizing AI report...")
    
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
    """
    with gr.Blocks(title=config.TITLE, js="""
        () => {
            const theme = localStorage.getItem('gradio-theme-preference');
            if (theme === 'dark') {
                document.body.classList.add('dark');
            }
        }
    """) as app:
        
        patient_data_state = gr.State({})
        
        with gr.Row(equal_height=True):
            # ================================================================
            # Sidebar Navigation
            # ================================================================
            with gr.Column(scale=1, min_width=280, elem_id="sidebar-column"):
                gr.HTML("""
                <div class="sidebar-logo">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" stroke-width="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                    </svg>
                    Diagnostic <span>Dashboard</span>
                </div>
                """)
                
                gr.HTML("""
                <div class="nav-item active">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                    </svg>
                    Diagnostics
                </div>
                """)
                
                gr.Markdown("---")
                
                # Patient Selection integrated here for now
                patient_id_input = gr.Textbox(
                    label="Active Patient",
                    value=config.DEFAULT_PATIENT_ID,
                    elem_id="patient-id-sidebar"
                )
                
                with gr.Row():
                    load_button = gr.Button("Load", variant="primary", size="sm")
                    random_button = gr.Button("Random", variant="secondary", size="sm")
                
                with gr.Row():
                    clear_button = gr.Button("Clear", size="sm")
                    export_button = gr.Button("Export", size="sm")

                report_file = gr.File(label="Clinical Report", visible=False)
                
                # Hidden variables
                status_output = gr.Textbox(visible=False)
                show_overlay = gr.Checkbox(value=False, visible=False)
                confidence_threshold = gr.Slider(visible=False)
                overlay_opacity = gr.Slider(value=0.35, visible=False)
                

            # ================================================================
            # Main Content Area
            # ================================================================
            with gr.Column(scale=4):
                # Top Bar
                with gr.Row(elem_id="top-bar"):
                    gr.HTML("""<div style="font-size: 1.2em; font-weight: 600; color: var(--text-main); flex-grow: 1;">Endometriosis- Segmentation and XAI Dashboard</div>""")
                    dark_mode = gr.Checkbox(label="🌙", value=False, elem_id="dark-mode-toggle")

                # Dashboard Content
                with gr.Column(elem_id="main-dashboard-content"):

                    # Imaging Grid
                    with gr.Row():
                        with gr.Column(elem_classes="image-card"):
                            gr.Markdown("CT Scan - Structural", elem_classes="image-card-title")
                            ct_image = gr.Image(show_label=False, interactive=False)
                        with gr.Column(elem_classes="image-card"):
                            gr.Markdown("PET Scan - Metabolic", elem_classes="image-card-title")
                            pet_image = gr.Image(show_label=False, interactive=False)
                    
                    with gr.Row():
                        with gr.Column(elem_classes="image-card"):
                            with gr.Row():
                                gr.Markdown("Segmentation Mask", elem_classes="image-card-title")
                                gr.HTML("""<div class="accuracy-badge">ACC: 98.4%</div>""")
                            pred_image = gr.Image(show_label=False, interactive=False)
                        with gr.Column(elem_classes="image-card"):
                            gr.Markdown("Explainable Attention Map", elem_classes="image-card-title")
                            heatmap_image = gr.Image(show_label=False, interactive=False)

                    # Metrics Section
                    (dice_score, iou_score, hausdorff_dist, 
                     sensitivity, specificity, confidence_score,
                     lesion_volume, sphericity, max_diameter, mean_density) = create_metrics_cards_section()

                    # Report Section
                    summary_output = create_summary_section()
                    
                    # Hidden images to keep logic happy
                    with gr.Row(visible=False):
                        gt_image = gr.Image()
                        overlay_image = gr.Image()

        
        # ====================================================================
        # Event Handlers
        # ====================================================================
        
        # Load patient button click handler
        load_button.click(
            fn=handle_load_patient,
            inputs=[patient_id_input, show_overlay, overlay_opacity],
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
            inputs=[show_overlay, overlay_opacity],
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
            inputs=[patient_data_state, show_overlay, overlay_opacity],
            outputs=[
                ct_image, pet_image, gt_image, pred_image, heatmap_image, overlay_image
            ],
            queue=False
        )
        
        overlay_opacity.change(
            fn=handle_overlay_toggle,
            inputs=[patient_data_state, show_overlay, overlay_opacity],
            outputs=[
                ct_image, pet_image, gt_image, pred_image, heatmap_image, overlay_image
            ],
            queue=False
        )
        
        # Dark mode toggle handler (JS only)
        dark_mode.change(
            fn=None,
            inputs=[dark_mode],
            outputs=None,
            js="""
            (checked) => {
                const theme = checked ? 'dark' : 'light';
                document.body.classList.toggle('dark', checked);
                localStorage.setItem('gradio-theme-preference', theme);
                
                // Also target the container specifically just in case
                const container = document.querySelector('.gradio-container');
                if (container) {
                    container.classList.toggle('dark', checked);
                }
            }
            """
        )
        
        export_button.click(
            fn=handle_export_report,
            inputs=[patient_data_state],
            outputs=[report_file],
            queue=False
        ).then(
            fn=lambda: gr.update(visible=True),
            outputs=[report_file]
        )
        
        # Load default patient on app start
        app.load(
            fn=handle_load_patient,
            inputs=[patient_id_input, show_overlay, overlay_opacity],
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
        theme=DASHBOARD_THEME,
        css=DASHBOARD_CSS,
        share=False,
        show_error=True,
        debug=True
    )
