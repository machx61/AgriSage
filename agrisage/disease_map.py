# disease_map.py
"""Supported diagnosis classes.

Only crops with a treatment knowledge base in data/diseases/ are supported.
Each class maps to its display name and the (crop_file, kb_key) entry that
holds its treatments; healthy classes map to None.
"""

# class -> (display name, (crop_file, kb_key) or None for healthy)
_CLASSES = {
    "apple_healthy": ("Apple - Healthy", None),
    "apple_scab": ("Apple - Scab", ("apple", "scab")),
    "apple_powdery_mildew": ("Apple - Powdery Mildew", ("apple", "powdery_mildew")),
    "apple_marssonina_blotch": ("Apple - Marssonina Leaf Blotch", ("apple", "marssonina_blotch")),
    "apple_alternaria_blotch": ("Apple - Alternaria Leaf Blotch", ("apple", "alternaria_blotch")),
    "apple_woolly_aphid": ("Apple - Woolly Apple Aphid", ("apple", "woolly_aphid")),
    "apple_mite_bronzing": ("Apple - Mite Bronzing", ("apple", "mite_bronzing")),

    "brinjal_healthy": ("Brinjal - Healthy", None),
    "brinjal_shoot_fruit_borer": ("Brinjal - Shoot & Fruit Borer", ("brinjal", "shoot_fruit_borer")),
    "brinjal_phomopsis_blight": ("Brinjal - Phomopsis Blight & Fruit Rot", ("brinjal", "phomopsis_blight")),
    "brinjal_little_leaf": ("Brinjal - Little Leaf", ("brinjal", "little_leaf")),
    "brinjal_bacterial_wilt": ("Brinjal - Bacterial Wilt", ("brinjal", "bacterial_wilt")),
    "brinjal_hadda_beetle": ("Brinjal - Hadda (Epilachna) Beetle", ("brinjal", "hadda_beetle")),

    "cabbage_healthy": ("Cabbage - Healthy", None),
    "cabbage_black_rot": ("Cabbage - Black Rot", ("cabbage", "black_rot")),
    "cabbage_downy_mildew": ("Cabbage - Downy Mildew", ("cabbage", "downy_mildew")),
    "cabbage_alternaria_leaf_spot": ("Cabbage - Alternaria Leaf Spot", ("cabbage", "alternaria_leaf_spot")),
    "cabbage_diamondback_moth": ("Cabbage - Diamondback Moth", ("cabbage", "diamondback_moth")),
    "cabbage_cabbage_butterfly": ("Cabbage - Cabbage Butterfly Caterpillars", ("cabbage", "cabbage_butterfly")),
    "cabbage_aphid": ("Cabbage - Aphid", ("cabbage", "aphid")),
    "cabbage_clubroot": ("Cabbage - Clubroot", ("cabbage", "clubroot")),

    "capsicum_healthy": ("Capsicum - Healthy", None),
    "capsicum_phytophthora_blight": ("Capsicum - Phytophthora Blight", ("capsicum", "phytophthora_blight")),
    "capsicum_anthracnose": ("Capsicum - Anthracnose & Die-back", ("capsicum", "anthracnose")),
    "capsicum_bacterial_leaf_spot": ("Capsicum - Bacterial Leaf Spot", ("capsicum", "bacterial_leaf_spot")),
    "capsicum_powdery_mildew": ("Capsicum - Powdery Mildew", ("capsicum", "powdery_mildew")),
    "capsicum_cercospora_leaf_spot": ("Capsicum - Cercospora Leaf Spot", ("capsicum", "cercospora_leaf_spot")),
    "capsicum_leaf_curl_mosaic": ("Capsicum - Leaf Curl & Mosaic", ("capsicum", "leaf_curl_mosaic")),

    "carrot_healthy": ("Carrot - Healthy", None),
    "carrot_alternaria_leaf_blight": ("Carrot - Alternaria Leaf Blight", ("carrot", "alternaria_leaf_blight")),
    "carrot_cercospora_leaf_spot": ("Carrot - Cercospora Leaf Spot", ("carrot", "cercospora_leaf_spot")),
    "carrot_powdery_mildew": ("Carrot - Powdery Mildew", ("carrot", "powdery_mildew")),

    # Cauliflower shares the cabbage knowledge base: same pathogens and pests, same treatments
    "cauliflower_healthy": ("Cauliflower - Healthy", None),
    "cauliflower_black_rot": ("Cauliflower - Black Rot", ("cabbage", "black_rot")),
    "cauliflower_downy_mildew": ("Cauliflower - Downy Mildew", ("cabbage", "downy_mildew")),
    "cauliflower_alternaria_leaf_spot": ("Cauliflower - Alternaria Leaf Spot", ("cabbage", "alternaria_leaf_spot")),
    "cauliflower_diamondback_moth": ("Cauliflower - Diamondback Moth", ("cabbage", "diamondback_moth")),
    "cauliflower_cabbage_butterfly": ("Cauliflower - Cabbage Butterfly Caterpillars", ("cabbage", "cabbage_butterfly")),
    "cauliflower_aphid": ("Cauliflower - Aphid", ("cabbage", "aphid")),
    "cauliflower_clubroot": ("Cauliflower - Clubroot", ("cabbage", "clubroot")),

    "corn_healthy": ("Maize - Healthy", None),
    "corn_turcicum_leaf_blight": ("Maize - Turcicum (Northern) Leaf Blight", ("maize", "turcicum_leaf_blight")),
    "corn_banded_leaf_sheath_blight": ("Maize - Banded Leaf & Sheath Blight", ("maize", "banded_leaf_and_sheath_blight")),
    "corn_fall_armyworm": ("Maize - Fall Armyworm", ("maize", "fall_armyworm")),
    "corn_stalk_rot": ("Maize - Stalk Rot", ("maize", "stalk_rot")),
    "corn_common_rust": ("Maize - Common Rust", ("maize", "common_rust")),
    "corn_gray_leaf_spot": ("Maize - Gray Leaf Spot", ("maize", "gray_leaf_spot")),

    "cucumber_healthy": ("Cucumber - Healthy", None),
    "cucumber_downy_mildew": ("Cucumber - Downy Mildew", ("cucumber", "downy_mildew")),
    "cucumber_powdery_mildew": ("Cucumber - Powdery Mildew", ("cucumber", "powdery_mildew")),
    "cucumber_mosaic_virus": ("Cucumber - Mosaic Virus", ("cucumber", "mosaic_virus")),
    "cucumber_red_pumpkin_beetle": ("Cucumber - Red Pumpkin Beetle", ("cucumber", "red_pumpkin_beetle")),
    "cucumber_leaf_miner": ("Cucumber - Serpentine Leaf Miner", ("cucumber", "leaf_miner")),

    "garlic_healthy": ("Garlic - Healthy", None),
    "garlic_stemphylium_blight": ("Garlic - Stemphylium Blight", ("garlic", "stemphylium_blight")),
    "garlic_rust": ("Garlic - Rust", ("garlic", "rust")),
    "garlic_basal_white_rot": ("Garlic - Basal Rot & White Rot", ("garlic", "basal_white_rot")),
    "garlic_thrips": ("Garlic - Thrips", ("garlic", "thrips")),
    # Same pathogen as onion purple blotch, so it shares those treatments
    "garlic_purple_blotch": ("Garlic - Purple Blotch", ("onion", "purple_blotch")),

    "mustard_healthy": ("Mustard - Healthy", None),
    "mustard_alternaria_blight": ("Mustard - Alternaria Blight", ("mustard", "alternaria_blight")),
    "mustard_white_rust": ("Mustard - White Rust", ("mustard", "white_rust")),
    "mustard_downy_mildew": ("Mustard - Downy Mildew", ("mustard", "downy_mildew")),
    "mustard_powdery_mildew": ("Mustard - Powdery Mildew", ("mustard", "powdery_mildew")),
    "mustard_aphid": ("Mustard - Aphid", ("mustard", "aphid")),
    "mustard_sawfly": ("Mustard - Sawfly (Shot-Hole Seedlings)", ("mustard", "sawfly")),

    "okra_healthy": ("Okra - Healthy", None),
    "okra_yellow_vein_mosaic_virus": ("Okra - Yellow Vein Mosaic Virus", ("okra", "yellow_vein_mosaic_virus")),
    "okra_cercospora_leaf_spot": ("Okra - Cercospora Leaf Spot", ("okra", "cercospora_leaf_spot")),
    "okra_damping_off_root_rot": ("Okra - Damping Off & Root Rot", ("okra", "damping_off_root_rot")),
    "okra_fusarium_wilt": ("Okra - Fusarium Wilt", ("okra", "fusarium_wilt")),
    "okra_powdery_mildew": ("Okra - Powdery Mildew", ("okra", "powdery_mildew")),

    "onion_healthy": ("Onion - Healthy", None),
    "onion_purple_blotch": ("Onion - Purple Blotch", ("onion", "purple_blotch")),
    "onion_stemphylium_blight": ("Onion - Stemphylium Leaf Blight", ("onion", "stemphylium_blight")),
    "onion_downy_mildew": ("Onion - Downy Mildew", ("onion", "downy_mildew")),
    # Thrips on onion and garlic are managed the same way, so onion shares the garlic entry
    "onion_thrips": ("Onion - Thrips", ("garlic", "thrips")),
    "onion_basal_rot": ("Onion - Basal Rot", ("onion", "basal_rot")),

    "pea_healthy": ("Pea - Healthy", None),
    "pea_powdery_mildew": ("Pea - Powdery Mildew", ("pea", "powdery_mildew")),
    "pea_rust": ("Pea - Rust", ("pea", "rust")),
    "pea_ascochyta_blight": ("Pea - Ascochyta Blight", ("pea", "ascochyta_blight")),
    "pea_leaf_miner": ("Pea - Leaf Miner", ("pea", "leaf_miner")),
    "pea_aphid": ("Pea - Aphid", ("pea", "aphid")),
    "pea_root_rot_wilt": ("Pea - Root Rot & Wilt", ("pea", "root_rot_wilt")),

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
    "rice_brown_spot": ("Rice - Brown Spot", ("rice", "brown_spot")),
    "rice_sheath_blight": ("Rice - Sheath Blight", ("rice", "sheath_blight")),

    "spinach_healthy": ("Spinach - Healthy", None),
    "spinach_downy_mildew": ("Spinach - Downy Mildew", ("spinach", "downy_mildew")),
    "spinach_cercospora_leaf_spot": ("Spinach - Cercospora Leaf Spot", ("spinach", "cercospora_leaf_spot")),
    "spinach_leaf_miner": ("Spinach - Leaf Miner", ("spinach", "leaf_miner")),
    "spinach_aphid": ("Spinach - Aphid", ("spinach", "aphid")),

    "tomato_healthy": ("Tomato - Healthy", None),
    "tomato_leaf_curl_virus": ("Tomato - Leaf Curl Virus", ("tomato", "leaf_curl_virus")),
    "tomato_bacterial_wilt": ("Tomato - Bacterial Wilt", ("tomato", "bacterial_wilt")),
    "tomato_septoria_leaf_spot": ("Tomato - Septoria Leaf Spot", ("tomato", "septoria_leaf_spot")),
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
    "wheat_brown_rust": ("Wheat - Brown (Leaf) Rust", ("wheat", "brown_rust")),
    "wheat_aphid": ("Wheat - Aphid", ("wheat", "aphid")),
}

DISEASE_DISPLAY_MAP = {cls: display for cls, (display, _) in _CLASSES.items()}
CLASS_TO_KB = {cls: kb for cls, (_, kb) in _CLASSES.items()}
# crop key (class prefix) -> crop name exactly as results show it, e.g. "corn" -> "Maize"
SUPPORTED_CROPS = {cls.split("_")[0]: display.partition(" - ")[0] for cls, (display, _) in _CLASSES.items()}

# Special answers the diagnosis model may give instead of a supported class.
UNSUPPORTED = "unsupported"
NOT_A_LEAF = "not_a_leaf"
# Given when the crop is one we support but the problem is not in our list.
OTHER_DISEASE = "other_disease"
# Given when the farmer named a crop but the photo clearly shows a different plant.
CROP_MISMATCH = "crop_mismatch"


def classes_for_crop(crop_key: str) -> list[str]:
    """Diagnosis classes belonging to one crop, e.g. "corn" -> corn_healthy, corn_fall_armyworm, ..."""
    return [cls for cls in _CLASSES if cls.split("_")[0] == crop_key]


def display_name(raw_class: str) -> str:
    return DISEASE_DISPLAY_MAP.get(raw_class, raw_class.replace("_", " ").title())
