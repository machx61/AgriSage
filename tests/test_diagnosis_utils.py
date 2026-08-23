import unittest

from diagnosis_utils import reminder_days_from_frequency, select_consensus_prediction


class ConsensusPredictionTests(unittest.TestCase):
    def test_confidence_only_includes_the_selected_class(self):
        label, confidence = select_consensus_prediction(
            ["apple_scab", "apple_scab", "tomato_mold"], [60.0, 80.0, 99.0]
        )
        self.assertEqual(label, "apple_scab")
        self.assertEqual(confidence, 70.0)

    def test_tie_breaks_on_confidence_then_label(self):
        label, confidence = select_consensus_prediction(
            ["tomato_mold", "apple_scab"], [80.0, 80.0]
        )
        self.assertEqual(label, "apple_scab")
        self.assertEqual(confidence, 80.0)

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(ValueError):
            select_consensus_prediction(["apple_scab"], [])


class ReminderFrequencyTests(unittest.TestCase):
    def test_extracts_day_week_and_month_intervals(self):
        self.assertEqual(reminder_days_from_frequency("Every 10-14 days"), 10)
        self.assertEqual(reminder_days_from_frequency("Refresh every 2-3 weeks"), 14)
        self.assertEqual(reminder_days_from_frequency("Once at planting, refresh every 2-3 months"), 60)
        self.assertEqual(reminder_days_from_frequency("Weekly"), 7)

    def test_does_not_schedule_non_recurring_actions(self):
        self.assertIsNone(reminder_days_from_frequency("Once, before sowing"))
        self.assertIsNone(reminder_days_from_frequency("As needed"))


if __name__ == "__main__":
    unittest.main()
