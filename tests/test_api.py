import os
import io
import pytest
from app import create_app
from services.grading_service import GradingService
from database.db import init_db
from database.models import InspectionRepository

@pytest.fixture
def client():
    os.environ["AI_MODE"] = "demo"
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_api_health(client):
    """Test health endpoint."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "OnionVision AI"

def test_grade_calculation():
    """Test standard quality score and grade logic."""
    counts = {
        "good": 14,
        "damaged": 2,
        "rotten": 2,
        "sprouted": 2
    }
    assessment = GradingService.calculate_assessment(counts)
    
    assert assessment["total"] == 20
    assert assessment["percentages"]["good"] == 70.0
    # Expected weighted score: (14*100 + 2*50 + 2*0 + 2*40) / 20 = 1580 / 20 = 79.0
    assert assessment["quality_score"] == 79.0
    assert assessment["preliminary_grade"] == "Grade B"

def test_grade_calculation_grade_a():
    """Test Grade A threshold calculation (>= 90)."""
    counts = {"good": 20, "damaged": 0, "rotten": 0, "sprouted": 0}
    assessment = GradingService.calculate_assessment(counts)
    assert assessment["quality_score"] == 100.0
    assert assessment["preliminary_grade"] == "Grade A"

def test_grade_calculation_empty():
    """Test zero onion edge case."""
    counts = {"good": 0, "damaged": 0, "rotten": 0, "sprouted": 0}
    assessment = GradingService.calculate_assessment(counts)
    assert assessment["total"] == 0
    assert assessment["quality_score"] == 0.0
    assert assessment["preliminary_grade"] == "URS"

def test_analyze_demo_image(client):
    """Test analyzing a demo sample image."""
    res = client.post("/api/analyze", json={"demo_image": "sample_onions_batch.jpg"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "report_id" in data
    assert data["total"] > 0
    assert "quality_score" in data
    assert "grade" in data

def test_analyze_invalid_file(client):
    """Test rejection of non-image file uploads."""
    data = {
        "image": (io.BytesIO(b"fake text data"), "test.txt")
    }
    res = client.post("/api/analyze", data=data, content_type="multipart/form-data")
    assert res.status_code == 400
    json_data = res.get_json()
    assert json_data["success"] is False
    assert "Invalid file format" in json_data["error"]

def test_inspection_history_and_stats(client):
    """Test history API and dashboard statistics."""
    # Fetch history
    res = client.get("/api/inspections")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert isinstance(data["inspections"], list)

    # Fetch stats
    stats_res = client.get("/api/stats")
    assert stats_res.status_code == 200
    stats_data = stats_res.get_json()
    assert stats_data["success"] is True
    assert "total_inspections" in stats_data["stats"]
