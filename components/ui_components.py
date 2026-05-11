"""
UI Components for the ECPC-IDS Dashboard.
Contains functions to build different sections of the interface.
"""

import gradio as gr
import numpy as np
from typing import Callable, List, Tuple
import config
from utils.helpers import format_metric_value, format_percentage


def create_patient_selector_section() -> Tuple[gr.Textbox, gr.Button, gr.Button]:
    """
    Create the patient selector control panel section.
    
    Returns:
        Tuple containing:
        - patient_id_input: Textbox for patient ID
        - load_button: Button to load patient data
        - clear_button: Button to clear current data
    """
    with gr.Group(label="👤 Patient Selection", scale=1):
        gr.Markdown("#### Load Patient Data")
        
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
            clear_button = gr.Button(
                "🗑️ Clear",
                variant="secondary",
                scale=1
            )
    
    return patient_id_input, load_button, clear_button


def create_image_display_section() -> Tuple[gr.Image, gr.Dropdown, gr.Image, gr.Image, gr.Image, gr.Image]:
    """
    Create the image display section with multiple imaging modalities.
    
    Returns:
        Tuple containing image and dropdown components for medical imaging display
    """
    with gr.Group(label="🖼️ Medical Imaging", scale=2):
        gr.Markdown("#### CT/PET and Analysis Visualizations")
        
        with gr.Row():
            # CT Image
            with gr.Column(scale=1):
                gr.Markdown("**CT Scan**")
                ct_image = gr.Image(
                    label="CT",
                    type="numpy",
                    interactive=False,
                    min_width=300
                )
            
            # PET Image
            with gr.Column(scale=1):
                gr.Markdown("**PET Scan**")
                pet_image = gr.Image(
                    label="PET",
                    type="numpy",
                    interactive=False,
                    min_width=300
                )
        
        with gr.Row():
            # Ground Truth
            with gr.Column(scale=1):
                gr.Markdown("**Ground Truth**")
                gt_image = gr.Image(
                    label="Ground Truth Segmentation",
                    type="numpy",
                    interactive=False,
                    min_width=300
                )
            
            # Prediction
            with gr.Column(scale=1):
                gr.Markdown("**Model Prediction**")
                pred_image = gr.Image(
                    label="Model Prediction",
                    type="numpy",
                    interactive=False,
                    min_width=300
                )
        
        with gr.Row():
            # Heatmap
            with gr.Column(scale=1):
                gr.Markdown("**Explainability Heatmap**")
                heatmap_image = gr.Image(
                    label="XAI Heatmap (Attribution)",
                    type="numpy",
                    interactive=False,
                    min_width=300
                )
            
            # Placeholder for additional analysis
            with gr.Column(scale=1):
                gr.Markdown("**Analysis Info**")
                analysis_info = gr.Image(
                    label="Placeholder",
                    type="numpy",
                    interactive=False,
                    min_width=300
                )
    
    return ct_image, pet_image, gt_image, pred_image, heatmap_image, analysis_info


def create_metrics_cards_section() -> Tuple[gr.Number, gr.Number, gr.Number, gr.Number, gr.Number]:
    """
    Create metrics display cards showing segmentation quality metrics.
    
    Returns:
        Tuple containing metric output components
    """
    with gr.Group(label="📊 Performance Metrics", scale=1):
        gr.Markdown("#### Segmentation Quality Metrics")
        
        with gr.Row():
            dice_score = gr.Number(
                label="Dice Score",
                value=0.0,
                interactive=False,
                precision=3
            )
            iou_score = gr.Number(
                label="IoU (Jaccard)",
                value=0.0,
                interactive=False,
                precision=3
            )
            hausdorff = gr.Number(
                label="Hausdorff Distance",
                value=0.0,
                interactive=False,
                precision=3
            )
        
        with gr.Row():
            sensitivity = gr.Number(
                label="Sensitivity (Recall)",
                value=0.0,
                interactive=False,
                precision=3
            )
            specificity = gr.Number(
                label="Specificity",
                value=0.0,
                interactive=False,
                precision=3
            )
    
    return dice_score, iou_score, hausdorff, sensitivity, specificity


def create_summary_section() -> Tuple[gr.Textbox, gr.Textbox]:
    """
    Create the summary and status information section.
    
    Returns:
        Tuple containing:
        - status_output: Status message display
        - summary_output: Detailed summary information
    """
    with gr.Group(label="📋 Status & Summary", scale=2):
        gr.Markdown("#### Analysis Status & Results")
        
        status_output = gr.Textbox(
            label="Status",
            value=config.STATUS_PLACEHOLDER,
            interactive=False,
            lines=2
        )
        
        summary_output = gr.Textbox(
            label="Summary Information",
            value="Load a patient to see analysis results.",
            interactive=False,
            lines=6
        )
    
    return status_output, summary_output


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
