import json
from database.db import get_db_connection

class InspectionRepository:
    @staticmethod
    def create(data: dict) -> int:
        """Inserts a new inspection record and returns its ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO inspections (
                report_id, original_image_path, annotated_image_path,
                total_onions, good_count, damaged_count, rotten_count,
                sprouted_count, undersized_count, good_percentage,
                damaged_percentage, rotten_percentage, sprouted_percentage,
                undersized_percentage, quality_score, preliminary_grade,
                average_confidence, ai_mode, pdf_path, detections_json
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            data["report_id"],
            data["original_image_path"],
            data["annotated_image_path"],
            data["total_onions"],
            data["good_count"],
            data["damaged_count"],
            data["rotten_count"],
            data["sprouted_count"],
            data["undersized_count"],
            data["good_percentage"],
            data["damaged_percentage"],
            data["rotten_percentage"],
            data["sprouted_percentage"],
            data["undersized_percentage"],
            data["quality_score"],
            data["preliminary_grade"],
            data["average_confidence"],
            data["ai_mode"],
            data.get("pdf_path"),
            json.dumps(data.get("detections", []))
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id

    @staticmethod
    def get_by_id(inspection_id: int):
        """Retrieves a single inspection record by primary key."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inspections WHERE id = ?", (inspection_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            d = dict(row)
            if d.get("detections_json"):
                try:
                    d["detections"] = json.loads(d["detections_json"])
                except Exception:
                    d["detections"] = []
            return d
        return None

    @staticmethod
    def get_by_report_id(report_id: str):
        """Retrieves a single inspection record by custom report ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inspections WHERE report_id = ?", (report_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            d = dict(row)
            if d.get("detections_json"):
                try:
                    d["detections"] = json.loads(d["detections_json"])
                except Exception:
                    d["detections"] = []
            return d
        return None

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0):
        """Returns all inspections ordered by creation time descending."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM inspections ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        rows = cursor.fetchall()
        conn.close()
        results = []
        for r in rows:
            d = dict(r)
            if d.get("detections_json"):
                try:
                    d["detections"] = json.loads(d["detections_json"])
                except Exception:
                    d["detections"] = []
            results.append(d)
        return results

    @staticmethod
    def update_pdf_path(inspection_id: int, pdf_path: str):
        """Updates the PDF path for a specific inspection."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE inspections SET pdf_path = ? WHERE id = ?", (pdf_path, inspection_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_dashboard_stats():
        """Calculates aggregate metrics for the dashboard."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_inspections,
                COALESCE(AVG(quality_score), 0) as avg_score,
                COALESCE(SUM(total_onions), 0) as total_onions,
                COALESCE(SUM(good_count), 0) as total_good,
                COALESCE(SUM(damaged_count), 0) as total_damaged,
                COALESCE(SUM(rotten_count), 0) as total_rotten,
                COALESCE(SUM(sprouted_count), 0) as total_sprouted,
                COALESCE(SUM(undersized_count), 0) as total_undersized
            FROM inspections
        """)
        stats_row = cursor.fetchone()
        
        # Grade breakdown
        cursor.execute("""
            SELECT preliminary_grade, COUNT(*) as count 
            FROM inspections 
            GROUP BY preliminary_grade
        """)
        grade_rows = cursor.fetchall()
        
        # Recent 5 inspections
        cursor.execute("SELECT * FROM inspections ORDER BY created_at DESC LIMIT 5")
        recent_rows = cursor.fetchall()
        
        conn.close()
        
        total_inspections = stats_row["total_inspections"] if stats_row else 0
        total_onions = stats_row["total_onions"] if stats_row else 0
        total_good = stats_row["total_good"] if stats_row else 0
        total_defects = total_onions - total_good
        avg_defect_rate = round((total_defects / total_onions * 100), 1) if total_onions > 0 else 0.0
        
        grades_dist = {"Grade A": 0, "Grade B": 0, "Grade C": 0, "URS": 0}
        for g in grade_rows:
            grades_dist[g["preliminary_grade"]] = g["count"]
            
        return {
            "total_inspections": total_inspections,
            "avg_quality_score": round(stats_row["avg_score"], 1) if stats_row else 0.0,
            "total_onions": total_onions,
            "total_good": total_good,
            "total_defects": total_defects,
            "avg_defect_rate": avg_defect_rate,
            "counts": {
                "good": total_good,
                "damaged": stats_row["total_damaged"] if stats_row else 0,
                "rotten": stats_row["total_rotten"] if stats_row else 0,
                "sprouted": stats_row["total_sprouted"] if stats_row else 0,
                "undersized": stats_row["total_undersized"] if stats_row else 0,
            },
            "grades_distribution": grades_dist,
            "recent_inspections": [dict(r) for r in recent_rows]
        }
