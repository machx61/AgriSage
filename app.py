# app.py
import datetime
import hashlib
import sqlite3
import uuid
from concurrent.futures import ThreadPoolExecutor

import requests
import streamlit as st
from streamlit_js_eval import get_geolocation

from agrisage import db, ui
from agrisage.db import now_ist
from agrisage.treatments_db import DEFAULT_TREATMENT, get_treatment_data, THEME_COLORS
from agrisage.disease_map import DISEASE_DISPLAY_MAP, NOT_A_LEAF, UNSUPPORTED, display_name
from agrisage.diagnosis_utils import reminder_days_from_frequency, select_consensus_prediction
from agrisage.gemini_tracker import analyze_progress, get_initial_assessment, get_initial_diagnosis
from agrisage.images import make_jpeg
from agrisage.session import get_device_id

db.init_db()


@st.cache_data(ttl=900)
def get_local_weather(lat: float, lon: float):
    """Current weather and elevation for a location, or None if unavailable."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "precipitation"],
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        return {
            "temp": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "precip": current.get("precipitation"),
            "elevation": data.get("elevation"),
        }
    except (requests.RequestException, ValueError):
        return None


ui.setup_page("AgriSage")

try:
    gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")
except FileNotFoundError:
    gemini_api_key = ""

ui.header("scan")
device_id = get_device_id("device_id")

if not gemini_api_key:
    st.error("Diagnosis is unavailable right now. Please try again later.")

# This browser component asks the visitor for permission and returns their device's
# GPS/network coordinates. Streamlit itself only runs on the server, so it cannot
# obtain a visitor's location without a browser component.
browser_location = get_geolocation()
loc_info = None
if isinstance(browser_location, dict) and "coords" in browser_location:
    coordinates = browser_location["coords"]
    try:
        loc_info = {
            "lat": float(coordinates["latitude"]),
            "lon": float(coordinates["longitude"]),
        }
        # Shared with the My Plants page for weather alerts
        st.session_state.user_lat = loc_info["lat"]
        st.session_state.user_lon = loc_info["lon"]
    except (KeyError, TypeError, ValueError):
        pass

weather = get_local_weather(loc_info["lat"], loc_info["lon"]) if loc_info else None
st.markdown(ui.weather_chips(weather, located=loc_info is not None), unsafe_allow_html=True)

# --- Image Input Section ---
images_to_process = []

if "camera_active" not in st.session_state:
    st.session_state.camera_active = False

with st.container(key="card_scan"):
    ui.section("Scan a leaf", "Take a close, sharp photo of one leaf in daylight.")

    gallery_files = st.file_uploader(
        "Upload leaf photos", type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True, label_visibility="collapsed",
    )
    if gallery_files:
        images_to_process.extend(gallery_files)

    if not images_to_process:
        if not st.session_state.camera_active:
            if st.button("📸 Use camera instead", use_container_width=True):
                st.session_state.camera_active = True
                st.rerun()
        else:
            cam_file = st.camera_input("Take a photo of the leaf", label_visibility="collapsed")
            if cam_file:
                images_to_process.append(cam_file)
            if st.button("✕ Close camera", use_container_width=True):
                st.session_state.camera_active = False
                st.rerun()


def elevation_zone_for(elevation):
    if elevation is None:
        return None
    if elevation < 900:
        return "Low Hill (<900m)"
    if elevation <= 1500:
        return "Mid Hill (900–1500m)"
    return "High Hill (1500–3000m)"


with st.expander("🌾 Field notes (optional) — tailor the advice to your farm", expanded=False):
    # Pre-fill from the browser's GPS location when it is available
    auto_elev = elevation_zone_for(weather["elevation"]) if weather else None
    auto_weather = f"{weather['temp']}°C, {weather['humidity']}% humidity" if weather and weather["temp"] is not None else ""
    if weather:
        st.caption("📡 Elevation and weather were filled in from your location.")

    elev_opts = ["Mid Hill (900–1500m)", "Low Hill (<900m)", "High Hill (1500–3000m)"]
    elev_index = elev_opts.index(auto_elev) if auto_elev in elev_opts else None

    elevation_zone = st.selectbox("Elevation Zone", elev_opts, index=elev_index, placeholder="Select Elevation Zone...")
    weather_note = st.text_input("Recent Weather", placeholder="e.g. Recent rainfall / high humidity", value=auto_weather)
    fertilizer_usage = st.selectbox("Fertilizer Usage", ["Cow Dung/Compost (Organic)", "Urea/Chemical (High Nitrogen)", "Mixed", "None"], index=None, placeholder="Select Fertilizer Usage...")
    fertilizer_note = st.text_input("Fertilizer Notes", placeholder="Any specific local inputs used?", value="")
    watering_pattern = st.selectbox("Field Conditions", ["Rainfed only", "Flat ground (holds water)", "Sloped/Well-drained", "Ridges/Raised beds"], index=None, placeholder="Select Field Conditions...")
    watering_note = st.text_input("Additional Notes", placeholder="Additional field notes", value="")


@st.cache_data
def create_pdf(raw_class):
    try:
        from fpdf import FPDF
    except ImportError:
        return None

    def safe(text):
        """Strip non-latin characters to avoid FPDF rendering errors."""
        if not text:
            return ""
        return text.encode('latin-1', 'replace').decode('latin-1')

    disease_name = display_name(raw_class)
    treatment_info = get_treatment_data(raw_class)

    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, safe(f"AgriSage: {disease_name}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, safe("IKS-based Treatment Plan (Himachal Pradesh)"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    category_labels = {
        "botanical": "Botanical Solutions",
        "biological": "Biological Solutions",
        "cultural": "Cultural Practices & Garden Care",
        "iks": "Indigenous Knowledge (IKS)",
    }

    # Merge local_practice into cultural for PDF
    if "local_practice" in treatment_info:
        combined_cultural = treatment_info.get("cultural", []) + treatment_info.get("local_practice", [])
        treatment_info = dict(treatment_info)  # shallow copy
        treatment_info["cultural"] = combined_cultural

    for cat, label in category_labels.items():
        items = treatment_info.get(cat, [])
        valid_items = [i for i in items if i.get('status') != 'gap_identified' and i.get('action') != 'IKS Research Gap Identified']
        if not valid_items:
            continue

        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_fill_color(235, 245, 235)
        pdf.cell(0, 8, safe(f"  {label}"), new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.ln(2)

        for item in valid_items:
            action  = safe(item.get("action", ""))
            summary = safe(item.get("summary", ""))
            how     = safe(item.get("how", ""))
            freq    = safe(item.get("frequency", ""))

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, f"  {action}", new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "", 10)
            if summary:
                pdf.set_x(14)
                pdf.multi_cell(w=186, h=5, text=f"  {summary}", new_x="LMARGIN", new_y="NEXT")
            if how:
                pdf.set_x(14)
                pdf.multi_cell(w=186, h=5, text=f"  How: {how}", new_x="LMARGIN", new_y="NEXT")
            if freq:
                pdf.set_font("Helvetica", "I", 9)
                pdf.cell(0, 5, f"    Frequency: {freq}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

    return bytes(pdf.output())


def generate_ics_file(treatment_name, days_until_next_spray):
    """Generate a standards-compliant calendar event for a recurring treatment."""
    event_start = (now_ist() + datetime.timedelta(days=days_until_next_spray)).replace(
        hour=9, minute=0, second=0, microsecond=0
    )
    event_end = event_start + datetime.timedelta(minutes=30)
    escaped_treatment = treatment_name.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Agrisage//Treatment Reminder//EN
BEGIN:VEVENT
UID:{uuid.uuid4()}@agrisage
DTSTAMP:{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:🌿 Agrisage: Apply {escaped_treatment}
DTSTART;TZID=Asia/Kolkata:{event_start.strftime('%Y%m%dT%H%M%S')}
DTEND;TZID=Asia/Kolkata:{event_end.strftime('%Y%m%dT%H%M%S')}
DESCRIPTION:Time to reapply the treatment for your crop as diagnosed by Agrisage.
END:VEVENT
END:VCALENDAR"""
    return ics_content

