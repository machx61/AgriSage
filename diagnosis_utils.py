"""Pure helpers for presenting model predictions and treatment reminders."""

from collections import defaultdict
import re
from typing import Sequence


def select_consensus_prediction(
    predictions: Sequence[str], confidences: Sequence[float]
) -> tuple[str, float]:
    """Return the most supported class and its mean confidence.

    A deterministic alphabetical tie-break keeps the same upload batch from
    producing different diagnoses between application runs.
    """
    if not predictions or len(predictions) != len(confidences):
        raise ValueError("Predictions and confidences must be non-empty and aligned.")

    scores: dict[str, list[float]] = defaultdict(list)
    for prediction, confidence in zip(predictions, confidences):
        scores[prediction].append(float(confidence))

    selected_class = sorted(
        scores,
        key=lambda label: (-len(scores[label]), -(sum(scores[label]) / len(scores[label])), label),
    )[0]
    selected_confidences = scores[selected_class]
    return selected_class, sum(selected_confidences) / len(selected_confidences)


def reminder_days_from_frequency(frequency: str) -> int | None:
    """Extract a repeat interval from a human-readable treatment frequency."""
    text = frequency.lower()
    match = re.search(
        r"(?:every|replace every|refresh every|test every)\s+(\d+)(?:\s*-\s*\d+)?\s*(day|week|month)",
        text,
    )
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        return value * {"day": 1, "week": 7, "month": 30}[unit]

    if "weekly" in text:
        return 7
    return None
