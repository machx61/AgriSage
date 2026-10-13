"""Run ~30 labelled internet photos through the AgriSage diagnosis pipeline and
check that the treatments shown match the expected disease.

Images come from the PlantVillage dataset (GitHub) and Wikimedia Commons.
Each photo is diagnosed the way the app does it with no crop selected; any photo
that comes out wrong is retried with the crop hint, as a farmer who knows the
crop would. The report is written to evaluation_30.json.

Usage: python scripts/eval_30_images.py [case numbers to run, e.g. 6 19 21]
"""
import json
import sys
import time
from pathlib import Path

import requests
import toml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agrisage.disease_map import (  # noqa: E402
    DISEASE_DISPLAY_MAP, OTHER_DISEASE, SUPPORTED_CROPS, UNSUPPORTED, NOT_A_LEAF, CROP_MISMATCH,
    classes_for_crop, display_name,
)
from agrisage.gemini_tracker import get_initial_diagnosis  # noqa: E402
from agrisage.images import make_jpeg  # noqa: E402
from agrisage.treatments_db import get_treatment_data, group_treatments  # noqa: E402

API_KEY = toml.load(ROOT / ".streamlit" / "secrets.toml")["GEMINI_API_KEY"]
HEADERS = {"User-Agent": "AgriSage-eval/1.0 (research)"}
PV = "https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color/"
COMMONS = "https://commons.wikimedia.org/w/api.php"

# (expected class, source, folder / Commons file title, index)
# expected "other_disease" = real disease on a supported crop that is not in our database
# expected "unsupported"   = crop we do not cover
CASES = [
    ("tomato_early_blight", "pv", "Tomato___Early_blight", 3),
    ("tomato_late_blight", "pv", "Tomato___Late_blight", 3),
    ("tomato_leaf_curl_virus", "pv", "Tomato___Tomato_Yellow_Leaf_Curl_Virus", 3),
    ("tomato_septoria_leaf_spot", "pv", "Tomato___Septoria_leaf_spot", 3),
    ("tomato_healthy", "pv", "Tomato___healthy", 3),
    ("tomato_bacterial_wilt", "cm", "File:Tomato Bacterial wilt (Pathogen Ralstonia solanacearum) (12091835495).jpg", 0),
    ("potato_early_blight", "pv", "Potato___Early_blight", 3),
    ("potato_late_blight", "pv", "Potato___Late_blight", 3),
    ("potato_healthy", "pv", "Potato___healthy", 3),
    ("apple_scab", "pv", "Apple___Apple_scab", 3),
    ("apple_healthy", "pv", "Apple___healthy", 3),
    ("corn_common_rust", "pv", "Corn_(maize)___Common_rust_", 3),
    ("corn_gray_leaf_spot", "pv", "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", 3),
    ("corn_turcicum_leaf_blight", "pv", "Corn_(maize)___Northern_Leaf_Blight", 3),
    ("corn_healthy", "pv", "Corn_(maize)___healthy", 3),
    ("capsicum_bacterial_leaf_spot", "pv", "Pepper,_bell___Bacterial_spot", 3),
    ("capsicum_healthy", "pv", "Pepper,_bell___healthy", 3),
    ("rice_sheath_blight", "cm", "File:RiceSheathArk.jpg", 0),
    ("wheat_brown_rust", "cm", "File:Wheat leaf rust on wheat.jpg", 0),
    ("wheat_aphid", "cm", "File:Russian wheat aphid.jpg", 0),
    ("cabbage_black_rot", "cm", "File:Black rot of cabbage symptoms.jpg", 0),
    ("pea_powdery_mildew", "cm", "File:Erbsen Echter Mehltau-4-JS.jpg", 0),
    ("mustard_white_rust", "cm", "File:Mustard- White rust.jpg", 0),
    (OTHER_DISEASE, "pv", "Tomato___Tomato_mosaic_virus", 3),
    (OTHER_DISEASE, "pv", "Tomato___Leaf_Mold", 3),
    (OTHER_DISEASE, "pv", "Tomato___Target_Spot", 3),
    ("brinjal_little_leaf", "cm", "File:Brinjal Little leaf phytoplasma.jpg", 0),
    (UNSUPPORTED, "pv", "Grape___Black_rot", 3),
    (UNSUPPORTED, "pv", "Strawberry___Leaf_scorch", 3),
    (UNSUPPORTED, "pv", "Squash___Powdery_mildew", 3),
]


def pv_url(folder: str, index: int) -> str:
    r = requests.get(PV + requests.utils.quote(folder), headers=HEADERS, timeout=20)
    r.raise_for_status()
    files = sorted(r.json(), key=lambda f: f["name"])
    return files[index * 7 % len(files)]["download_url"]  # spread picks across the folder