def get_upload_signature(files):
    """Return a stable identifier for the images currently in the uploader."""
    digest = hashlib.sha256()
    for uploaded_file in files:
        digest.update(uploaded_file.name.encode("utf-8", errors="replace"))
        digest.update(uploaded_file.getvalue())
    return digest.hexdigest()


def diagnose_image(name, image_bytes, allowed_classes):
    """Resize one photo and ask Gemini for a diagnosis. Runs in a worker thread,
    so it must not call any st.* functions."""
    try:
        jpeg = make_jpeg(image_bytes, 800)
    except Exception as exc:
        return name, None, {"class": None, "error": f"not a readable image ({exc})"}
    return name, jpeg, get_initial_diagnosis(gemini_api_key, jpeg, allowed_classes)


upload_signature = get_upload_signature(images_to_process) if images_to_process else None
photo_count = len(images_to_process)
analyze_requested = st.button(
    f"🔍 Diagnose {photo_count} photo{'s' if photo_count != 1 else ''}" if photo_count else "🔍 Diagnose leaf",
    type="primary",
    disabled=not images_to_process or not gemini_api_key,
    use_container_width=True,
)

if analyze_requested:
    predictions = []
    confidences = []
    tracking_photo = None
    allowed_classes = list(DISEASE_DISPLAY_MAP.keys())
    with st.spinner("🔬 Examining your leaf…"):
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(
                lambda f: diagnose_image(f.name, f.getvalue(), allowed_classes),
                images_to_process,
            ))

    for name, jpeg, result in results:
        raw_class = result.get("class")
        if raw_class is None:
            st.error(f"⚠️ Could not analyze '{name}': {result.get('error', 'unknown error')}")
        elif raw_class == NOT_A_LEAF:
            st.warning(f"🍃 '{name}' doesn't look like a plant. Please take a clear photo of a leaf.")
        elif raw_class == UNSUPPORTED:
            st.warning(f"🌾 We couldn't recognise the leaf in '{name}'. Try a closer, clearer photo.")
        else:
            predictions.append(raw_class)
            confidences.append(float(result["confidence"]))
            if tracking_photo is None:
                tracking_photo = make_jpeg(jpeg, 400, quality=60)

    if predictions:
        final_raw_class, final_confidence = select_consensus_prediction(predictions, confidences)
        st.session_state.last_analysis = {
            "upload_signature": upload_signature,
            "raw_class": final_raw_class,
            "confidence": final_confidence,
            "photo": tracking_photo,
            "photo_count": len(predictions),
        }
        try:
            db.save_scan(device_id, final_raw_class, display_name(final_raw_class), final_confidence)
        except sqlite3.Error as exc:
            st.warning(f"The diagnosis was completed, but its history could not be saved: {exc}")
    else:
        st.session_state.pop("last_analysis", None)
        st.error("No image could be diagnosed. Please try a clear, close photo of a single leaf.")


