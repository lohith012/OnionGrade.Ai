import os
import shutil
from flask import Blueprint, request, jsonify, send_file, current_app
from config import Config
from utils.helpers import allowed_file, save_uploaded_file, generate_report_id
from utils.image_processing import validate_image, preprocess_image
from services.detection_service import DetectionService
from services.grading_service import GradingService
from services.report_service import ReportService
from database.models import InspectionRepository

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Lazy-loaded detection service singleton
_detector = None

def get_detector():
    global _detector
    if _detector is None:
        _detector = DetectionService()
    return _detector

@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "OnionVision AI",
        "ai_mode": Config.AI_MODE,
        "database": "connected"
    })

@api_bp.route("/analyze", methods=["POST"])
def analyze_onion():
    """
    Main image analysis endpoint.
    Accepts:
        - Multipart 'image' file OR
        - JSON payload with 'demo_image' path (e.g. 'demo1.jpg')
    """
    try:
        report_id = generate_report_id()
        upload_dir = os.path.join(Config.UPLOAD_FOLDER, report_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        saved_image_path = None
        
        # Check if file uploaded via multipart form
        if "image" in request.files:
            file = request.files["image"]
            if file.filename == "":
                return jsonify({"success": False, "error": "No file selected. Please choose an onion image."}), 400
                
            if not allowed_file(file.filename):
                return jsonify({
                    "success": False,
                    "error": f"Invalid file format. Allowed formats: {', '.join(Config.ALLOWED_EXTENSIONS).upper()}"
                }), 400
                
            saved_image_path = save_uploaded_file(file, upload_dir)
            
        # Check if demo sample image requested
        elif request.is_json and request.json.get("demo_image"):
            demo_filename = os.path.basename(request.json["demo_image"])
            src_demo = os.path.join(Config.STATIC_FOLDER, "demo", demo_filename)
            if not os.path.exists(src_demo):
                return jsonify({"success": False, "error": f"Sample demo image '{demo_filename}' not found."}), 404
                
            saved_image_path = os.path.join(upload_dir, f"sample_{demo_filename}")
            shutil.copyfile(src_demo, saved_image_path)
            
        elif request.form.get("demo_image"):
            demo_filename = os.path.basename(request.form.get("demo_image"))
            src_demo = os.path.join(Config.STATIC_FOLDER, "demo", demo_filename)
            if not os.path.exists(src_demo):
                return jsonify({"success": False, "error": f"Sample demo image '{demo_filename}' not found."}), 404
                
            saved_image_path = os.path.join(upload_dir, f"sample_{demo_filename}")
            shutil.copyfile(src_demo, saved_image_path)
            
        else:
            return jsonify({
                "success": False,
                "error": "No image uploaded. Please upload a photo or select a demo sample."
            }), 400

        # Validate image file integrity
        if not validate_image(saved_image_path):
            if os.path.exists(saved_image_path):
                os.remove(saved_image_path)
            return jsonify({
                "success": False,
                "error": "The uploaded image file is corrupted or unreadable. Please upload a valid JPG, PNG, or WEBP photo."
            }), 400

        # Preprocess image
        try:
            _, _, meta = preprocess_image(saved_image_path)
        except Exception as e:
            return jsonify({"success": False, "error": f"Image preprocessing failed: {str(e)}"}), 500

        # Run Detection
        annotated_filename = f"annotated_{os.path.basename(saved_image_path)}"
        annotated_path = os.path.join(upload_dir, annotated_filename)
        
        detector = get_detector()
        detection_result = detector.detect(saved_image_path, annotated_path)
        
        total_onions = detection_result["total_onions"]
        if total_onions == 0:
            return jsonify({
                "success": False,
                "error": "Unable to detect onions clearly. Please upload a clearer image with good lighting and contrasting background."
            }), 422

        # Calculate Grading & Quality Score
        assessment = GradingService.calculate_assessment(detection_result["counts"])
        
        # Prepare relative image URLs for frontend display
        rel_orig_url = f"/uploads/{report_id}/{os.path.basename(saved_image_path)}"
        rel_annot_url = f"/uploads/{report_id}/{annotated_filename}"
        
        # Generate PDF Report
        pdf_filename = f"Report_{report_id}.pdf"
        pdf_path = os.path.join(Config.REPORTS_FOLDER, pdf_filename)
        
        record_payload = {
            "report_id": report_id,
            "created_at": None,  # SQLite auto timestamp
            "original_image_path": saved_image_path,
            "annotated_image_path": annotated_path,
            "total_onions": total_onions,
            "good_count": assessment["counts"]["good"],
            "damaged_count": assessment["counts"]["damaged"],
            "rotten_count": assessment["counts"]["rotten"],
            "sprouted_count": assessment["counts"].get("sprouted", 0),
            "undersized_count": assessment["counts"].get("undersized", 0),
            "good_percentage": assessment["percentages"].get("good", 0.0),
            "damaged_percentage": assessment["percentages"].get("damaged", 0.0),
            "rotten_percentage": assessment["percentages"].get("rotten", 0.0),
            "sprouted_percentage": assessment["percentages"].get("sprouted", 0.0),
            "undersized_percentage": assessment["percentages"].get("undersized", 0.0),
            "quality_score": assessment["quality_score"],
            "preliminary_grade": assessment["preliminary_grade"],
            "average_confidence": detection_result["average_confidence"],
            "ai_mode": detection_result["ai_mode"],
            "pdf_path": pdf_path,
            "detections": detection_result.get("detections", [])
        }
        
        try:
            ReportService.generate_pdf(record_payload, pdf_path)
        except Exception as pdf_err:
            current_app.logger.warning(f"PDF generation error: {pdf_err}")
            record_payload["pdf_path"] = None

        # Save to SQLite Database
        db_id = InspectionRepository.create(record_payload)
        
        return jsonify({
            "success": True,
            "id": db_id,
            "report_id": report_id,
            "total": total_onions,
            "counts": assessment["counts"],
            "percentages": assessment["percentages"],
            "quality_score": assessment["quality_score"],
            "grade": assessment["preliminary_grade"],
            "grade_description": assessment["grade_description"],
            "confidence": detection_result["average_confidence"],
            "ai_mode": detection_result["ai_mode"],
            "original_image_url": rel_orig_url,
            "annotated_image_url": rel_annot_url,
            "redirect_url": f"/results/{db_id}",
            "pdf_download_url": f"/api/report/{db_id}",
            "defect_percentage": assessment["defect_percentage"],
            "detections": detection_result.get("detections", [])
        })

    except Exception as e:
        current_app.logger.error(f"Error in /api/analyze: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"An unexpected error occurred during analysis: {str(e)}"
        }), 500

