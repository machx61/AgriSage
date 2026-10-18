import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from agrisage import auth, db


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        for patcher in (mock.patch.object(db, "DATABASE_PATH", Path(self.tmp.name) / "test.db"),
                        mock.patch.object(db, "_database_url", return_value=None)):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)
        db.init_db()

    def test_password_hash_is_salted_and_verifies(self):
        first, second = auth.hash_password("correct horse"), auth.hash_password("correct horse")
        self.assertNotEqual(first, second)
        self.assertTrue(auth.verify_password("correct horse", first))
        self.assertFalse(auth.verify_password("wrong horse", first))
        self.assertFalse(auth.verify_password("anything", "garbage"))

    def test_signup_validates_input(self):
        self.assertIn("Username", auth.signup("a!", "longenough")[1])
        self.assertIn("Password", auth.signup("farmer1", "short")[1])
        user, error = auth.signup("  Farmer1 ", "longenough")
        self.assertIsNone(error)
        self.assertEqual(user["username"], "farmer1")

    def test_signup_rejects_taken_username_case_insensitively(self):
        auth.signup("farmer1", "longenough")
        self.assertEqual(auth.signup("FARMER1", "different-pass")[1], "That username is taken.")

    def test_login_success_and_generic_failure(self):
        auth.signup("farmer1", "longenough")
        user, error = auth.login("Farmer1", "longenough")
        self.assertEqual((user["username"], error), ("farmer1", None))
        self.assertEqual(auth.login("farmer1", "wrong-pass")[1], "Wrong username or password.")
        self.assertEqual(auth.login("nobody", "longenough")[1], "Wrong username or password.")

    def test_account_locks_after_repeated_failures(self):
        auth.signup("farmer1", "longenough")
        for _ in range(auth.MAX_FAILED_ATTEMPTS):
            auth.login("farmer1", "wrong-pass")
        user, error = auth.login("farmer1", "longenough")  # even the right password is refused while locked
        self.assertIsNone(user)
        self.assertIn("Too many failed attempts", error)

        with mock.patch.object(time, "time", return_value=time.time() + auth.LOCK_SECONDS + 5):
            self.assertIsNotNone(auth.login("farmer1", "longenough")[0])

    def test_success_resets_failure_count(self):
        auth.signup("farmer1", "longenough")
        for _ in range(auth.MAX_FAILED_ATTEMPTS - 1):
            auth.login("farmer1", "wrong-pass")
        self.assertIsNotNone(auth.login("farmer1", "longenough")[0])
        for _ in range(auth.MAX_FAILED_ATTEMPTS - 1):
            auth.login("farmer1", "wrong-pass")
        self.assertIsNotNone(auth.login("farmer1", "longenough")[0])

    def test_session_token_round_trip_expiry_and_logout(self):
        user, _ = auth.signup("farmer1", "longenough")
        token = auth.new_session(user["id"])
        self.assertEqual(auth.user_from_token(token), user)
        self.assertIsNone(auth.user_from_token("not-a-token"))
        self.assertIsNone(auth.user_from_token(""))

        with mock.patch.object(time, "time", return_value=time.time() + (auth.SESSION_DAYS + 1) * 86400):
            self.assertIsNone(auth.user_from_token(token))

        auth.end_session(token)
        self.assertIsNone(auth.user_from_token(token))

    def test_raw_token_is_not_stored(self):
        user, _ = auth.signup("farmer1", "longenough")
        token = auth.new_session(user["id"])
        with db.transaction() as conn:
            stored = [row[0] for row in conn.execute("SELECT token_hash FROM auth_sessions")]
        self.assertNotIn(token, stored)


if __name__ == "__main__":
    unittest.main()
