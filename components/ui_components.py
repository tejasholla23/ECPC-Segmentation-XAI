"""
UI Components for the ECPC-IDS Dashboard.
Contains functions to build different sections of the interface.
"""

import gradio as gr
import numpy as np
from typing import Callable, List, Tuple
import config
from utils.helpers import format_metric_value, format_percentage


def create_patient_selector_section() -> Tuple[gr.Textbox, gr.Button, gr.Button, gr.Button]:
    """
    Create the patient selector control panel section.
    
    Returns:
        Tuple containing:
        - patient_id_input: Textbox for patient ID
        - load_button: Button to load patient data
        - random_button: Button to fetch a random patient
        - clear_button: Button to clear current data
    """
    with gr.Column(variant="panel", scale=1):
        gr.Markdown("#### 👤 Patient Selection")
        
        patient_id_input = gr.Textbox(
            label="Patient ID",
            placeholder="Enter patient ID (e.g., PATIENT_001)",
            value=config.DEFAULT_PATIENT_ID,
            interactive=True,
            scale=2
        )
        
        with gr.Row():
            load_button = gr.Button(
                "🔄 Load Patient",
                variant="primary",
                scale=1,
                size="lg"
            )
            random_button = gr.Button(
                "🎲 Random Patient",
                variant="secondary",
                scale=1
            )
        
        with gr.Row():
            clear_button = gr.Button(
                "🗑️ Clear",
                variant="secondary",
                scale=1
            )
            export_button = gr.Button(
                "📥 Export Report",
                variant="secondary",
                scale=1
            )
            
        # Hidden file component for download
        report_file = gr.File(label="Download Clinical Report", visible=False)
    
    return patient_id_input, load_button, random_button, clear_button, export_button, report_file


def create_image_display_section() -> Tuple[gr.Image, gr.Image, gr.Image, gr.Image, gr.Image, gr.Image]:
    """
    Create the image display section with multiple imaging modalities.
    
    Returns:
        Tuple containing image components for medical imaging display
    """
    with gr.Column(elem_id="image-display-container", scale=2, variant="panel"):
        gr.Markdown("#### 🧬 Imaging Modalities & Analysis")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("**CT Scan**")
                ct_image = gr.Image(
                    label="CT Scan",
                    type="numpy",
                    interactive=False,
                    min_width=320,
                    height=320
                )
            with gr.Column(scale=1):
                gr.Markdown("**PET Scan**")
                pet_image = gr.Image(
                    label="PET Scan",
                    type="numpy",
                    interactive=False,
                    min_width=320,
                    height=320
                )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("**Ground Truth Mask**")
                gt_image = gr.Image(
                    label="Ground Truth Mask",
                    type="numpy",
                    interactive=False,
                    min_width=320,
                    height=320
                )
            with gr.Column(scale=1):
                gr.Markdown("**Prediction Mask**")
                pred_image = gr.Image(
                    label="Prediction Mask",
                    type="numpy",
                    interactive=False,
                    min_width=320,
                    height=320
                )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("**XAI Heatmap Overlay**")
                heatmap_image = gr.Image(
                    label="Heatmap Overlay",
                    type="numpy",
                    interactive=False,
                    min_width=320,
                    height=320
                )
            with gr.Column(scale=1):
                gr.Markdown("**Overlay Mode**")
                overlay_image = gr.Image(
                    label="Overlay Visualization",
                    type="numpy",
                    interactive=False,
                    min_width=320,
                    height=320
                )
    
    return ct_image, pet_image, gt_image, pred_image, heatmap_image, overlay_image


def create_metrics_cards_section() -> Tuple[gr.Number, gr.Number, gr.Number, gr.Number, gr.Number, gr.Number, gr.Number, gr.Number, gr.Number, gr.Number]:
    """
    Create metrics display cards showing segmentation quality metrics.
    
    Returns:
        Tuple containing metric output components
    """
    with gr.Column(elem_id="metrics-container", scale=1, variant="panel"):
        gr.Markdown("#### 🩺 Clinical Analysis Metrics")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("**Model Performance**")
                with gr.Row():
                    dice_score = gr.Number(label="Dice Score", value=0.0, interactive=False, precision=3, elem_classes="metric-card")
                    iou_score = gr.Number(label="IoU", value=0.0, interactive=False, precision=3, elem_classes="metric-card")
                with gr.Row():
                    hausdorff = gr.Number(label="Hausdorff", value=0.0, interactive=False, precision=3, elem_classes="metric-card")
                    confidence_score = gr.Number(label="Confidence", value=0.0, interactive=False, precision=3, elem_classes="metric-card")
            
            with gr.Column(scale=1):
                gr.Markdown("**Statistical Reliability**")
                with gr.Row():
                    sensitivity = gr.Number(label="Sensitivity", value=0.0, interactive=False, precision=3, elem_classes="metric-card")
                    specificity = gr.Number(label="Specificity", value=0.0, interactive=False, precision=3, elem_classes="metric-card")
        
        gr.Markdown("---")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("**Lesion Geometry**")
                with gr.Row():
                    lesion_volume = gr.Number(label="Volume (mm³)", value=0.0, interactive=False, precision=1, elem_classes="metric-card")
                    sphericity = gr.Number(label="Sphericity", value=0.0, interactive=False, precision=3, elem_classes="metric-card")
                with gr.Row():
                    max_diameter = gr.Number(label="Max Diameter (mm)", value=0.0, interactive=False, precision=2, elem_classes="metric-card")
            
            with gr.Column(scale=1):
                gr.Markdown("**Radiomics Features**")
                with gr.Row():
                    mean_density = gr.Number(label="Mean Density (HU)", value=0.0, interactive=False, precision=1, elem_classes="metric-card")
    
    return (
        dice_score,
        iou_score,
        hausdorff,
        sensitivity,
        specificity,
        confidence_score,
        lesion_volume,
        sphericity,
        max_diameter,
        mean_density
    )