def reorder_and_highlight_treatments(treatments_list, fertilizer, watering):
    if not treatments_list: return []
    boosted = []
    regular = []
    for t in treatments_list:
        action = t.get('action', '')
        warning = ''

        # Nitrogen logic
        if fertilizer == 'Urea/Chemical (High Nitrogen)' and 'Nitrogen' in action:
            warning = '🚨 <b>High Nitrogen Alert:</b> Your current fertilizer habit may worsen this disease.'

        # Watering logic
        if watering == 'Flat ground (holds water)' and 'Ridge' in action:
            warning = '🚨 <b>Drainage Alert:</b> Flat ground retains moisture. Consider ridges.'

        t = {**t, '_highlight_warning': warning}
        (boosted if warning else regular).append(t)

    return boosted + regular


TREATMENT_CATEGORIES = [  # (key, tab label, default card theme)
    ("botanical", "🌿 Botanical", "pastel_green"),
    ("biological", "✨ Biological", "mint_green"),
    ("cultural", "🌾 Cultural", "soft_yellow"),
    ("iks", "📜 Traditional", "lavender"),
]


def usable_items(items):
    """Drop empty or placeholder entries."""
    return [i for i in items if i.get('action') and i.get('action') != 'IKS Research Gap Identified' and (i.get('how') or i.get('summary'))]


def render_treatments(treatment_info, fertilizer, watering):
    by_category = {
        "botanical": treatment_info.get("botanical", []),
        "biological": treatment_info.get("biological", []),
        # local_practice entries are shown together with cultural ones
        "cultural": treatment_info.get("cultural", []) + treatment_info.get("local_practice", []),
        "iks": treatment_info.get("iks", []),
    }
    categories = [(key, label, theme, usable_items(by_category[key]))
                  for key, label, theme in TREATMENT_CATEGORIES]
    categories = [c for c in categories if c[3]]
    if not categories:
        st.info("No specific remedies are recorded for this result yet.")
        return

    tabs = st.tabs([f"{label} · {len(items)}" for _, label, _, items in categories])
    for tab, (section_key, _, default_theme, items) in zip(tabs, categories):
        with tab:
            for idx, item in enumerate(reorder_and_highlight_treatments(items, fertilizer, watering)):
                theme = THEME_COLORS.get(item.get('theme', default_theme), THEME_COLORS[default_theme])
                st.markdown(ui.treatment_card(item, theme), unsafe_allow_html=True)

                reminder_days = reminder_days_from_frequency(item['frequency']) if item.get('frequency') else None
                if reminder_days is not None:
                    st.download_button(
                        label=f"📅 Remind me in {reminder_days} days",
                        data=generate_ics_file(item['action'], reminder_days),
                        file_name=f"{item['action'].replace(' ', '_')}_reminder.ics",
                        mime="text/calendar",
                        use_container_width=True,
                        key=f"ics_{section_key}_{idx}"
                    )


