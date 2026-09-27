from config import Config
from utils.helpers import format_percentage

class GradingService:
    @staticmethod
    def calculate_assessment(counts: dict) -> dict:
        """
        Calculates percentages, weighted preliminary quality score, and grade.
        
        Args:
            counts: dict with keys: good, damaged, rotten, sprouted
            
        Returns:
            dict with total, percentages, quality_score, preliminary_grade,
            grade_description, defect_rate, and scoring breakdown.
        """
        good = int(counts.get("good", 0))
        damaged = int(counts.get("damaged", 0))
        rotten = int(counts.get("rotten", 0))
        sprouted = int(counts.get("sprouted", 0))
        
        total = good + damaged + rotten + sprouted
        
        if total == 0:
            return {
                "total": 0,
                "counts": {"good": 0, "damaged": 0, "rotten": 0, "sprouted": 0},
                "percentages": {"good": 0.0, "damaged": 0.0, "rotten": 0.0, "sprouted": 0.0},
                "quality_score": 0.0,
                "preliminary_grade": "URS",
                "grade_description": "No onions detected for evaluation",
                "defect_count": 0,
                "defect_percentage": 0.0
            }
            
        percentages = {
            "good": format_percentage(good, total),
            "damaged": format_percentage(damaged, total),
            "rotten": format_percentage(rotten, total),
            "sprouted": format_percentage(sprouted, total)
        }
        
        # Weighted Quality Score formula:
        # score = (good * 100 + damaged * 50 + sprouted * 40 + rotten * 0) / total
        weights = Config.SCORE_WEIGHTS
        raw_score = (
            good * weights["good"] +
            damaged * weights["damaged"] +
            sprouted * weights["sprouted"] +
            rotten * weights["rotten"]
        ) / total
        
        quality_score = round(raw_score, 1)
        
        # Determine Preliminary Grade based on configurable thresholds
        preliminary_grade = "URS"
        grade_description = "Under Review / Substandard – High spoilage risk"
        for t in Config.GRADE_THRESHOLDS:
            if quality_score >= t["min_score"]:
                preliminary_grade = t["grade"]
                grade_description = t["description"]
                break
                
        defects = damaged + rotten + sprouted
        defect_percentage = format_percentage(defects, total)
        
        return {
            "total": total,
            "counts": {
                "good": good,
                "damaged": damaged,
                "rotten": rotten,
                "sprouted": sprouted
            },
            "percentages": percentages,
            "quality_score": quality_score,
            "preliminary_grade": preliminary_grade,
            "grade_description": grade_description,
            "defect_count": defects,
            "defect_percentage": defect_percentage,
            "score_weights": weights
        }
