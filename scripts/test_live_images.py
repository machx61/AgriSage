"""Test live plant disease images against AgriSage diagnosis and treatment pipeline.
"""
import json
import sys
from pathlib import Path
import toml
import urllib.parse
import urllib.request
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agrisage.disease_map import DISEASE_DISPLAY_MAP, display_name
from agrisage.gemini_tracker import get_initial_diagnosis
from agrisage.treatments_db import get_treatment_data

# Load API key
secrets_path = Path(".streamlit/secrets.toml")
api_key = toml.load(secrets_path)["GEMINI_API_KEY"]

# Test dataset: (Crop & Disease Name, Ground Truth Key, Image URL)
TEST_CASES = [
    # Tomatoes
    ("Tomato Early Blight", "tomato_early_blight",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Tomato___Early_blight/0012b9d2-2130-4a06-a834-b1f3af34f57e___RS_Erly.B%208389.JPG"),
    ("Tomato Late Blight", "tomato_late_blight",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Tomato___Late_blight/0003faa8-4b27-4c65-bf68-6d57380d3e35___RS_Late.B%204946.JPG"),
    ("Tomato Yellow Leaf Curl", "tomato_leaf_curl_virus",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Tomato___Tomato_Yellow_Leaf_Curl_Virus/0011031b-402a-4428-984e-03091e988ccf___UF.GRC_YLCV_Lab%2009307.JPG"),
    ("Tomato Healthy", "tomato_healthy",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Tomato___healthy/00014074-fba2-409f-9369-c485ab35a621___GH_HLLeaf%20259.JPG"),

    # Potatoes
    ("Potato Early Blight", "potato_early_blight",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Potato___Early_blight/001187a0-573b-432a-bfce-9cb194d87441___RS_Erly.B%209478.JPG"),
    ("Potato Late Blight", "potato_late_blight",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Potato___Late_blight/006955a3-00e9-4c66-86e1-432f8a7638b0___RS_Late.B%204932.JPG"),
    ("Potato Healthy", "potato_healthy",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Potato___healthy/00fc8ee8-5382-438e-9c49-c7e6a1477764___RS_HL%201864.JPG"),

    # Apples
    ("Apple Scab", "apple_scab",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Apple___Apple_scab/0007588c-c2e0-4f1f-829d-4de073dd3436___FREC_Scab%203335.JPG"),
    ("Apple Healthy", "apple_healthy",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Apple___healthy/0055f284-a2a7-47b0-8bd6-c7379d71c19d___RS_HL%207674.JPG"),

    # Capsicum / Bell Pepper
    ("Capsicum Bacterial Spot", "capsicum_bacterial_leaf_spot",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Pepper%2C_bell___Bacterial_spot/000665b2-dc09-4783-a4e4-a829e8c30c30___NREC_B.Spot%209123.JPG"),
    ("Capsicum Healthy", "capsicum_healthy",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Pepper%2C_bell___healthy/0010062a-29e7-4959-ac02-357f8e328770___JR_HL%207981.JPG"),

    # Maize / Corn
    ("Maize Northern Leaf Blight", "corn_turcicum_leaf_blight",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Corn_(maize)___Northern_Leaf_Blight/00a153dd-4f3a-40fa-ba8b-177aeecfd614___RS_NLB%204123.JPG"),
    ("Maize Healthy", "corn_healthy",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Corn_(maize)___healthy/0003157b-70c8-472e-8418-45be5012921a___R.S_HL%208312.JPG"),

    # More Tomatoes
    ("Tomato Septoria Leaf Spot", "tomato_early_blight",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Tomato___Septoria_leaf_spot/00f16781-53e3-4603-9ef6-b250dd11b229___JR_Sept.L.S%208415.JPG"),
    ("Tomato Spider Mites", "tomato_leaf_curl_virus",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Tomato___Spider_mites%20Two-spotted_spider_mite/0004f52c-4630-4562-b6d2-e22301140939___UMIR_Sp.M%209351.JPG"),

    # More Potatoes
    ("Potato Early Blight (Sample 2)", "potato_early_blight",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Potato___Early_blight/03b07b1a-2977-4340-97e3-0d8011287e07___RS_Erly.B%206775.JPG"),
    ("Potato Late Blight (Sample 2)", "potato_late_blight",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Potato___Late_blight/0168e378-6202-4f01-9a79-242d99d3ad39___RS_Late.B%205096.JPG"),

    # More Apples
    ("Apple Scab (Sample 2)", "apple_scab",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Apple___Apple_scab/01a3cf3f-94c1-44d5-8973-e5fb4daeb45e___FREC_Scab%203340.JPG"),
    ("Apple Black Rot / Scab", "apple_scab",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Apple___Black_rot/0139bc6d-391c-4e17-a59e-7718176fae3f___JR_FrSL%208501.JPG"),

    # More Peppers
    ("Capsicum Bacterial Spot (Sample 2)", "capsicum_bacterial_leaf_spot",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Pepper%2C_bell___Bacterial_spot/01be457a-1cf0-45e8-b807-6f81dfc95c89___NREC_B.Spot%201880.JPG"),
    ("Capsicum Healthy (Sample 2)", "capsicum_healthy",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Pepper%2C_bell___healthy/017efad8-c290-4889-8d75-beae0d0ae1be___JR_HL%208468.JPG"),

    # More Maize
    ("Maize Northern Leaf Blight (Sample 2)", "corn_turcicum_leaf_blight",
     "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Corn_(maize)___Northern_Leaf_Blight/017eb3ec-cb24-4f05-8919-4b62dbd669ec___RS_NLB%203603.JPG"),

    # Rice
    ("Rice Bacterial Leaf Blight", "rice_bacterial_leaf_blight",
     "https://upload.wikimedia.org/wikipedia/commons/b/b1/Bacterial_blight_of_rice.jpeg"),

    # Wheat
    ("Wheat Rust", "wheat_yellow_rust",
     "https://upload.wikimedia.org/wikipedia/commons/d/d4/Wheat_leaf_rust_on_wheat.jpg"),

    # Apple Scab Wikimedia
    ("Apple Scab (Wikimedia)", "apple_scab",
     "https://upload.wikimedia.org/wikipedia/commons/5/50/Apple_scab.jpg"),
]

print(f"Total test images: {len(TEST_CASES)}")
allowed_classes = list(DISEASE_DISPLAY_MAP.keys())

results = []
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AgriSage/1.0"}

for idx, (title, expected_key, url) in enumerate(TEST_CASES, 1):
    print(f"[{idx}/{len(TEST_CASES)}] Testing: {title}...", end=" ", flush=True)
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"FAILED (HTTP {resp.status_code})")
            results.append({"title": title, "expected": expected_key, "predicted": None, "match": False, "error": f"HTTP {resp.status_code}"})
            continue
        image_bytes = resp.content

        # Run diagnosis
        diagnosis = get_initial_diagnosis(api_key, image_bytes, allowed_classes)
        pred_class = diagnosis.get("class")
        confidence = diagnosis.get("confidence", 0)

        # Check match: either exact match or same crop + compatible disease family
        exact_match = (pred_class == expected_key)
        crop_match = pred_class and pred_class.split("_")[0] == expected_key.split("_")[0]

        # Get treatment plan
        treatments = get_treatment_data(pred_class) if pred_class else {}
        nf_cards = treatments.get("natural_farming", [])
        nf_bio = [c for c in nf_cards if any(k in c.get("action", "").lower() for k in ("jeevamrit", "beejamrit", "tonic", "coat", "microbe", "dung"))]
        nf_bot = [c for c in nf_cards if c not in nf_bio]

        bot_count = len(treatments.get("botanical", [])) + len(nf_bot)
        bio_count = len(treatments.get("biological", [])) + len(nf_bio)
        cul_count = len(treatments.get("cultural", [])) + len(treatments.get("local_practice", [])) + len(treatments.get("iks", []))

        print(f"-> {pred_class} ({confidence}%) [Exact: {exact_match}, Crop: {crop_match}]")
        results.append({
            "idx": idx,
            "title": title,
            "expected": expected_key,
            "predicted": pred_class,
            "display": display_name(pred_class) if pred_class else "Unknown",
            "confidence": confidence,
            "exact_match": exact_match,
            "crop_match": crop_match,
            "treatments": {"botanical": bot_count, "biological": bio_count, "cultural": cul_count}
        })
    except Exception as exc:
        print(f"ERROR: {exc}")
        results.append({"title": title, "expected": expected_key, "predicted": None, "match": False, "error": str(exc)})

# Summary
exact_matches = sum(1 for r in results if r.get("exact_match"))
crop_matches = sum(1 for r in results if r.get("crop_match"))
total = len(results)

print("\n" + "="*70)
print(f"EVALUATION SUMMARY: {exact_matches}/{total} exact matches ({exact_matches/total*100:.1f}%), {crop_matches}/{total} crop matches ({crop_matches/total*100:.1f}%)")
print("="*70)

with open("test_evaluation_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("Saved detailed results to test_evaluation_results.json")
