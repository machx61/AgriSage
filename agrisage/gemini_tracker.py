"""Gemini calls for leaf diagnosis and plant-progress tracking.

Images are passed as JPEG bytes. Responses are constrained with a JSON schema,
so Gemini always returns parseable JSON with the expected keys.
"""

import json
import time
from functools import lru_cache

import httpx
from google import genai
from google.genai import errors, types

from agrisage.disease_map import NOT_A_LEAF, UNSUPPORTED

# Tried in order; when one is overloaded the next one is used.
MODELS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash"]
MODEL = MODELS[0]

STATUS_LABELS = ["improving", "stable", "worsening", "recovered"]

_S = types.Schema
_T = types.Type

REQUEST_TIMEOUT_S = 40   # one request
TOTAL_TIMEOUT_S = 90     # all attempts together, so the app never hangs


@lru_cache(maxsize=4)
def _client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_S * 1000))


class GeminiTimeout(Exception):
    pass


# Free-tier models often answer "503 high demand", "504 deadline exceeded" or
# "429 rate limit"; these are worth retrying on another model.
_RETRY_CODES = {429, 500, 503, 504}


def _generate(api_key: str, prompt: str, images: list[bytes], schema: types.Schema) -> dict:
    parts = [prompt] + [types.Part.from_bytes(data=img, mime_type="image/jpeg") for img in images]
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    deadline = time.monotonic() + TOTAL_TIMEOUT_S
    last_error = None
    for round_no in range(2):
        for model in MODELS:
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


def get_initial_diagnosis(api_key: str, image_jpeg: bytes, allowed_classes: list[str]) -> dict:
    """Classify a leaf photo into one of `allowed_classes`.

    Returns {"class": str, "confidence": int}. "class" can also be
    UNSUPPORTED or NOT_A_LEAF. On failure it returns {"class": None, "error": str}.
    """
    prompt = f"""
You are an expert plant pathologist. Identify the crop and disease in this photo.

Choose "class" from this list only:
{', '.join(allowed_classes)}

Use "{UNSUPPORTED}" if the crop or the disease is not in the list.
Use "{NOT_A_LEAF}" if the photo does not show a plant.
"confidence" is how sure you are, from 0 to 100.
"""
    schema = _S(
        type=_T.OBJECT,
        properties={
            "class": _S(type=_T.STRING, enum=list(allowed_classes) + [UNSUPPORTED, NOT_A_LEAF]),
            "confidence": _S(type=_T.INTEGER),
        },
        required=["class", "confidence"],
    )
    try:
        result = _generate(api_key, prompt, [image_jpeg], schema)
        return {"class": result["class"], "confidence": _clamp(result.get("confidence"), 0, 100, 50)}
    except Exception as e:
        print(f"GEMINI DIAGNOSIS ERROR: {e!r}")
        return {"class": None, "error": friendly_error(e)}


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