@api_bp.route("/inspections", methods=["GET"])
def get_inspections():
    """Returns inspection history list."""
    try:
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        inspections = InspectionRepository.get_all(limit=limit, offset=offset)
        return jsonify({
            "success": True,
            "count": len(inspections),
            "inspections": inspections
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route("/inspections/<int:inspection_id>", methods=["GET"])
def get_inspection_detail(inspection_id: int):
    """Returns details for a single inspection."""
    inspection = InspectionRepository.get_by_id(inspection_id)
    if not inspection:
        return jsonify({"success": False, "error": "Inspection record not found"}), 404
        
    return jsonify({
        "success": True,
        "inspection": inspection
    })

@api_bp.route("/report/<int:inspection_id>", methods=["GET"])
def download_report(inspection_id: int):
    """Downloads or streams the PDF report for a given inspection ID."""
    inspection = InspectionRepository.get_by_id(inspection_id)
    if not inspection:
        return jsonify({"success": False, "error": "Inspection not found"}), 404
        
    pdf_path = inspection.get("pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        # Regenerate on the fly if missing
        pdf_path = os.path.join(Config.REPORTS_FOLDER, f"Report_{inspection['report_id']}.pdf")
        try:
            ReportService.generate_pdf(inspection, pdf_path)
            InspectionRepository.update_pdf_path(inspection_id, pdf_path)
        except Exception as e:
            return jsonify({"success": False, "error": f"Could not generate PDF: {str(e)}"}), 500
            
    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"OnionVision_Report_{inspection['report_id']}.pdf"
    )

@api_bp.route("/stats", methods=["GET"])
def get_stats():
    """Returns dashboard statistics."""
    try:
        stats = InspectionRepository.get_dashboard_stats()
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
