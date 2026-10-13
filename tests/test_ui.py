import unittest
from agrisage import ui


class TestSupportedCrops(unittest.TestCase):
    def test_supported_crops_with_dict(self):
        crops_dict = {"tomato": "Tomato", "potato": "Potato"}
        html = ui.supported_crops(crops_dict)
        self.assertIn("Tomato", html)
        self.assertIn("Potato", html)
        self.assertIn("Works with 2 crops", html)

    def test_supported_crops_with_list(self):
        crops_list = ["Apple", "Brinjal", "Tomato"]
        html = ui.supported_crops(crops_list)
        self.assertIn("Apple", html)
        self.assertIn("Tomato", html)
        self.assertIn("Works with 3 crops", html)

    def test_supported_crops_with_tuples(self):
        crops_tuples = [("tomato", "Tomato"), ("rice", "Rice")]
        html = ui.supported_crops(crops_tuples)
        self.assertIn("Tomato", html)
        self.assertIn("Rice", html)
        self.assertIn("Works with 2 crops", html)

    def test_supported_crops_with_empty(self):
        html = ui.supported_crops([])
        self.assertIn("Works with 0 crops", html)


if __name__ == "__main__":
    unittest.main()
