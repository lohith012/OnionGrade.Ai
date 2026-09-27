import os
from flask import Flask, send_from_directory, render_template, jsonify
from flask_cors import CORS
from config import Config
from database.db import init_db
from routes.api import api_bp
from routes.pages import pages_bp

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Ensure necessary folders exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(Config.STATIC_FOLDER, "demo"), exist_ok=True)
    os.makedirs(os.path.join(Config.STATIC_FOLDER, "images"), exist_ok=True)
    os.makedirs(os.path.dirname(Config.MODEL_PATH), exist_ok=True)
    
    # Initialize SQLite database
    init_db()
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(pages_bp)
    
    # Serve uploaded images securely
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)
        
    # Serve generated PDF reports
    @app.route("/reports/<path:filename>")
    def serve_report(filename):
        return send_from_directory(Config.REPORTS_FOLDER, filename)
        
    # Context processor for global template variables
    @app.context_processor
    def inject_globals():
        return {
            "app_title": "OnionVision AI",
            "app_tagline": "AI-Powered Onion Quality Assessment & Preliminary Grading",
            "ai_mode": Config.AI_MODE
        }
        
    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html", error=str(e)), 404
        
    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({
            "success": False,
            "error": "The uploaded image exceeds the 10MB size limit. Please upload a smaller image."
        }), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html", error=str(e)), 500
        
    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print(f"[*] OnionVision AI starting at http://127.0.0.1:{port} (Mode: {Config.AI_MODE.upper()})")
    app.run(host="0.0.0.0", port=port, debug=debug)
