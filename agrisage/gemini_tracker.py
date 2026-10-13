"""Gemini calls for leaf diagnosis and plant-progress tracking.

Images are passed as JPEG bytes. Responses are constrained with a JSON schema,
so Gemini always returns parseable JSON with the expected keys.
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor
import threading
from functools import lru_cache

import httpx
from google import genai
from google.genai import errors, types

from agrisage.disease_map import CROP_MISMATCH, NOT_A_LEAF, OTHER_DISEASE, UNSUPPORTED

# Tried in order; when one is overloaded the next one is used.
MODELS = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
MODEL = MODELS[0]

STATUS_LABELS = ["improving", "stable", "worsening", "recovered"]

_S = types.Schema
_T = types.Type

# Independent models asked up front; a third breaks a tie.
VOTES_FIRST_ROUND = 2

REQUEST_TIMEOUT_S = 40   # one request
TOTAL_TIMEOUT_S = 90     # all attempts together, so the app never hangs


@lru_cache(maxsize=4)
def _build_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_S * 1000))


def _client(api_key: str) -> genai.Client:
    # lru_cache alone lets two threads each build a client on a miss; the one
    # that loses is garbage-collected and closes the connection the other is using.
    with _client_lock:
        return _build_client(api_key)


_client_lock = threading.Lock()


class GeminiTimeout(Exception):
    pass


# Free-tier models often answer "503 high demand", "504 deadline exceeded" or
# "429 rate limit"; these are worth retrying on another model.
_RETRY_CODES = {429, 500, 503, 504}


def _generate(
    api_key: str, prompt: str, images: list[bytes], schema: types.Schema, models: list[str] | None = None
) -> dict:
    parts = [prompt] + [types.Part.from_bytes(data=img, mime_type="image/jpeg") for img in images]
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    deadline = time.monotonic() + TOTAL_TIMEOUT_S
    last_error = None
    for round_no in range(2):
        for model in models or MODELS:
            if time.monotonic() >= deadline:
                raise last_error or GeminiTimeout()
            try:
                response = _client(api_key).models.generate_content(model=model, contents=parts, config=config)
                return json.loads(response.text)
            except errors.APIError as e:
                if e.code not in _RETRY_CODES:
                    raise
                last_error = e
            except httpx.TimeoutException:
                last_error = GeminiTimeout()
        if round_no == 0:
            time.sleep(3)
    raise last_error


def friendly_error(e: Exception) -> str:
    """Short, readable message for errors shown in the app."""
    if isinstance(e, GeminiTimeout):
        return "This is taking too long. Please try again in a minute."
    if isinstance(e, errors.APIError):
        if e.code == 429:
            return "Too many scans in a short time. Please wait a minute and try again."
        if e.code in (500, 503, 504):
            return "The service is busy right now. Please try again in a moment."
        if e.code in (400, 401, 403):
            return "Something went wrong. Please try again later."
    return "Something went wrong. Please try again."


def _clamp(value, low: int, high: int, default: int) -> int:
    try:
        return max(low, min(high, int(value)))
    except (TypeError, ValueError):
        return default


def _diagnose_once(
    api_key: str, image_jpeg: bytes, allowed_classes: list[str], crop_name: str | None, models: list[str]
) -> dict:
    if crop_name:
        crop_line = f"""The farmer says this plant is {crop_name}; take that as given unless the photo clearly shows a different kind of plant (then use "{CROP_MISMATCH}")."""
        extra_classes = [OTHER_DISEASE, UNSUPPORTED, NOT_A_LEAF, CROP_MISMATCH]
    else:
        crop_line = "Work out which crop it is yourself."
        extra_classes = [OTHER_DISEASE, UNSUPPORTED, NOT_A_LEAF]

    prompt = f"""
You are an expert plant pathologist looking at a photo of a crop leaf or plant. {crop_line}

Do this in order:
1. Describe what you see in "observations".
2. Say which crop it is in "crop_seen" and what is wrong with it (or "healthy") in "diagnosis", using your own knowledge of
   plant diseases, pests and disorders. Do NOT limit yourself to any list at this step: any disease, pest, nutrient
   deficiency or disorder is allowed.
