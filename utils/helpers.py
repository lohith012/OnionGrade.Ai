import os
import re
import uuid
import datetime
from werkzeug.utils import secure_filename
from config import Config

def generate_report_id() -> str:
    """Generates a structured report ID like ON-2026-A1B2."""
    year = datetime.datetime.now().year
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"ON-{year}-{unique_suffix}"

def allowed_file(filename: str) -> bool:
    """Checks if the filename has an allowed extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file_storage, target_folder: str) -> str:
    """
    Saves an uploaded file securely with a unique identifier to prevent overwriting.
    """
    os.makedirs(target_folder, exist_ok=True)
    orig_name = secure_filename(file_storage.filename or "upload.jpg")
    ext = orig_name.rsplit(".", 1)[-1].lower() if "." in orig_name else "jpg"
    unique_name = f"{uuid.uuid4().hex}_{orig_name}"
    save_path = os.path.join(target_folder, unique_name)
    file_storage.save(save_path)
    return save_path

def format_percentage(part: int, total: int) -> float:
    """Calculates safe percentage rounded to 1 decimal place."""
    if total <= 0:
        return 0.0
    return round((part / total) * 100.0, 1)