def commons_url(title: str) -> str:
    r = requests.get(COMMONS, headers=HEADERS, timeout=20, params={
        "action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url",
        "iiurlwidth": 1000, "format": "json"})
    page = next(iter(r.json()["query"]["pages"].values()))
    info = page["imageinfo"][0]
    return info.get("thumburl") or info["url"]


def fetch(source: str, ref: str, index: int):
    url = pv_url(ref, index) if source == "pv" else commons_url(ref)
    for attempt in range(5):  # Wikimedia rate-limits bursts
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 429:
            break
        time.sleep(10 * (attempt + 1))
    resp.raise_for_status()
    return url, resp.content


def treatments_summary(raw_class: str) -> dict:
    info = get_treatment_data(raw_class)
    grouped = group_treatments(info)
    return {
        "name": info.get("name"),
        "healthy": raw_class.endswith("_healthy"),
        "cards": {k: [c["action"] for c in v] for k, v in grouped.items()},
    }


def verdict(expected: str, got: str | None) -> str:
    if got == expected:
        return "exact"
    if got is None:
        return "error"
    if expected in (OTHER_DISEASE, UNSUPPORTED):
        # not in the database: any "no verified treatment" answer is the safe outcome
        return "safe" if got in (OTHER_DISEASE, UNSUPPORTED, NOT_A_LEAF) else "WRONG"
    if got in (OTHER_DISEASE, UNSUPPORTED, NOT_A_LEAF):
        return "abstained"
    if get_treatment_data(got) is get_treatment_data(expected) or (
        get_treatment_data(got).get("name") == get_treatment_data(expected).get("name")
        and got.split("_")[0] == expected.split("_")[0]
    ):
        return "same-treatment"
    if got.split("_")[0] == expected.split("_")[0]:
        return "wrong-disease"
    return "wrong-crop"


def main():
    only = {int(a) for a in sys.argv[1:]}
    rows = []
    for n, (expected, source, ref, index) in enumerate(CASES, 1):
        if only and n not in only:
            continue
        label = f"[{n:2}/{len(CASES)}] {expected} <- {ref.split('/')[-1][:50]}"
        try:
            url, raw = fetch(source, ref, index)
            jpeg = make_jpeg(raw, 800)
        except Exception as exc:  # noqa: BLE001
            print(label, "-> DOWNLOAD FAILED", exc)
            rows.append({"expected": expected, "ref": ref, "error": f"download: {exc}"})
            continue

        result = get_initial_diagnosis(API_KEY, jpeg, list(DISEASE_DISPLAY_MAP))
        got = result.get("class")
        row = {
            "expected": expected, "source": source, "ref": ref, "url": url,
            "auto": {"class": got, "confidence": result.get("confidence"), "name": result.get("name"),
                     "disagreed": result.get("disagreed", False), "alternative": result.get("alternative"),
                     "verdict": verdict(expected, got)},
        }
        if got and got not in (OTHER_DISEASE, UNSUPPORTED, NOT_A_LEAF, CROP_MISMATCH):
            row["auto"]["treatments"] = treatments_summary(got)

        # A farmer who knows the crop would pick it; retry wrong answers that way
        crop_key = expected.split("_")[0]
        if row["auto"]["verdict"] not in ("exact", "same-treatment", "safe") and crop_key in SUPPORTED_CROPS:
            hinted = get_initial_diagnosis(API_KEY, jpeg, classes_for_crop(crop_key), SUPPORTED_CROPS[crop_key])
            hgot = hinted.get("class")
            row["with_crop_hint"] = {"class": hgot, "confidence": hinted.get("confidence"),
                                     "name": hinted.get("name"), "verdict": verdict(expected, hgot)}
            if hgot and hgot not in (OTHER_DISEASE, UNSUPPORTED, NOT_A_LEAF, CROP_MISMATCH):
                row["with_crop_hint"]["treatments"] = treatments_summary(hgot)

        rows.append(row)
        extra = f" | hint -> {row['with_crop_hint']['class']} ({row['with_crop_hint']['verdict']})" if "with_crop_hint" in row else ""
        print(f"{label}\n      auto -> {got} {result.get('confidence')}% ({row['auto']['verdict']}){extra}", flush=True)
        time.sleep(1)

    out = ROOT / ("evaluation_30_retry.json" if only else "evaluation_30.json")
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    counts = {}
    for r in rows:
        v = r.get("auto", {}).get("verdict", "download-failed")
        counts[v] = counts.get(v, 0) + 1
    print("\nAUTO-DETECT:", counts)
    print("Report:", out)


if __name__ == "__main__":
    main()