3. Only then set "class". We keep verified treatments for a short list of conditions:
{', '.join(allowed_classes)}
   Use one of these only if your "diagnosis" is that same condition. If it is a different condition, or the photo does not
   clearly fit, answer "{OTHER_DISEASE}" (supported crop, other problem) or "{UNSUPPORTED}" (crop not in the list).
   A close match is not a match. Visible lesions, pests or virus symptoms are never "healthy".

Reference notes for telling look-alikes apart:
- Pick the crop first, then the disease. Capsicum covers bell pepper and chilli.
- Powdery mildew: on capsicum the white growth is mainly on the underside of the leaf with yellow patches on top; on cucumber it is white powder on the top surface.
- Cucumber downy mildew shows angular yellow spots bounded by veins; mosaic virus shows mottling with leaf distortion and no angular spots.
- Capsicum leaf curl and mosaic covers curling, mottling and crinkling; bacterial leaf spot has small water-soaked spots with yellow halos; Cercospora has grey-centred "frog-eye" spots.
- Onion leaves are round and hollow; garlic leaves are flat and solid. Purple blotch shows sunken white flecks with purple centres; Stemphylium shows yellow-orange streaks that become spindle-shaped spots; thrips leave silvery streaks and tiny black dots.
- Apple scab is velvety olive-brown spots (often under the leaf); Marssonina is dark spots with tiny black dots on mature leaves; Alternaria is dark brown spots with a purple edge. Woolly aphid is white cottony colonies on twigs and shoots; mite bronzing is a bronze, dusty leaf surface.
- Crop identity: pea has compound leaves with tendrils; carrot has finely divided fern-like leaves; spinach has smooth, soft, arrow-shaped leaves; mustard has lobed leaves, often with yellow flowers; cabbage forms a firm leafy head; cauliflower has a white or cream curd with leaves around it.
- Mustard Alternaria shows concentric brown rings; white rust shows raised creamy-white blisters; downy mildew shows grey-white patches underneath; powdery mildew is floury white on both sides. Pea powdery mildew is white powder mostly on top; pea rust is orange pustules underneath.
- Cabbage-family black rot is a yellow V-shaped wedge from the leaf edge with black veins; Alternaria is brown spots with rings; downy mildew is yellow patches with grey mould underneath; diamondback moth makes small windows and holes with tiny green larvae; cabbage butterfly caterpillars are larger green larvae with yellow eggs.
- Brinjal shoot_fruit_borer, little_leaf and bacterial_wilt are whole-plant problems (wilting shoots, tiny bunched leaves, sudden wilting).
- Tomato bacterial wilt is sudden wilting of the whole plant or a shoot while the leaves are still green, with no spots; Septoria is many small round spots with dark edges, grey-white centres and tiny black dots on the lower leaves; early blight spots are larger with concentric rings; leaf curl virus curls and yellows the leaves.
- Rice brown spot is oval brown spots with grey centres on leaves; sheath blight is large greenish-grey lesions on the sheath near the water line; bacterial leaf blight is yellow-white stripes from the leaf tip.
- Maize common rust is brick-red powdery pustules on both leaf sides; gray leaf spot is long rectangular grey-tan lesions between veins; turcicum blight is long cigar-shaped grey-green lesions.
- Wheat brown rust is small round orange-brown pustules scattered on leaves; yellow rust is yellow pustules in stripes along the veins; aphids are small green insect colonies on leaves and ears.
- Onion basal rot is leaves yellowing and drying from the tip, with pink then rotting roots and a soft, brown base, sometimes with white mould.
- If the photo is too unclear to separate two classes, use "{UNSUPPORTED}" instead of guessing.

