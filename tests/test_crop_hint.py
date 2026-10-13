import unittest
from unittest.mock import patch

from agrisage import gemini_tracker
from agrisage.disease_map import (
    CROP_MISMATCH, DISEASE_DISPLAY_MAP, NOT_A_LEAF, OTHER_DISEASE, SUPPORTED_CROPS, UNSUPPORTED, classes_for_crop,
)


class TestClassesForCrop(unittest.TestCase):
    def test_only_that_crop(self):
        classes = classes_for_crop("tomato")
        self.assertIn("tomato_healthy", classes)
        self.assertTrue(all(c.startswith("tomato_") for c in classes))

    def test_every_supported_crop_has_classes_and_they_partition_the_map(self):
        collected = [c for crop in SUPPORTED_CROPS for c in classes_for_crop(crop)]
        self.assertEqual(sorted(collected), sorted(DISEASE_DISPLAY_MAP))

    def test_unknown_crop(self):
        self.assertEqual(classes_for_crop("banana"), [])


class TestDiagnosisCropHint(unittest.TestCase):
    def run_diagnosis(self, crop_name, classes):
        with patch.object(gemini_tracker, "_generate",
                          return_value={"observations": "x", "crop_seen": "Tomato", "diagnosis": "", "class": classes[0], "confidence": 80}) as gen:
            result = gemini_tracker.get_initial_diagnosis("key", b"img", classes, crop_name)
        _, prompt, _, schema, _ = gen.call_args.args
        return result, prompt, schema

    def test_crop_given(self):
        classes = classes_for_crop("tomato")
        result, prompt, schema = self.run_diagnosis("Tomato", classes)
        self.assertEqual(result, {"class": classes[0], "confidence": 80, "name": ""})
        self.assertIn("The farmer says this plant is Tomato", prompt)
        self.assertEqual(set(schema.properties["class"].enum), set(classes) | {OTHER_DISEASE, UNSUPPORTED, NOT_A_LEAF, CROP_MISMATCH})

    def test_model_is_asked_to_diagnose_freely_before_choosing_a_class(self):
        classes = classes_for_crop("tomato")
        _, prompt, schema = self.run_diagnosis("Tomato", classes)
        self.assertEqual(schema.property_ordering, ["observations", "crop_seen", "diagnosis", "class", "confidence"])
        self.assertIn("Do NOT limit yourself to any list at this step", prompt)
        self.assertLess(prompt.index("Do NOT limit yourself"), prompt.index("tomato_healthy"))

    def test_no_crop(self):
        classes = list(DISEASE_DISPLAY_MAP)
        _, prompt, schema = self.run_diagnosis(None, classes)
        self.assertNotIn("farmer says", prompt)
        self.assertNotIn(CROP_MISMATCH, schema.properties["class"].enum)


def answer(cls, confidence, name=""):
    return {"observations": "x", "crop_seen": "Tomato", "diagnosis": name, "class": cls, "confidence": confidence}


class TestVoting(unittest.TestCase):
    CLASSES = classes_for_crop("tomato")

    def diagnose(self, *answers):
        """answers[i] is what the i-th model in the rotation says (or an exception)."""
        def fake(api_key, prompt, images, schema, models):
            reply = answers[gemini_tracker.MODELS.index(models[0])]
            if isinstance(reply, Exception):
                raise reply
            return reply

        with patch.object(gemini_tracker, "_generate", side_effect=fake) as gen:
            result = gemini_tracker.get_initial_diagnosis("key", b"img", self.CLASSES, "Tomato")
        return result, gen

    def test_unanimous_uses_the_models_stated_confidence(self):
        result, gen = self.diagnose(answer("tomato_early_blight", 40), answer("tomato_early_blight", 90))
        self.assertEqual(gen.call_count, 2)
        self.assertEqual(result["class"], "tomato_early_blight")
        self.assertEqual(result["confidence"], 65)  # mean of 40 and 90
        self.assertNotIn("disagreed", result)

    def test_tie_is_broken_by_a_third_model(self):
        result, gen = self.diagnose(
            answer("tomato_early_blight", 80), answer("tomato_powdery_mildew", 70), answer("tomato_early_blight", 60))
        self.assertEqual(gen.call_count, 3)
        self.assertEqual(result["class"], "tomato_early_blight")
        self.assertEqual(result["confidence"], 47)  # 2 of 3 votes, mean stated 70
        self.assertTrue(result["disagreed"])
        self.assertEqual(result["alternative"], "tomato_powdery_mildew")

    def test_three_way_split(self):
        result, _ = self.diagnose(
            answer("tomato_early_blight", 80), answer("tomato_powdery_mildew", 70), answer("tomato_healthy", 60))
        self.assertEqual(result["class"], "tomato_early_blight")  # best stated confidence breaks the tie
        self.assertEqual(result["confidence"], 27)

    def test_failed_vote_counts_against_confidence(self):
        result, gen = self.diagnose(answer("tomato_early_blight", 90), RuntimeError("down"), answer("tomato_early_blight", 90))
        self.assertEqual(gen.call_count, 3)
        self.assertEqual(result["class"], "tomato_early_blight")
        self.assertEqual(result["confidence"], 60)

    def test_all_votes_failing_is_an_error(self):
        result, _ = self.diagnose(RuntimeError("a"), RuntimeError("b"), RuntimeError("c"))
        self.assertIsNone(result["class"])
        self.assertIn("error", result)

    def test_other_disease_keeps_its_name(self):
        result, _ = self.diagnose(
            answer(OTHER_DISEASE, 30, "Tomato Septoria leaf spot"), answer(OTHER_DISEASE, 40, ""))
        self.assertEqual(result["class"], OTHER_DISEASE)
        self.assertEqual(result["name"], "Tomato Septoria leaf spot")


if __name__ == "__main__":
    unittest.main()
