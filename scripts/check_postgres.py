"""Smoke-test the Postgres backend against the database in DATABASE_URL.

Run from the repo root:  python scripts/check_postgres.py

DATABASE_URL comes from the environment or .streamlit/secrets.toml. The check
creates one throwaway account, exercises accounts / scans / plants /
ownership, then deletes everything it created.
"""

import os
import secrets
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agrisage import auth, db

ASSESSMENT = {"health_score": 40, "status_label": "Moderate", "ai_notes": "Spots", "next_checkin_days": 5}
CHECKIN = {"health_score": 60, "status_label": "improving", "ai_notes": "Better",
           "treatment_adjustments": "Continue plan", "next_checkin_days": 7}


def check(label: str, condition: bool):
    print(f"{'PASS' if condition else 'FAIL'}  {label}")
    if not condition:
        raise SystemExit(1)


def main():
    if not db._database_url():
        raise SystemExit("DATABASE_URL is not set (environment or .streamlit/secrets.toml).")

    db.init_db()
    db._initialized.clear()
    db.init_db()
    check("init_db runs twice without error", True)

    suffix = secrets.token_hex(4)
    alice, error = auth.signup(f"pgcheck_a_{suffix}", "longenough1")
    bob, _ = auth.signup(f"pgcheck_b_{suffix}", "longenough1")
    user_ids = [alice["id"], bob["id"]]
    try:
        check("signup", error is None and alice["id"] != bob["id"])
        check("duplicate username rejected", auth.signup(alice["username"].upper(), "longenough1")[0] is None)
        check("login works", auth.login(alice["username"], "longenough1")[0] == alice)
        check("wrong password rejected", auth.login(alice["username"], "nope-nope")[0] is None)

        token = auth.new_session(alice["id"])
        check("session token resolves to user", auth.user_from_token(token) == alice)
        auth.end_session(token)
        check("session token revoked on logout", auth.user_from_token(token) is None)

        db.save_scan(alice["id"], "potato_late_blight", "Potato - Late Blight", 87.5)
        check("scan history saved and scoped",
              len(db.get_past_scans(alice["id"])) == 1 and db.get_past_scans(bob["id"]) == [])

        db.add_plant(alice["id"], "Check Plant", "tomato_early_blight", "Tomato - Early Blight", 80.0,
                     ASSESSMENT, b"jpeg-1")
        (plant,) = db.get_tracked_plants(alice["id"])
        plant_id = plant[0]
        db.add_checkin(plant_id, alice["id"], "Tomato - Early Blight", 100.0, CHECKIN, b"jpeg-2")
        entries = db.get_progress_entries(plant_id, alice["id"])
        check("plant + check-in + photos round trip", [e["photo"] for e in entries] == [b"jpeg-1", b"jpeg-2"])

        check("other user sees nothing", db.get_progress_entries(plant_id, bob["id"]) == [])
        try:
            db.add_checkin(plant_id, bob["id"], "x", 1.0, CHECKIN, None)
            check("other user cannot check in", False)
        except PermissionError:
            check("other user cannot check in", True)
        db.delete_plant(plant_id, bob["id"])
        check("other user cannot delete", len(db.get_tracked_plants(alice["id"])) == 1)

        db.delete_plant(plant_id, alice["id"])
        check("owner can delete", db.get_tracked_plants(alice["id"]) == [])
    finally:
        with db.transaction() as conn:
            for user_id in user_ids:
                conn.execute("DELETE FROM auth_sessions WHERE user_id = ?", (user_id,))
                conn.execute("DELETE FROM scans WHERE user_id = ?", (user_id,))
                conn.execute("DELETE FROM progress_entries WHERE plant_id IN "
                             "(SELECT id FROM tracked_plants WHERE user_id = ?)", (user_id,))
                conn.execute("DELETE FROM tracked_plants WHERE user_id = ?", (user_id,))
                conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    print("\nAll Postgres checks passed; test data cleaned up.")


if __name__ == "__main__":
    main()
