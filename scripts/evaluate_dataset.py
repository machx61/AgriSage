"""Fetch 26 real plant disease images from the PlantVillage repository,
run them through the AgriSage diagnosis and treatment pipeline, and verify matches.
"""
import json
import sys
from pathlib import Path
import requests
import toml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agrisage.disease_map import DISEASE_DISPLAY_MAP, display_name
from agrisage.gemini_tracker import get_initial_diagnosis
from agrisage.treatments_db import get_treatment_data

# Load API key
secrets_path = Path(".streamlit/secrets.toml")
api_key = toml.load(secrets_path)["GEMINI_API_KEY"]

CATEGORIES = [
    ("Tomato Early Blight", "Tomato___Early_blight", "tomato_early_blight"),
    ("Tomato Late Blight", "Tomato___Late_blight", "tomato_late_blight"),
    ("Tomato Yellow Leaf Curl", "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "tomato_leaf_curl_virus"),
    ("Tomato Healthy", "Tomato___healthy", "tomato_healthy"),
    ("Potato Early Blight", "Potato___Early_blight", "potato_early_blight"),
    ("Potato Late Blight", "Potato___Late_blight", "potato_late_blight"),
    ("Potato Healthy", "Potato___healthy", "potato_healthy"),
    ("Apple Scab", "Apple___Apple_scab", "apple_scab"),
    ("Apple Healthy", "Apple___healthy", "apple_healthy"),
    ("Capsicum Bacterial Spot", "Pepper,_bell___Bacterial_spot", "capsicum_bacterial_leaf_spot"),
    ("Capsicum Healthy", "Pepper,_bell___healthy", "capsicum_healthy"),
    ("Maize Northern Leaf Blight", "Corn_(maize)___Northern_Leaf_Blight", "corn_turcicum_leaf_blight"),
    ("Maize Healthy", "Corn_(maize)___healthy", "corn_healthy"),
]

headers = {"User-Agent": "AgriSage-Evaluation"}
allowed_classes = list(DISEASE_DISPLAY_MAP.keys())

test_items = []
print("Fetching real image URLs from repository...")
for title, folder, expected_key in CATEGORIES:
    url = f"https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color/{folder}"
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code == 200:
        files = r.json()
        # Take the first 2 images
        for i, f in enumerate(files[:2], 1):
            test_items.append({
                "title": f"{title} (Sample {i})",
                "folder": folder,
                "expected": expected_key,
                "file_name": f["name"],
                "download_url": f["download_url"],
            })
    else:
        print(f"Warning: could not list {folder} ({r.status_code})")

print(f"Collected {len(test_items)} test images. Starting diagnosis & treatment evaluation...\n")

results = []
for idx, item in enumerate(test_items, 1):
    title = item["title"]
    expected = item["expected"]
    url = item["download_url"]
    print(f"[{idx}/{len(test_items)}] {title}...", end=" ", flush=True)

    try:
        img_resp = requests.get(url, headers=headers, timeout=15)
        if img_resp.status_code != 200:
            print(f"Download failed (HTTP {img_resp.status_code})")
            continue
        image_bytes = img_resp.content

        # 1. Run diagnosis
        diagnosis = get_initial_diagnosis(api_key, image_bytes, allowed_classes)
        predicted = diagnosis.get("class")
        confidence = diagnosis.get("confidence", 0)

        exact_match = (predicted == expected)
        crop_match = bool(predicted and predicted.split("_")[0] == expected.split("_")[0])

        # 2. Get treatments
        treatments = get_treatment_data(predicted) if predicted else {}
        nf_cards = treatments.get("natural_farming", [])
        nf_bio = [c for c in nf_cards if any(k in c.get("action", "").lower() for k in ("jeevamrit", "beejamrit", "tonic", "coat", "microbe", "dung"))]
        nf_bot = [c for c in nf_cards if c not in nf_bio]

        bot_count = len(treatments.get("botanical", [])) + len(nf_bot)
        bio_count = len(treatments.get("biological", [])) + len(nf_bio)
        cul_count = len(treatments.get("cultural", [])) + len(treatments.get("local_practice", [])) + len(treatments.get("iks", []))

        status_str = "MATCH" if exact_match else ("CROP MATCH" if crop_match else "MISMATCH")
        print(f"-> {predicted} ({confidence}%) [{status_str}] | Treatments: {bot_count} bot, {bio_count} bio, {cul_count} cul")

        results.append({
            "idx": idx,
            "title": title,
            "expected_class": expected,
            "predicted_class": predicted,
            "display_name": display_name(predicted) if predicted else "Unknown",
            "confidence": confidence,
            "exact_match": exact_match,
            "crop_match": crop_match,
            "treatments": {
                "botanical": bot_count,
                "biological": bio_count,
                "cultural": cul_count,
                "total": bot_count + bio_count + cul_count
            }
        })
    except Exception as e:
        print(f"ERROR: {e}")

exact = sum(1 for r in results if r["exact_match"])
crop_ok = sum(1 for r in results if r["crop_match"])
total = len(results)

print("\n" + "="*80)
print(f"FINAL ACCURACY SUMMARY:")
print(f"  Exact Disease Matches: {exact}/{total} ({exact/total*100:.1f}%)")
print(f"  Crop-level Matches:    {crop_ok}/{total} ({crop_ok/total*100:.1f}%)")
print("="*80)

output_file = Path("evaluation_report.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump({"summary": {"total": total, "exact_matches": exact, "crop_matches": crop_ok}, "results": results}, f, indent=2)

print(f"Saved evaluation report to {output_file.resolve()}")