Use "{NOT_A_LEAF}" if the photo does not show a plant.
"observations" is one or two sentences: leaf shape, spot colour and pattern, which side of the leaf, any pests.
"crop_seen" is the crop's common name, e.g. "Tomato".
"diagnosis" is the common name of the disease, pest or disorder with the crop, e.g. "Tomato mosaic virus", or "healthy".
"confidence" is how sure you are of your "class" answer, from 0 to 100.
"""
    # The free-text fields come first so the model names the problem before it is steered to a listed class
    schema = _S(
        type=_T.OBJECT,
        properties={
            "observations": _S(type=_T.STRING),
            "crop_seen": _S(type=_T.STRING),
            "diagnosis": _S(type=_T.STRING),
            "class": _S(type=_T.STRING, enum=list(allowed_classes) + extra_classes),
            "confidence": _S(type=_T.INTEGER),
        },
        property_ordering=["observations", "crop_seen", "diagnosis", "class", "confidence"],
        required=["observations", "crop_seen", "diagnosis", "class", "confidence"],
    )
    result = _generate(api_key, prompt, [image_jpeg], schema, models)
    return {
        "class": result["class"],
        "confidence": _clamp(result.get("confidence"), 0, 100, 50),
        "name": str(result.get("diagnosis") or "").strip(),
    }


def get_initial_diagnosis(
    api_key: str, image_jpeg: bytes, allowed_classes: list[str], crop_name: str | None = None
) -> dict:
    """Classify a leaf photo into one of `allowed_classes`.

    `crop_name` is the crop the farmer says this is; `allowed_classes` should
    then be limited to that crop's classes. Returns {"class", "confidence", "name"}.
    "class" can also be OTHER_DISEASE (supported crop, problem not in the list;
    "name" says what it looks like), UNSUPPORTED, NOT_A_LEAF, or CROP_MISMATCH
    when a crop was given but the photo clearly shows another plant.

    "confidence" combines two things: how many of the requested votes back the
    winning class (independent models vote; two first, a third only when they
    disagree) and how sure those winning models say they are. A lone or split
    vote therefore lowers it, and it is not a rounded 100/67/33. When the votes are not unanimous the result also
    carries "disagreed": True and the runner-up as "alternative".
    On failure it returns {"class": None, "error": str}.
    """
    errors_seen: list[Exception] = []

    def vote(index: int) -> dict | None:
        try:
            return _diagnose_once(api_key, image_jpeg, allowed_classes, crop_name,
                                  MODELS[index:] + MODELS[:index])
        except Exception as e:
            print(f"GEMINI DIAGNOSIS ERROR: {e!r}")
            errors_seen.append(e)
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        votes = [v for v in pool.map(vote, range(VOTES_FIRST_ROUND)) if v]
    requested = VOTES_FIRST_ROUND
    if len({v["class"] for v in votes}) > 1 or len(votes) < VOTES_FIRST_ROUND:
        third = vote(VOTES_FIRST_ROUND)
        requested += 1
        if third:
            votes.append(third)

    if not votes:
        return {"class": None, "error": friendly_error(errors_seen[0])}

    tally: dict[str, list[dict]] = {}
    for v in votes:
        tally.setdefault(v["class"], []).append(v)
    # most votes first; the models' own stated confidence only breaks ties
    ranked = sorted(tally.items(), key=lambda kv: (-len(kv[1]), -max(v["confidence"] for v in kv[1])))
    winner, winner_votes = ranked[0]
    result = {
        "class": winner,
        "confidence": round(
            (len(winner_votes) / requested)
            * sum(v["confidence"] for v in winner_votes) / len(winner_votes)
        ),
        "name": next((v["name"] for v in winner_votes if v["name"]), ""),
    }
    if len(winner_votes) < requested and len(ranked) > 1:
        result["disagreed"] = True
        result["alternative"] = ranked[1][0]
    return result


_ASSESSMENT_SCHEMA = _S(
    type=_T.OBJECT,
    properties={
        "health_score": _S(type=_T.INTEGER),
        "status_label": _S(type=_T.STRING),
        "ai_notes": _S(type=_T.STRING),
        "next_checkin_days": _S(type=_T.INTEGER),
    },
    required=["health_score", "status_label", "ai_notes", "next_checkin_days"],
)


def get_initial_assessment(api_key: str, image_jpeg: bytes, disease_name: str, confidence: float) -> dict:
    """Baseline health assessment for a newly tracked plant."""
    prompt = f"""