analysis = st.session_state.get("last_analysis")
if analysis and (analysis.get("upload_signature") == upload_signature or analysis.get("from_history")):
    final_raw_class = analysis["raw_class"]
    final_confidence = analysis["confidence"]
    disease_label = display_name(final_raw_class)
    treatment_info = get_treatment_data(final_raw_class)
    photo = analysis.get("photo")
    healthy = final_raw_class.endswith("_healthy")

    crop, _, condition = disease_label.partition(" - ")
    subtitle_parts = [crop]
    if treatment_info is not DEFAULT_TREATMENT and not healthy and treatment_info.get("name") not in (None, condition):
        subtitle_parts.append(treatment_info["name"])
    if analysis.get("photo_count", 1) > 1:
        subtitle_parts.append(f"agreed across {analysis['photo_count']} photos")
    if analysis.get("from_history"):
        subtitle_parts.append("from your scan history")

    st.markdown(ui.diagnosis_card(
        title=condition or disease_label,
        subtitle=" · ".join(subtitle_parts),
        confidence=final_confidence,
        healthy=healthy,
        photo=photo,
        crop_emoji=ui.CROP_EMOJI.get(final_raw_class.split("_")[0], "🌿"),
    ), unsafe_allow_html=True)

    pdf_bytes = create_pdf(final_raw_class)
    if pdf_bytes:
        st.download_button("📄 Save treatment plan (PDF)", data=pdf_bytes, file_name=f"{disease_label.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)

    if healthy:
        ui.section("Keep it healthy", "Simple habits and tonics to prevent disease.")
    else:
        ui.section("Natural treatment plan", "Tap a category. Remedies matching your field notes are shown first.")
    render_treatments(treatment_info, fertilizer_usage, watering_pattern)

    # --- Plant Tracking ---
    existing_plants = db.get_tracked_plants(device_id)

    with st.container(key="card_track"):
        ui.section("Track this plant", "Get a health score, progress notes and check-in reminders.")
        track_tab, link_tab = st.tabs(["🆕 New plant", "📎 Existing plant"])

        with track_tab:
            if not gemini_api_key:
                st.info("Plant tracking is unavailable right now.")
            elif not photo:
                st.info("📸 Scan a new photo of this plant to start tracking it.")
            else:
                plant_name = st.text_input("Give this plant a name", placeholder="e.g. Backyard Tomato", key="new_plant_name")
                if st.button("🌱 Start tracking", type="primary", use_container_width=True):
                    if not plant_name or not plant_name.strip():
                        st.warning("Please enter a name for your plant.")
                    else:
                        with st.spinner("🔬 Assessing plant health…"):
                            assessment = get_initial_assessment(gemini_api_key, photo, disease_label, final_confidence)
                        next_date = db.add_plant(
                            device_id, plant_name.strip(), final_raw_class, disease_label,
                            final_confidence, assessment, photo,
                        )
                        st.success(f"✅ **{plant_name.strip()}** is being tracked! Health score {assessment['health_score']}/100 · next check-in {next_date}.")

        with link_tab:
            if not existing_plants:
                st.caption("No tracked plants yet. Start one in the New plant tab.")
            elif not gemini_api_key:
                st.info("Plant tracking is unavailable right now.")
            elif not photo:
                st.info("📸 Scan a new photo of this plant to add a check-in.")
            else:
                plant_options = {f"{p[1]} (#{p[0]})": p[0] for p in existing_plants}
                selected = st.selectbox("Add this scan as a check-in for:", list(plant_options.keys()), index=None, placeholder="Select a plant...", key="link_plant_select")
                if selected and st.button("📎 Add check-in", type="primary", use_container_width=True):
                    plant_id = plant_options[selected]
                    prev = db.get_latest_entry(plant_id)

                    with st.spinner("🔬 Comparing with the last photo…"):
                        result = analyze_progress(
                            gemini_api_key,
                            prev["photo"] if prev else None,
                            photo,
                            disease_label,
                            prev["health_score"] if prev else 50,
                            prev["adjusted_treatment"] if prev else "",
                        )

                    next_date = db.add_checkin(plant_id, disease_label, final_confidence, result, photo)
                    status_emoji = {"improving": "🟢", "stable": "🟡", "worsening": "🔴", "recovered": "✨"}.get(result["status_label"], "🟡")
                    st.success(f"{status_emoji} Check-in saved! Health {result['health_score']}/100 · next check-in {next_date}.")

# --- Display Persistent History ---
with st.expander("🕘 Recent scans"):
    past_scans = db.get_past_scans(device_id)
    if not past_scans:
        st.caption("Your scans will appear here.")
    else:
        # Older scans were saved without raw_class; recover it from the display name
        reverse_map = {v: k for k, v in DISEASE_DISPLAY_MAP.items()}
        with st.container(key="history"):
            for idx, (date, disease, confidence, raw_class) in enumerate(past_scans):
                if st.button(f"{disease}  ·  {date}  ·  {confidence:.0f}%", key=f"hist_{idx}", use_container_width=True):
                    st.session_state.last_analysis = {
                        "upload_signature": None,
                        "raw_class": raw_class or reverse_map.get(disease, disease.lower().replace(" ", "_")),
                        "confidence": confidence,
                        "photo": None,
                        "from_history": True,
                    }
                    st.rerun()
