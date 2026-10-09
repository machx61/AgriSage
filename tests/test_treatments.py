import json
import unittest

from agrisage.disease_map import CLASS_TO_KB, DISEASE_DISPLAY_MAP
from agrisage.treatments_db import (
    DATA_DIR,
    DEFAULT_TREATMENT,
    get_treatment_data,
    load_disease_data,
    load_formulations,
)
from agrisage.ui import CROP_EMOJI

SECTIONS = ["cultural", "biological", "botanical", "natural_farming", "local_practice", "iks"]


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
                self.assertTrue(any(treatment.get(s) for s in SECTIONS))

    def test_every_crop_has_a_healthy_class_and_an_emoji(self):
        for crop in {raw_class.split("_")[0] for raw_class in DISEASE_DISPLAY_MAP}:
            with self.subTest(crop=crop):
                self.assertIn(f"{crop}_healthy", DISEASE_DISPLAY_MAP)
                self.assertIn(crop, CROP_EMOJI)

    def test_healthy_classes_get_preventive_care(self):
        treatment = get_treatment_data("tomato_healthy")
        self.assertEqual(treatment["name"], "Healthy Plant")
        self.assertTrue(treatment["natural_farming"])

    def test_unknown_class_falls_back_to_default(self):
        self.assertIs(get_treatment_data("banana_sigatoka"), DEFAULT_TREATMENT)
        self.assertIs(get_treatment_data("unsupported"), DEFAULT_TREATMENT)

    def test_specific_routing(self):
        self.assertEqual(get_treatment_data("potato_late_blight")["name"], "Late Blight")
        self.assertIn("Turcicum", get_treatment_data("corn_turcicum_leaf_blight")["name"])
        self.assertIn("Yellow Rust", get_treatment_data("wheat_yellow_rust")["name"])


class FormulationTests(unittest.TestCase):
    def test_every_formulation_is_a_complete_recipe_card(self):
        for key, card in load_formulations().items():
            with self.subTest(formulation=key):
                for field in ("action", "summary", "how", "frequency", "evidence"):
                    self.assertTrue(card.get(field), field)
                for field in ("materials_needed", "preparation_steps", "application_steps", "safety_notes"):
                    self.assertTrue(card["details"].get(field), field)

    def test_every_formulation_reference_exists(self):
        library = load_formulations()
        for path in sorted(DATA_DIR.glob("*.json")):
            for kb_key, entry in json.loads(path.read_text(encoding="utf-8")).items():
                for ref in entry.get("natural_farming", []):
                    ref_id = ref if isinstance(ref, str) else ref.get("ref")
                    with self.subTest(crop=path.stem, entry=kb_key, ref=ref_id):
                        self.assertIn(ref_id, library)

    def test_references_become_cards_and_keep_overrides(self):
        treatment = get_treatment_data("okra_yellow_vein_mosaic_virus")
        cards = treatment["natural_farming"]
        self.assertTrue(cards)
        for card in cards:
            self.assertTrue(card["action"])
            self.assertTrue(card["details"]["materials_needed"])

        resolved = get_treatment_data("tomato_healthy")["natural_farming"]
        self.assertEqual(resolved[0]["action"], load_formulations()["jeevamrit"]["action"])


if __name__ == "__main__":
    unittest.main()