You are an expert plant pathologist. This plant was diagnosed with '{disease_name}' (confidence {confidence:.0f}%).
Give a baseline health assessment:
- "health_score": overall plant health from 0 to 100 (100 = perfectly healthy).
- "status_label": a short summary such as "Critical", "Moderate" or "Mild".
- "ai_notes": brief observations about the plant.
- "next_checkin_days": recommended days until the next check-in (2-14).
"""
    try:
        if not image_jpeg:
            raise ValueError("no photo available")
        result = _generate(api_key, prompt, [image_jpeg], _ASSESSMENT_SCHEMA)
        return {
            "health_score": _clamp(result.get("health_score"), 0, 100, 50),
            "status_label": str(result.get("status_label", "Unknown")),
            "ai_notes": str(result.get("ai_notes", "")),
            "next_checkin_days": _clamp(result.get("next_checkin_days"), 2, 14, 3),
        }
    except Exception as e:
        print(f"GEMINI TRACKER ERROR: {e!r}")
        return {
            "health_score": 50,
            "status_label": "Unknown",
            "ai_notes": f"Could not assess the photo: {friendly_error(e)}",
            "next_checkin_days": 3,
        }


_PROGRESS_SCHEMA = _S(
    type=_T.OBJECT,
    properties={
        "health_score": _S(type=_T.INTEGER),
        "status_label": _S(type=_T.STRING, enum=STATUS_LABELS),
        "ai_notes": _S(type=_T.STRING),
        "treatment_adjustments": _S(type=_T.STRING),
        "next_checkin_days": _S(type=_T.INTEGER),
    },
    required=["health_score", "status_label", "ai_notes", "treatment_adjustments", "next_checkin_days"],
)


def analyze_progress(
    api_key: str,
    prev_image_jpeg: bytes | None,
    curr_image_jpeg: bytes,
    disease_name: str,
    prev_score: int,
    treatment_history: str,
) -> dict:
    """Compare the current photo with the previous one and score progress.

    If there is no previous photo, only the current photo is assessed.
    """
    if prev_image_jpeg:
        images = [prev_image_jpeg, curr_image_jpeg]
        photo_text = (
            f"Image 1 is the previous state (health score {prev_score}/100).\n"
            "Image 2 is the current state."
        )
    else:
        images = [curr_image_jpeg]
        photo_text = (
            f"No earlier photo is available; the previous health score was {prev_score}/100.\n"
            "The image shows the current state."
        )

    prompt = f"""
You are an expert plant pathologist. This plant is being treated for '{disease_name}'.
{photo_text}
Most recent treatment advice: {treatment_history or 'the standard treatment plan'}

Give a progress assessment:
- "health_score": CURRENT overall plant health from 0 to 100.
- "status_label": one of {', '.join(STATUS_LABELS)}.
- "ai_notes": what has changed and what you observe.
- "treatment_adjustments": brief, specific advice (e.g. "Continue plan", "Improve drainage").
- "next_checkin_days": days until the next check-in (2-14).
"""
    try:
        if not curr_image_jpeg:
            raise ValueError("no current photo available")
        result = _generate(api_key, prompt, images, _PROGRESS_SCHEMA)
        status = result.get("status_label")
        return {
            "health_score": _clamp(result.get("health_score"), 0, 100, prev_score),
            "status_label": status if status in STATUS_LABELS else "stable",
            "ai_notes": str(result.get("ai_notes", "")),
            "treatment_adjustments": str(result.get("treatment_adjustments", "")),
            "next_checkin_days": _clamp(result.get("next_checkin_days"), 2, 14, 3),
        }
    except Exception as e:
        print(f"GEMINI PROGRESS ERROR: {e!r}")
        return {
            "health_score": prev_score,
            "status_label": "stable",
            "ai_notes": f"Could not compare the photos: {friendly_error(e)}",
            "treatment_adjustments": "Please follow the treatment plan shown on the scan page.",
            "next_checkin_days": 3,
        }
