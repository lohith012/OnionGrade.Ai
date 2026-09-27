import os
from flask import Blueprint, render_template, abort
from config import Config
from database.models import InspectionRepository

pages_bp = Blueprint("pages", __name__)

def to_web_url(path_str: str) -> str:
    """Converts a local filesystem path to a web accessible URL."""
    if not path_str:
        return ""
    norm = path_str.replace("\\", "/")
    if "/uploads/" in norm:
        return "/uploads/" + norm.split("/uploads/", 1)[1]
    if "/static/" in norm:
        return "/static/" + norm.split("/static/", 1)[1]
    return norm

@pages_bp.route("/")
def index():
    """Renders the landing page."""
    return render_template("index.html", ai_mode=Config.AI_MODE)

@pages_bp.route("/inspect")
def inspect():
    """Renders the interactive quality inspection page."""
    return render_template(
        "inspect.html",
        ai_mode=Config.AI_MODE,
        class_meta=Config.CLASS_METADATA,
        allowed_extensions=list(Config.ALLOWED_EXTENSIONS)
    )

@pages_bp.route("/results/<int:inspection_id>")
def results(inspection_id: int):
    """Renders the detailed result page for an inspection."""
    inspection = InspectionRepository.get_by_id(inspection_id)
    if not inspection:
        abort(404, description="Inspection record not found")
        
    inspection["original_image_url"] = to_web_url(inspection.get("original_image_path"))
    inspection["annotated_image_url"] = to_web_url(inspection.get("annotated_image_path"))
        
    return render_template(
        "results.html",
        inspection=inspection,
        class_meta=Config.CLASS_METADATA,
        ai_mode=Config.AI_MODE
    )

@pages_bp.route("/dashboard")
def dashboard():
    """Renders the metrics and analytics dashboard."""
    stats = InspectionRepository.get_dashboard_stats()
    return render_template(
        "dashboard.html",
        stats=stats,
        ai_mode=Config.AI_MODE,
        class_meta=Config.CLASS_METADATA
    )

@pages_bp.route("/history")
def history():
    """Renders the historical inspection log."""
    inspections = InspectionRepository.get_all(limit=200)
    return render_template(
        "history.html",
        inspections=inspections,
        ai_mode=Config.AI_MODE
    )

@pages_bp.route("/about")
def about():
    """Renders the about and methodology page."""
    return render_template(
        "about.html",
        score_weights=Config.SCORE_WEIGHTS,
        grade_thresholds=Config.GRADE_THRESHOLDS,
        class_meta=Config.CLASS_METADATA,
        ai_mode=Config.AI_MODE
    )
