import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agrisage import db

ASSESSMENT = {"health_score": 40, "status_label": "Moderate", "ai_notes": "Spots", "next_checkin_days": 5}
CHECKIN = {"health_score": 60, "status_label": "improving", "ai_notes": "Better",
           "treatment_adjustments": "Continue plan", "next_checkin_days": 7}


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        for patcher in (mock.patch.object(db, "DATABASE_PATH", Path(self.tmp.name) / "test.db"),
                        mock.patch.object(db, "_database_url", return_value=None)):  # never touch a real Postgres
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)
        db.init_db()
        self.alice = db.create_user("alice", "hash-a")
        self.bob = db.create_user("bob", "hash-b")

    def test_scan_history_round_trip(self):
        db.save_scan(self.alice, "potato_late_blight", "Potato - Late Blight", 87.5)
        db.save_scan(self.bob, "wheat_healthy", "Wheat - Healthy", 90.0)
        self.assertEqual(
            [row[1:] for row in db.get_past_scans(self.alice)],
            [("Potato - Late Blight", 87.5, "potato_late_blight")],
        )

    def test_plant_tracking_lifecycle(self):
        db.add_plant(self.alice, "Backyard Tomato", "tomato_early_blight", "Tomato - Early Blight", 80.0,
                     ASSESSMENT, b"jpeg-1")
        (plant,) = db.get_tracked_plants(self.alice)
        plant_id = plant[0]
        self.assertEqual(plant[1:4], ("Backyard Tomato", "tomato", "tomato_early_blight"))

        db.add_checkin(plant_id, self.alice, "Tomato - Early Blight", 100.0, CHECKIN, b"jpeg-2")

        entries = db.get_progress_entries(plant_id, self.alice)
        self.assertEqual([e["photo"] for e in entries], [b"jpeg-1", b"jpeg-2"])
        self.assertEqual(db.get_latest_entry(plant_id, self.alice)["adjusted_treatment"], "Continue plan")
        self.assertEqual(db.get_tracked_plants(self.alice)[0][5:7], ("improving", 60))

        db.delete_plant(plant_id, self.alice)
        self.assertEqual(db.get_tracked_plants(self.alice), [])
        self.assertEqual(db.get_progress_entries(plant_id, self.alice), [])

    def test_users_cannot_touch_each_others_plants(self):
        db.add_plant(self.alice, "Alice Rice", "rice_hispa", "Rice - Hispa", 70.0, ASSESSMENT, b"jpeg-1")
        plant_id = db.get_tracked_plants(self.alice)[0][0]

        self.assertEqual(db.get_tracked_plants(self.bob), [])
        self.assertEqual(db.get_progress_entries(plant_id, self.bob), [])
        with self.assertRaises(PermissionError):
            db.add_checkin(plant_id, self.bob, "Rice - Hispa", 100.0, CHECKIN, b"jpeg-2")
        db.delete_plant(plant_id, self.bob)

        self.assertEqual(len(db.get_progress_entries(plant_id, self.alice)), 1)
        self.assertEqual(len(db.get_tracked_plants(self.alice)), 1)

    def test_claim_device_data_moves_only_unowned_rows(self):
        with db.transaction() as conn:
            conn.execute("INSERT INTO scans (session_id, date, disease, confidence, raw_class) "
                         "VALUES ('dev1', '2025-01-01 10:00', 'Old Scan', 50.0, 'rice_hispa')")
            conn.execute("INSERT INTO tracked_plants (device_id, plant_name, crop_type) VALUES ('dev1', 'Old Plant', 'rice')")
            conn.execute("INSERT INTO scans (session_id, user_id, date, disease, confidence, raw_class) "
                         "VALUES ('dev1', ?, '2025-01-02 10:00', 'Bob Scan', 50.0, 'rice_hispa')", (self.bob,))

        db.claim_device_data(self.alice, "dev1")

        self.assertEqual([row[1] for row in db.get_past_scans(self.alice)], ["Old Scan"])
        self.assertEqual([row[1] for row in db.get_past_scans(self.bob)], ["Bob Scan"])
        self.assertEqual([p[1] for p in db.get_tracked_plants(self.alice)], ["Old Plant"])

    def test_duplicate_username_is_rejected(self):
        self.assertIsNone(db.create_user("alice", "other-hash"))

    def test_init_db_is_idempotent(self):
        db._initialized.clear()
        db.init_db()
        db.init_db()

    def test_migration_adds_columns_to_old_scans_table(self):
        path = Path(self.tmp.name) / "old.db"
        conn = sqlite3.connect(path)
        conn.execute("CREATE TABLE scans (id INTEGER PRIMARY KEY, date TEXT, disease TEXT, confidence REAL)")
        conn.close()
        with mock.patch.object(db, "DATABASE_PATH", path):
            db.init_db()
            user_id = db.create_user("carol", "hash-c")
            db.save_scan(user_id, "rice_hispa", "Rice - Hispa", 70.0)
            self.assertEqual(db.get_past_scans(user_id)[0][3], "rice_hispa")


if __name__ == "__main__":
    unittest.main()