def create_summary_section() -> gr.HTML:
    """
    Create the clinical report section using HTML for rich formatting.
    
    Returns:
        gr.HTML: detailed summary output component
    """
    with gr.Column(elem_id="report-container", scale=2, variant="panel"):
        gr.Markdown("#### 📋 AI Clinical Report")
        summary_output = gr.HTML(
            value="""
            <div style="padding: 40px; text-align: center; color: #64748b;">
                <div style="font-size: 3em; margin-bottom: 20px;">📋</div>
                <div style="font-size: 1.2em;">Waiting for patient analysis...</div>
                <div style="font-size: 0.9em; margin-top: 10px;">Select a patient to generate AI diagnostic report.</div>
            </div>
            """,
            elem_id="clinical-report-output"
        )
    
    return summary_output


def create_dummy_image(shape: Tuple[int, int, int] = (400, 400, 3), image_type: str = "random") -> np.ndarray:
    """
    Create a dummy image for development/testing without backend.
    
    Args:
        shape: Image dimensions (height, width, channels)
        image_type: Type of dummy image ('random', 'checkerboard', 'gradient', 'empty')
        
    Returns:
        np.ndarray: Dummy image array
    """
    if image_type == "checkerboard":
        size = min(shape[0], shape[1]) // 20
        board = np.indices((shape[0], shape[1])).sum(axis=0) % (2 * size) < size
        img = np.stack([board] * shape[2], axis=-1).astype(np.uint8) * 200
        return img
    
    elif image_type == "gradient":
        x = np.linspace(0, 255, shape[1], dtype=np.uint8)
        img = np.tile(x, (shape[0], 1))
        if shape[2] == 3:
            img = np.stack([img, img[::-1], img * 0.5], axis=-1)
        else:
            img = img[:, :, np.newaxis]
        return img
    
    elif image_type == "empty":
        return np.ones(shape, dtype=np.uint8) * 50
    
    else:  # random
        return np.random.randint(0, 256, shape, dtype=np.uint8)


def create_dummy_segmentation_image(shape: Tuple[int, int, int] = (400, 400, 3)) -> np.ndarray:
    """
    Create a dummy medical segmentation image with a circular/oval lesion area.
    
    Args:
        shape: Image dimensions
        
    Returns:
        np.ndarray: Dummy segmentation image
    """
    img = np.ones(shape, dtype=np.uint8) * 30
    center_y, center_x = shape[0] // 2, shape[1] // 2
    radius_y, radius_x = shape[0] // 4, shape[1] // 4
    
    y, x = np.ogrid[:shape[0], :shape[1]]
    mask = ((x - center_x) ** 2 / (radius_x ** 2) + 
            (y - center_y) ** 2 / (radius_y ** 2)) <= 1
    
    img[mask] = 200
    return img


def create_dummy_heatmap(shape: Tuple[int, int, int] = (400, 400, 3)) -> np.ndarray:
    """
    Create a dummy XAI heatmap showing attribution/attention areas.
    
    Args:
        shape: Image dimensions
        
    Returns:
        np.ndarray: Dummy heatmap image
    """
    # Create a smooth gradient heatmap
    x = np.linspace(0, np.pi, shape[1])
    y = np.linspace(0, np.pi, shape[0])
    xx, yy = np.meshgrid(x, y)
    heatmap = (np.sin(xx) * np.sin(yy) + 1) / 2  # Values 0-1
    
    # Convert to colormap (red for high values, blue for low)
    r = (heatmap * 255).astype(np.uint8)
    b = ((1 - heatmap) * 255).astype(np.uint8)
    g = (np.ones_like(heatmap) * 100).astype(np.uint8)
    
    return np.stack([r, g, b], axis=-1)
