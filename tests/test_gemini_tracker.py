import json
import unittest
from unittest import mock

from agrisage import gemini_tracker


def fake_client(payload=None, error=None):
    client = mock.MagicMock()
    if error:
        client.models.generate_content.side_effect = error
    else:
        client.models.generate_content.return_value.text = json.dumps(payload)
    return client


class GeminiTrackerTests(unittest.TestCase):
    def setUp(self):
        gemini_tracker._client.cache_clear()

    def patch_client(self, client):
        patcher = mock.patch.object(gemini_tracker, "_client", return_value=client)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_diagnosis_uses_class_enum_and_clamps_confidence(self):
        client = fake_client({"class": "rice_hispa", "confidence": 140})
        self.patch_client(client)
        result = gemini_tracker.get_initial_diagnosis("key", b"img", ["rice_hispa", "rice_healthy"])
        self.assertEqual(result, {"class": "rice_hispa", "confidence": 100})

        schema = client.models.generate_content.call_args.kwargs["config"].response_schema
        self.assertEqual(schema.properties["class"].enum, ["rice_hispa", "rice_healthy", "unsupported", "not_a_leaf"])

    def test_diagnosis_error_returns_no_class(self):
        self.patch_client(fake_client(error=RuntimeError("quota exceeded")))
        result = gemini_tracker.get_initial_diagnosis("key", b"img", ["rice_hispa"])
        self.assertIsNone(result["class"])
        self.assertEqual(result["error"], "Something went wrong. Please try again.")

    def test_progress_without_previous_photo_sends_one_image(self):
        client = fake_client({"health_score": 70, "status_label": "improving", "ai_notes": "ok",
                              "treatment_adjustments": "Continue", "next_checkin_days": 30})
        self.patch_client(client)
        result = gemini_tracker.analyze_progress("key", None, b"curr", "Rice - Hispa", 50, "")
        self.assertEqual(result["next_checkin_days"], 14)
        self.assertEqual(result["treatment_adjustments"], "Continue")

        contents = client.models.generate_content.call_args.kwargs["contents"]
        self.assertEqual(len(contents), 2)  # prompt + current image
        self.assertIn("No earlier photo", contents[0])

    def test_overloaded_model_falls_back_to_next_model(self):
        client = fake_client({"class": "rice_hispa", "confidence": 80})
        ok = client.models.generate_content.return_value
        busy = gemini_tracker.errors.APIError(503, {"error": {"message": "high demand"}})
        client.models.generate_content.side_effect = [busy, ok]
        self.patch_client(client)

        result = gemini_tracker.get_initial_diagnosis("key", b"img", ["rice_hispa"])
        self.assertEqual(result["class"], "rice_hispa")
        models = [c.kwargs["model"] for c in client.models.generate_content.call_args_list]
        self.assertEqual(models, gemini_tracker.MODELS[:2])

    def test_all_models_timing_out_gives_friendly_error(self):
        client = fake_client(error=gemini_tracker.httpx.ReadTimeout("slow"))
        self.patch_client(client)
        with mock.patch.object(gemini_tracker.time, "sleep"):
            result = gemini_tracker.get_initial_diagnosis("key", b"img", ["rice_hispa"])
        self.assertIsNone(result["class"])
        self.assertIn("taking too long", result["error"])
        self.assertEqual(client.models.generate_content.call_count, 2 * len(gemini_tracker.MODELS))

    def test_assessment_without_photo_returns_fallback(self):
        client = fake_client({})
        self.patch_client(client)
        result = gemini_tracker.get_initial_assessment("key", b"", "Rice - Hispa", 80)
        self.assertEqual(result["status_label"], "Unknown")
        client.models.generate_content.assert_not_called()


if __name__ == "__main__":
    unittest.main()
