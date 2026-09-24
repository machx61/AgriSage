# disease_map.py
"""Supported diagnosis classes.

Only crops with a treatment knowledge base in data/diseases/ are supported.
Each class maps to its display name and the (crop_file, kb_key) entry that
holds its treatments; healthy classes map to None.
"""

SUPPORTED_CROPS = ["Maize (Corn)", "Okra", "Potato", "Rice", "Tomato", "Wheat"]

# class -> (display name, (crop_file, kb_key) or None for healthy)
_CLASSES = {
    "corn_healthy": ("Maize - Healthy", None),
    "corn_turcicum_leaf_blight": ("Maize - Turcicum (Northern) Leaf Blight", ("maize", "turcicum_leaf_blight")),
    "corn_banded_leaf_sheath_blight": ("Maize - Banded Leaf & Sheath Blight", ("maize", "banded_leaf_and_sheath_blight")),
    "corn_fall_armyworm": ("Maize - Fall Armyworm", ("maize", "fall_armyworm")),
    "corn_stalk_rot": ("Maize - Stalk Rot", ("maize", "stalk_rot")),

    "okra_healthy": ("Okra - Healthy", None),
    "okra_yellow_vein_mosaic_virus": ("Okra - Yellow Vein Mosaic Virus", ("okra", "yellow_vein_mosaic_virus")),
    "okra_cercospora_leaf_spot": ("Okra - Cercospora Leaf Spot", ("okra", "cercospora_leaf_spot")),
    "okra_damping_off_root_rot": ("Okra - Damping Off & Root Rot", ("okra", "damping_off_root_rot")),
    "okra_fusarium_wilt": ("Okra - Fusarium Wilt", ("okra", "fusarium_wilt")),
    "okra_powdery_mildew": ("Okra - Powdery Mildew", ("okra", "powdery_mildew")),

    "potato_healthy": ("Potato - Healthy", None),
    "potato_early_blight": ("Potato - Early Blight", ("potato", "early_blight")),
    "potato_late_blight": ("Potato - Late Blight", ("potato", "late_blight")),
    "potato_black_scurf_common_scab": ("Potato - Black Scurf & Common Scab", ("potato", "black_scurf_common_scab")),
    "potato_bacterial_wilt": ("Potato - Bacterial Wilt", ("potato", "bacterial_wilt")),
    "potato_root_knot_nematode": ("Potato - Root-Knot Nematode", ("potato", "root_knot_nematode")),
    "potato_tuber_moth": ("Potato - Tuber Moth", ("potato", "potato_tuber_moth")),

    "rice_healthy": ("Rice - Healthy", None),
    "rice_bacterial_leaf_blight": ("Rice - Bacterial Leaf Blight & Blast", ("rice", "bacterial_leaf_blight")),
    "rice_hispa": ("Rice - Hispa", ("rice", "rice_hispa")),

    "tomato_healthy": ("Tomato - Healthy", None),
    "tomato_leaf_curl_virus": ("Tomato - Leaf Curl Virus", ("tomato", "leaf_curl_virus")),
    "tomato_early_blight": ("Tomato - Early Blight", ("tomato", "early_blight")),
    # Same pathogen (Phytophthora infestans) as potato late blight, so it shares those treatments
    "tomato_late_blight": ("Tomato - Late Blight", ("potato", "late_blight")),
    "tomato_powdery_mildew": ("Tomato - Powdery Mildew", ("tomato", "powdery_mildew")),
    "tomato_root_knot_nematode": ("Tomato - Root-Knot Nematode", ("tomato", "root_knot_nematode")),
    "tomato_stem_wound_damage": ("Tomato - Stem Damage & Cracking", ("tomato", "stem_wound_damage")),

    "wheat_healthy": ("Wheat - Healthy", None),
    "wheat_yellow_rust": ("Wheat - Yellow (Stripe) Rust", ("wheat", "yellow_rust")),
    "wheat_powdery_mildew": ("Wheat - Powdery Mildew", ("wheat", "powdery_mildew")),
    "wheat_loose_smut": ("Wheat - Loose Smut", ("wheat", "loose_smut")),
    "wheat_karnal_bunt": ("Wheat - Karnal Bunt", ("wheat", "karnal_bunt")),
}

DISEASE_DISPLAY_MAP = {cls: display for cls, (display, _) in _CLASSES.items()}
CLASS_TO_KB = {cls: kb for cls, (_, kb) in _CLASSES.items()}

# Special answers the diagnosis model may give instead of a supported class.
UNSUPPORTED = "unsupported"
NOT_A_LEAF = "not_a_leaf"


def display_name(raw_class: str) -> str:
    return DISEASE_DISPLAY_MAP.get(raw_class, raw_class.replace("_", " ").title())
