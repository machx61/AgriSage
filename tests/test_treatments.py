import unittest

from agrisage.disease_map import CLASS_TO_KB, DISEASE_DISPLAY_MAP
from agrisage.treatments_db import DEFAULT_TREATMENT, get_treatment_data, load_disease_data


class TreatmentCoverageTests(unittest.TestCase):
    def test_every_kb_reference_exists(self):
        for raw_class, kb in CLASS_TO_KB.items():
            if kb is None:
                continue
            crop_file, kb_key = kb
            with self.subTest(raw_class=raw_class):
                self.assertIn(kb_key, load_disease_data(crop_file))

    def test_every_supported_class_has_real_treatments(self):
        for raw_class in DISEASE_DISPLAY_MAP:
            with self.subTest(raw_class=raw_class):
                treatment = get_treatment_data(raw_class)
                self.assertIsNot(treatment, DEFAULT_TREATMENT)
                sections = ["cultural", "biological", "botanical", "local_practice", "iks"]
                self.assertTrue(any(treatment.get(s) for s in sections))

    def test_healthy_classes_get_preventive_care(self):
        treatment = get_treatment_data("tomato_healthy")
        self.assertEqual(treatment["name"], "Healthy Plant")
        self.assertTrue(treatment["iks"])

    def test_unknown_class_falls_back_to_default(self):
        self.assertIs(get_treatment_data("apple_scab"), DEFAULT_TREATMENT)
        self.assertIs(get_treatment_data("unsupported"), DEFAULT_TREATMENT)

    def test_specific_routing(self):
        self.assertEqual(get_treatment_data("potato_late_blight")["name"], "Late Blight")
        self.assertIn("Turcicum", get_treatment_data("corn_turcicum_leaf_blight")["name"])
        self.assertIn("Yellow Rust", get_treatment_data("wheat_yellow_rust")["name"])


if __name__ == "__main__":
    unittest.main()
