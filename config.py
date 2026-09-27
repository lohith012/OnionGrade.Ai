import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "onionvision-ai-secret-key-2026-secure")
    
    # AI Mode: 'real' or 'demo'
    AI_MODE = os.getenv("AI_MODE", "demo").lower()
    
    # Model path
    MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "best.pt"))
    
    # Upload and Report Directories
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    REPORTS_FOLDER = str(BASE_DIR / "reports")
    STATIC_FOLDER = str(BASE_DIR / "static")
    
    # Max file upload size (default: 10MB)
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_SIZE", 10 * 1024 * 1024))
    
    # Allowed file formats
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    
    # Database
    DATABASE_PATH = str(BASE_DIR / "onionvision.db")
    
    # Quality Scoring weights
    SCORE_WEIGHTS = {
        "good": 100,
        "damaged": 50,
        "sprouted": 40,
        "rotten": 0
    }
    
    # Grading Thresholds
    GRADE_THRESHOLDS = [
        {"min_score": 90, "grade": "Grade A", "description": "Premium Export Quality – Minimal to zero defects"},
        {"min_score": 75, "grade": "Grade B", "description": "Good Domestic Market Quality – Minor acceptable defects"},
        {"min_score": 60, "grade": "Grade C", "description": "Fair / Processing Grade – Significant defects present"},
        {"min_score": 0,  "grade": "URS",     "description": "Under Review / Substandard – High spoilage risk"}
    ]
    
    # Visual Palette for Classes
    CLASS_METADATA = {
        "good": {
            "name": "Good Quality",
            "hex": "#10B981",       # Emerald Green
            "rgb": [16, 185, 129],
            "bgr": [46, 195, 22],
            "badge_class": "badge-success",
            "icon": "bi-check-circle-fill"
        },
        "damaged": {
            "name": "Damaged / Bruised",
            "hex": "#F59E0B",       # Amber Orange
            "rgb": [245, 158, 11],
            "bgr": [11, 158, 245],
            "badge_class": "badge-warning",
            "icon": "bi-exclamation-triangle-fill"
        },
        "rotten": {
            "name": "Rotten / Moldy",
            "hex": "#EF4444",       # Crimson Red
            "rgb": [239, 68, 68],
            "bgr": [68, 68, 239],
            "badge_class": "badge-danger",
            "icon": "bi-x-circle-fill"
        },
        "sprouted": {
            "name": "Sprouted",
            "hex": "#8B5CF6",       # Violet
            "rgb": [139, 92, 246],
            "bgr": [246, 92, 139],
            "badge_class": "badge-purple",
            "icon": "bi-flower1"
        }
    }
