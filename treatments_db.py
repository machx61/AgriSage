"""
Agrisage Knowledge Base
Regional Context: Himachal Pradesh (Hills Zone)
Focus: Indigenous Knowledge Systems (IKS) & Vrikshayurveda Practices
"""
import json
from pathlib import Path
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent / "data" / "diseases"

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
            "action": "General Seed Health",
            "emoji": "🐄",
            "theme": "butter_yellow",
            "summary": "Keep seeds healthy with a traditional ash-and-dung blanket or cow urine soak!",
            "how": "Mix ash and cow dung together and apply to seeds, or soak in cow urine before sowing.",
            "frequency": "Once, before sowing"
        }
    ],
    "biological": []
}

@st.cache_data
def load_disease_data(crop_name: str) -> dict:
    """Load the disease JSON for a specific crop."""
    # handle alias
    if crop_name == "corn":
        crop_name = "maize"
    elif crop_name == "pepper":
        crop_name = "okra"
        
    file_path = DATA_DIR / f"{crop_name}.json"
    if not file_path.exists():
        return {}
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_treatment_data(predicted_class: str):
    """Normalize YOLO label, route to the correct crop dict, and retrieve matching treatment profile."""
    key = predicted_class.lower().strip()
    
    if "healthy" in key:
        return HEALTHY_TREATMENT
        
    parts = key.split("_", 1) 
    
    if len(parts) != 2:
        return DEFAULT_TREATMENT
        
    crop = parts[0]
    disease = parts[1]

    data = load_disease_data(crop)
    if not data:
        return DEFAULT_TREATMENT

    if crop == "tomato":
        if "yellow_virus" in disease or "mosaic_virus" in disease or "leaf_curl" in disease:
            return data.get("leaf_curl_virus", DEFAULT_TREATMENT)
        if "nematode" in disease:
            return data.get("root_knot_nematode", DEFAULT_TREATMENT)
        if "stem" in disease or "wound" in disease:
            return data.get("stem_wound_damage", DEFAULT_TREATMENT)
                
    elif crop == "potato":
        if "scurf" in disease or "scab" in disease:
            return data.get("black_scurf_common_scab", DEFAULT_TREATMENT)
        if "wilt" in disease:
            return data.get("bacterial_wilt", DEFAULT_TREATMENT)
        if "nematode" in disease:
            return data.get("root_knot_nematode", DEFAULT_TREATMENT)
        if "moth" in disease:
            return data.get("potato_tuber_moth", DEFAULT_TREATMENT)

    elif crop == "rice":
        if "hispa" in disease:
            return data.get("rice_hispa", DEFAULT_TREATMENT)
        if "storage" in disease or "post_harvest" in disease:
            return data.get("post_harvest_storage", DEFAULT_TREATMENT)
                
    elif crop == "wheat":
        if "leaf_rust" in disease or "stripe_rust" in disease:
            return data.get("yellow_rust", DEFAULT_TREATMENT)
        if "storage" in disease or "harvest" in disease:
            return data.get("storage_and_harvest", DEFAULT_TREATMENT)
            
    # Generic matching if no specific aliases matched
    for db_key in data:
        if db_key in disease:
            return data[db_key]

    return DEFAULT_TREATMENT
