"""
Agrisage Knowledge Base
Regional Context: Himachal Pradesh (Hills Zone)
Focus: Indigenous Knowledge Systems (IKS) & Vrikshayurveda Practices
"""
import json
from pathlib import Path
import streamlit as st

from agrisage.disease_map import CLASS_TO_KB

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "diseases"

THEME_COLORS = {
    "mint_green": {"bg": "#E8F8F5", "border": "#2ECC71", "text": "#117A65"},
    "soft_blue": {"bg": "#EBF5FB", "border": "#3498DB", "text": "#1B4F72"},
    "pastel_green": {"bg": "#EAFAF1", "border": "#27AE60", "text": "#196F3D"},
    "soft_yellow": {"bg": "#FEFDE8", "border": "#F1C40F", "text": "#7D6608"},
    "butter_yellow": {"bg": "#FEF9E7", "border": "#F39C12", "text": "#7E5109"},
    "lavender": {"bg": "#F4ECF7", "border": "#8E44AD", "text": "#512E5F"},
    "peach": {"bg": "#FBEEE6", "border": "#E67E22", "text": "#784212"},
    "soft_pink": {"bg": "#FDEDEC", "border": "#E74C3C", "text": "#78281F"},
    "sky_blue": {"bg": "#EAF2F8", "border": "#2980B9", "text": "#1A5276"},
}

DEFAULT_TREATMENT = {
    "name": "General Foliar Condition",
    "cultural": [
        {
            "action": "Five-Gift Cow Tonic (Panchagavya)",
            "emoji": "🐄",
            "theme": "soft_pink",
            "summary": "A gentle, nourishing tonic passed down through generations—no animal harmed!",
            "how": "Ferment cow milk, curd, ghee, cow urine, and cow dung. Dilute and use as a soil drench.",
            "frequency": "Every 10-14 days"
        }
    ],
    "biological": []
}

HEALTHY_TREATMENT = {
    "name": "Healthy Plant",
    "cultural": [
        {
            "action": "Weekly Leaf Check",
            "emoji": "🔍",
            "theme": "butter_yellow",
            "summary": "Your plant looks healthy! Catching problems early is the best protection.",
            "how": "Look at both sides of a few leaves every week for spots, curling, yellowing or insects, and scan again if anything changes.",
            "frequency": "Weekly"
        },
        {
            "action": "Water at the Roots",
            "emoji": "💧",
            "theme": "sky_blue",
            "summary": "Wet leaves invite fungal diseases, especially in humid hill weather.",
            "how": "Water the soil around the base in the morning instead of sprinkling over the leaves, and keep drainage channels clear.",
            "frequency": "Whenever watering"
        }
    ],
    "biological": []
}

# Preventive tonics from the okra knowledge base that suit any healthy crop.
_PREVENTIVE_KB = ("okra", "general_preventive_formulations")
_PREVENTIVE_ACTIONS = {"Jiwamrita Soil Tonic", "Five-Gift Panchagavya Tonic"}


@st.cache_data
def load_disease_data(crop_name: str) -> dict:
    """Load the disease JSON for a specific crop."""
    file_path = DATA_DIR / f"{crop_name}.json"
    if not file_path.exists():
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_healthy_treatment() -> dict:
    crop_file, kb_key = _PREVENTIVE_KB
    preventive = load_disease_data(crop_file).get(kb_key, {}).get("iks", [])
    return {**HEALTHY_TREATMENT, "iks": [i for i in preventive if i.get("action") in _PREVENTIVE_ACTIONS]}


def get_treatment_data(predicted_class: str) -> dict:
    """Return the treatment profile for a supported diagnosis class."""
    key = predicted_class.lower().strip()
    if key not in CLASS_TO_KB:
        return DEFAULT_TREATMENT

    kb = CLASS_TO_KB[key]
    if kb is None:
        return get_healthy_treatment()

    crop_file, kb_key = kb
    return load_disease_data(crop_file).get(kb_key, DEFAULT_TREATMENT)
