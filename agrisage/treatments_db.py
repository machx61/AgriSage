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
FORMULATIONS_FILE = DATA_DIR.parent / "formulations.json"

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
    "biological": [],
    # Soil-building natural-farming inputs that suit any healthy crop
    "natural_farming": ["jeevamrit", "beejamrit"]
}


@st.cache_data
def load_disease_data(crop_name: str) -> dict:
    """Load the disease JSON for a specific crop."""
    file_path = DATA_DIR / f"{crop_name}.json"
    if not file_path.exists():
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_formulations() -> dict:
    """Shared natural-farming recipes (Jeevamrit, Agniastra, ...) keyed by id."""
    with open(FORMULATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_formulations(treatment: dict) -> dict:
    """Swap the formulation ids under "natural_farming" for their recipe cards.

    An entry is an id from formulations.json, or {"ref": id, ...} whose other
    keys override the shared card (e.g. a crop-specific "how" or "frequency").
    """
    refs = treatment.get("natural_farming")
    if not refs:
        return treatment

    library = load_formulations()
    cards = []
    for ref in refs:
        overrides = {} if isinstance(ref, str) else {k: v for k, v in ref.items() if k != "ref"}
        card = library.get(ref if isinstance(ref, str) else ref.get("ref"))
        if card:
            cards.append({**card, **overrides})
    return {**treatment, "natural_farming": cards}


# Cards that only say "nothing is documented"; never shown to farmers
PLACEHOLDER_ACTIONS = {"IKS Research Gap Identified", "Ask a Local Elder"}

# Natural-farming recipes that are biological inputs rather than botanical sprays
_BIOLOGICAL_KEYWORDS = ("jeevamrit", "beejamrit", "tonic", "coat", "microbe", "dung")


def group_treatments(treatment: dict) -> dict[str, list[dict]]:
    """Sort a treatment profile into botanical / biological / cultural cards,
    dropping empty entries and placeholders."""
    natural = treatment.get("natural_farming", [])
    biological_natural = [c for c in natural
                          if any(k in c.get("action", "").lower() for k in _BIOLOGICAL_KEYWORDS)]
    botanical_natural = [c for c in natural if c not in biological_natural]
    grouped = {
        "botanical": treatment.get("botanical", []) + botanical_natural,
        "biological": treatment.get("biological", []) + biological_natural,
        "cultural": (treatment.get("cultural", []) + treatment.get("local_practice", [])
                     + treatment.get("iks", [])),
    }
    return {
        category: [c for c in cards
                   if c.get("action") and c["action"] not in PLACEHOLDER_ACTIONS
                   and (c.get("how") or c.get("summary"))]
        for category, cards in grouped.items()
    }


def get_healthy_treatment() -> dict:
    return resolve_formulations(HEALTHY_TREATMENT)


def get_treatment_data(predicted_class: str) -> dict:
    """Return the treatment profile for a supported diagnosis class."""
    key = predicted_class.lower().strip()
    if key not in CLASS_TO_KB:
        return DEFAULT_TREATMENT

    kb = CLASS_TO_KB[key]
    if kb is None:
        return get_healthy_treatment()

    crop_file, kb_key = kb
    treatment = load_disease_data(crop_file).get(kb_key)
    return resolve_formulations(treatment) if treatment else DEFAULT_TREATMENT
