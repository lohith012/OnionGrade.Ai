import cv2
import numpy as np
import os
from PIL import Image

def validate_image(file_path: str) -> bool:
    """
    Validates that the file exists, is non-empty, and can be read by PIL & OpenCV.
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return False
    
    try:
        with Image.open(file_path) as img:
            img.verify()
        
        # Also check with OpenCV
        cv_img = cv2.imread(file_path)
        if cv_img is None or cv_img.size == 0:
            return False
            
        return True
    except Exception:
        return False

def resize_image(image: np.ndarray, max_dim: int = 1280) -> np.ndarray:
    """
    Resizes image maintaining aspect ratio so neither dimension exceeds max_dim.
    """
    h, w = image.shape[:2]
    if max(h, w) <= max_dim:
        return image
    
    scale = max_dim / float(max(h, w))
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

def preprocess_image(image_path: str, target_size: int = 640) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Preprocesses the image for inspection and AI inference.
    Returns:
        processed_cv: Preprocessed OpenCV image ready for inference/drawing
        original_cv: Loaded original image
        metadata: Metadata about dimensions, contrast, brightness
    """
    original_cv = cv2.imread(image_path)
    if original_cv is None:
        raise ValueError("Could not read image file with OpenCV")

    h, w, c = original_cv.shape
    
    # Analyze brightness and contrast
    gray = cv2.cvtColor(original_cv, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))
    
    # Mild denoising if noisy, without blurring edges
    denoised = cv2.fastNlMeansDenoisingColored(original_cv, None, 3, 3, 7, 21) if contrast > 80 else original_cv.copy()
    
    # Optional auto-brightness normalization if too dark
    if brightness < 60:
        # Boost exposure slightly
        alpha = 1.3
        beta = 20
        normalized = cv2.convertScaleAbs(denoised, alpha=alpha, beta=beta)
    else:
        normalized = denoised
        
    metadata = {
        "width": w,
        "height": h,
        "channels": c,
        "brightness": round(brightness, 1),
        "contrast": round(contrast, 1),
        "aspect_ratio": round(w / h, 2)
    }
    
    return normalized, original_cv, metadata
