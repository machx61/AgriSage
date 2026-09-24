import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agrisage import db


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        patcher = mock.patch.object(db, "DATABASE_PATH", Path(self.tmp.name) / "test.db")
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)
        db.init_db()

    def test_scan_history_round_trip(self):
        db.save_scan("dev1", "potato_late_blight", "Potato - Late Blight", 87.5)
        db.save_scan("dev2", "wheat_healthy", "Wheat - Healthy", 90.0)
        self.assertEqual(
            [row[1:] for row in db.get_past_scans("dev1")],
            [("Potato - Late Blight", 87.5, "potato_late_blight")],
        )

    def test_plant_tracking_lifecycle(self):
        assessment = {"health_score": 40, "status_label": "Moderate", "ai_notes": "Spots", "next_checkin_days": 5}
        db.add_plant("dev1", "Backyard Tomato", "tomato_early_blight", "Tomato - Early Blight", 80.0,
                     assessment, b"jpeg-1")
        (plant,) = db.get_tracked_plants("dev1")
        plant_id = plant[0]
        self.assertEqual(plant[1:4], ("Backyard Tomato", "tomato", "tomato_early_blight"))

        result = {"health_score": 60, "status_label": "improving", "ai_notes": "Better",
                  "treatment_adjustments": "Continue plan", "next_checkin_days": 7}
        db.add_checkin(plant_id, "Tomato - Early Blight", 100.0, result, b"jpeg-2")

        entries = db.get_progress_entries(plant_id)
        self.assertEqual([e["photo"] for e in entries], [b"jpeg-1", b"jpeg-2"])
        self.assertEqual(db.get_latest_entry(plant_id)["adjusted_treatment"], "Continue plan")
        self.assertEqual(db.get_tracked_plants("dev1")[0][5:7], ("improving", 60))

        db.delete_plant(plant_id)
        self.assertEqual(db.get_tracked_plants("dev1"), [])
        self.assertEqual(db.get_progress_entries(plant_id), [])

    def test_migration_adds_raw_class_to_old_scans_table(self):
        path = Path(self.tmp.name) / "old.db"
        conn = sqlite3.connect(path)
        conn.execute("CREATE TABLE scans (id INTEGER PRIMARY KEY, date TEXT, disease TEXT, confidence REAL)")
        conn.close()
        with mock.patch.object(db, "DATABASE_PATH", path):
            db.init_db()
            db.save_scan("dev1", "rice_hispa", "Rice - Hispa", 70.0)
            self.assertEqual(db.get_past_scans("dev1")[0][3], "rice_hispa")


if __name__ == "__main__":
    unittest.main()
