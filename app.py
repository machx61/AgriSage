# app.py
import os
import sqlite3
import streamlit as st
import requests
import datetime
import base64
import hashlib
from pathlib import Path
import tempfile
import uuid
from PIL import Image
from ultralytics import YOLO
from streamlit_js_eval import get_geolocation
from treatments_db import get_treatment_data, THEME_COLORS
from disease_map import DISEASE_DISPLAY_MAP
from diagnosis_utils import reminder_days_from_frequency, select_consensus_prediction

# --- Database Setup for Persistent History ---
APP_DIR = Path(__file__).resolve().parent
DATABASE_PATH = APP_DIR / "agrisage_history.db"
MODEL_PATH = APP_DIR / "best.pt"
INDIA_TIMEZONE = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def init_db():
    """Creates a local database file if it doesn't exist."""
    with sqlite3.connect(DATABASE_PATH, timeout=5) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS scans
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      session_id TEXT,
                      date TEXT,
                      disease TEXT,
                      confidence REAL)''')
        existing_columns = {row[1] for row in c.execute("PRAGMA table_info(scans)")}
        if "session_id" not in existing_columns:
            c.execute("ALTER TABLE scans ADD COLUMN session_id TEXT")
        c.execute("CREATE INDEX IF NOT EXISTS idx_scans_session_id ON scans(session_id)")


def save_scan(session_id, disease_name, confidence):
    """Saves a new scan to the database."""
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with sqlite3.connect(DATABASE_PATH, timeout=5) as conn:
        conn.execute(
            "INSERT INTO scans (session_id, date, disease, confidence) VALUES (?, ?, ?, ?)",
            (session_id, date_str, disease_name, confidence),
        )


def get_past_scans(session_id):
    """Retrieves the last 10 scans from this browser session."""
    with sqlite3.connect(DATABASE_PATH, timeout=5) as conn:
        return conn.execute(
            "SELECT date, disease, confidence FROM scans WHERE session_id = ? ORDER BY id DESC LIMIT 10",
            (session_id,),
        ).fetchall()

# Initialize DB on startup
init_db()

@st.cache_data(ttl=900)
def get_local_weather(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "precipitation"],
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        current = response.json().get("current", {})
        return {
            "temp": current.get("temperature_2m", "N/A"),
            "humidity": current.get("relative_humidity_2m", "N/A"),
            "precip": current.get("precipitation", "N/A")
        }
    except Exception:
        return {"temp": "N/A", "humidity": "N/A", "precip": "N/A"}

# PWA & Mobile Viewport Config
st.set_page_config(
    page_title="Agrisage PWA",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Define your PWA Manifest
manifest = """
{
  "name": "Agrisage Pathology",
  "short_name": "Agrisage",
  "display": "standalone",
  "background_color": "#FCFBF4",
  "theme_color": "#27AE60",
  "start_url": "/",
  "icons": [{
      "src": "https://cdn-icons-png.flaticon.com/512/628/628283.png",
      "sizes": "512x512",
      "type": "image/png"
  }]
}
"""
b64_manifest = base64.b64encode(manifest.encode('utf-8')).decode('utf-8')

# Inject it into the Streamlit DOM
st.markdown(f"""
    <link rel="manifest" href="data:application/manifest+json;base64,{b64_manifest}">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
""", unsafe_allow_html=True)

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        max-width: 600px;
    }
    
    /* Modern iOS-Style Cards */
    .treatment-card {
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        transition: transform 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .treatment-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    
    /* Header with Icon Box */
    .card-header {
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.01em;
    }
    .card-icon {
        background: rgba(255, 255, 255, 0.6);
        padding: 8px 10px;
        border-radius: 12px;
        font-size: 1.3rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    /* Text styling */
    .card-summary {
        font-size: 0.95rem;
        font-weight: 500;
        opacity: 0.85;
        margin-bottom: 16px;
        line-height: 1.5;
    }
    
    /* Glassmorphism Instructions Box */
    .card-instructions {
        font-size: 0.9rem;
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(10px);
        padding: 16px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.8);
        color: #1F2937;
        line-height: 1.5;
    }
    .card-instructions b {
        color: #111827;
        font-weight: 700;
    }
    
    /* Pill Badge for Frequency */
    .freq-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 0, 0, 0.05);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 12px;
        color: #374151;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Load Model
@st.cache_resource
def load_yolo():
    if not MODEL_PATH.is_file():
        st.error("⚠️ `best.pt` not found! Place your 3.2 MB model in this directory.")
        return None
    try:
        return YOLO(MODEL_PATH)
    except Exception as exc:
        st.error(f"⚠️ The disease model could not be loaded: {exc}")
        return None

model = load_yolo()

# App Header
st.markdown("## 🌱 Agrisage Vision")
st.caption("Botanical Plant Pathology Engine")

if "history_session_id" not in st.session_state:
    st.session_state.history_session_id = uuid.uuid4().hex

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
    except (KeyError, TypeError, ValueError):
        st.warning("Location was received but did not contain valid coordinates.")
elif isinstance(browser_location, dict) and "error" in browser_location:
    st.info("Location access is unavailable. Allow location permission to see local weather.")
else:
    st.caption("Allow location access to view weather at your current farm.")

if loc_info:
    weather = get_local_weather(loc_info["lat"], loc_info["lon"])

if loc_info and weather["temp"] != "N/A":
    st.markdown(f"""
    <div style="background-color: #F0FDF4; border: 1px solid #86EFAC; border-radius: 12px; padding: 10px 14px; margin-bottom: 12px;">
        <div style="font-weight: 600; font-size: 0.85rem; color: #166534;">📍 Current Weather</div>
        <div style="font-size: 0.95rem; color: #14532D; margin-top: 2px;">
            🌡️ <b>{weather['temp']}°C</b> &nbsp;|&nbsp; 
            💧 Humidity: <b>{weather['humidity']}%</b> &nbsp;|&nbsp; 
            🌧️ Rain: <b>{weather['precip']} mm</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        if float(weather["humidity"]) >= 80:
            st.warning("⚠️ **High Humidity Advisory:** Elevated risk for fungal blight and rust. Avoid overhead watering.")
    except (TypeError, ValueError):
        pass

# --- Image Input Section ---
images_to_process = []

# Initialize the camera state if it doesn't exist yet
if "camera_active" not in st.session_state:
    st.session_state.camera_active = False

# Gallery Upload (Now accepts multiple files)
gallery_files = st.file_uploader("📂 Upload from gallery:", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
if gallery_files:
    images_to_process.extend(gallery_files)

# Camera Toggle Logic
if not images_to_process:
    st.markdown("<div style='text-align: center; margin: 10px 0;'><b>OR</b></div>", unsafe_allow_html=True)
    
    if not st.session_state.camera_active:
        # Button to turn the camera ON
        if st.button("📸 Open Camera", use_container_width=True):
            st.session_state.camera_active = True
            st.rerun()
    else:
        # Button to turn the camera OFF
        if st.button("❌ Close Camera", use_container_width=True):
            st.session_state.camera_active = False
            st.rerun()
            
        # The actual camera input
        cam_file = st.camera_input("Take a photo of the leaf")
        if cam_file:
            images_to_process.append(cam_file)

with st.expander("🌾 Add Field Notes", expanded=False):
    import requests
    if st.button("📍 Auto-Detect Location & Weather"):
        lat, lon = None, None
        try:
            # Try browser GPS first (works on Android/iOS)
            loc = get_geolocation()
            if loc and loc.get("coords"):
                lat = loc["coords"]["latitude"]
                lon = loc["coords"]["longitude"]
                st.success(f"📡 GPS location detected!")
        except Exception:
            pass
        
        # Fallback to IP-based detection
        if lat is None:
            try:
                ip_info = requests.get("http://ip-api.com/json/", timeout=5).json()
                if ip_info.get("status") == "success":
                    lat, lon = ip_info["lat"], ip_info["lon"]
                    st.info("📡 Approximate location via network (allow GPS in browser for better accuracy)")
            except Exception:
                pass
        
        if lat is not None and lon is not None:
            try:
                r = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m&elevation=nan", timeout=5).json()
                elevation = r.get("elevation", 0)
                current = r.get("current", {})
                if elevation < 900:
                    st.session_state.auto_elev = "Low Hill (<900m)"
                elif elevation <= 1500:
                    st.session_state.auto_elev = "Mid Hill (900–1500m)"
                else:
                    st.session_state.auto_elev = "High Hill (1500–3000m)"
                st.session_state.auto_weather = f"{current.get('temperature_2m', '')}°C, {current.get('relative_humidity_2m', '')}% humidity"
            except Exception as e:
                st.error(f"Weather fetch failed: {e}")
        else:
            st.error("Could not detect location. Please allow location access in your browser settings and try again.")

    elev_opts = ["Mid Hill (900–1500m)", "Low Hill (<900m)", "High Hill (1500–3000m)"]
    elev_index = None
    if 'auto_elev' in st.session_state and st.session_state.auto_elev in elev_opts:
        elev_index = elev_opts.index(st.session_state.auto_elev)

    elevation_zone = st.selectbox("Elevation Zone", elev_opts, index=elev_index, placeholder="Select Elevation Zone...")
    weather_note = st.text_input("Recent Weather", placeholder="e.g. Recent rainfall / high humidity", value=st.session_state.get('auto_weather', ""))
    fertilizer_usage = st.selectbox("Fertilizer Usage", ["Cow Dung/Compost (Organic)", "Urea/Chemical (High Nitrogen)", "Mixed", "None"], index=None, placeholder="Select Fertilizer Usage...")
    fertilizer_note = st.text_input("Fertilizer Notes", placeholder="Any specific local inputs used?", value="")
    watering_pattern = st.selectbox("Field Conditions", ["Rainfed only", "Flat ground (holds water)", "Sloped/Well-drained", "Ridges/Raised beds"], index=None, placeholder="Select Field Conditions...")
    watering_note = st.text_input("Additional Notes", placeholder="Additional field notes", value="")


def create_pdf(disease_name, treatment_info):
    try:
        from fpdf import FPDF
    except ImportError:
        return None

    def safe(text):
        """Strip non-latin characters to avoid FPDF rendering errors."""
        if not text:
            return ""
        return text.encode('latin-1', 'replace').decode('latin-1')

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
        "local_practice": "Local Practices",
        "iks": "Indigenous Knowledge (IKS)",
    }

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

    return pdf.output()

def generate_ics_file(treatment_name, days_until_next_spray):
    """Generate a standards-compliant calendar event for a recurring treatment."""
    event_start = (datetime.datetime.now(INDIA_TIMEZONE) + datetime.timedelta(days=days_until_next_spray)).replace(
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


upload_signature = get_upload_signature(images_to_process) if images_to_process else None
analyze_requested = st.button(
    "🔍 Analyze Leaf Images",
    disabled=not images_to_process or model is None,
    use_container_width=True,
)

if analyze_requested:
    predictions = []
    confidences = []
    with st.spinner(f"Analyzing {len(images_to_process)} leaf image(s)..."):
        for uploaded_file in images_to_process:
            temp_path = None
            try:
                uploaded_file.seek(0)
                with Image.open(uploaded_file) as source_image:
                    image = source_image.convert("RGB")
                st.image(image, caption=f"Analyzed: {uploaded_file.name}", use_container_width=True)

                with tempfile.NamedTemporaryFile(prefix="agrisage_", suffix=".png", delete=False) as temp_file:
                    temp_path = temp_file.name
                    image.save(temp_file, format="PNG")

                results = model(temp_path)
                probs = results[0].probs
                if probs is None:
                    raise ValueError("The loaded model did not return classification probabilities.")
                raw_class = results[0].names[probs.top1]
                predictions.append(raw_class)
                confidences.append(probs.top1conf.item() * 100)
            except Exception as exc:
                st.warning(f"Could not analyze '{uploaded_file.name}': {exc}")
            finally:
                if temp_path:
                    try:
                        os.unlink(temp_path)
                    except FileNotFoundError:
                        pass

    if predictions:
        final_raw_class, final_confidence = select_consensus_prediction(predictions, confidences)
        display_name = DISEASE_DISPLAY_MAP.get(
            final_raw_class, final_raw_class.replace("_", " ").title()
        )
        st.session_state.last_analysis = {
            "upload_signature": upload_signature,
            "raw_class": final_raw_class,
            "confidence": final_confidence,
        }
        try:
            save_scan(st.session_state.history_session_id, display_name, final_confidence)
        except sqlite3.Error as exc:
            st.warning(f"The diagnosis was completed, but its history could not be saved: {exc}")
    else:
        st.error("No image could be analyzed. Please upload a valid leaf photo and try again.")


def reorder_and_highlight_treatments(treatments_list, fertilizer, watering):
    if not treatments_list: return []
    boosted = []
    regular = []
    for t in treatments_list:
        action = t.get('action', '')
        highlight = False
        warning = ''
        
            # Nitrogen logic
        if fertilizer == 'Urea/Chemical (High Nitrogen)' and 'Nitrogen' in action:
            highlight = True
            warning = '🚨 **High Nitrogen Alert:** Your current fertilizer habit may worsen this disease. '
            
        # Watering logic
        if watering == 'Flat ground (holds water)' and 'Ridge' in action:
            highlight = True
            warning = '🚨 **Drainage Alert:** Flat ground retains moisture. Consider ridges. '
            
        if highlight:
            t['_highlight_warning'] = warning
            boosted.append(t)
        else:
            t['_highlight_warning'] = ''
            regular.append(t)
            
    return boosted + regular

def render_treatment_section(title, items, default_theme, fertilizer, watering):
    if not items:
        return
        
    st.markdown(f"#### {title}")
    ordered_items = reorder_and_highlight_treatments(items, fertilizer, watering)
    
    for item in ordered_items:
        theme_name = item.get('theme', default_theme)
        theme = THEME_COLORS.get(theme_name, THEME_COLORS[default_theme])
        freq_html = f'''<div class="freq-badge">⏱️ {item['frequency']}</div>''' if 'frequency' in item else ''
        warning_html = f"<div style='color: #B91C1C; margin-bottom: 8px; font-weight: 600;'>{item['_highlight_warning']}</div>" if item.get('_highlight_warning') else ''
        
        details_html = ''
        if 'details' in item:
            d = item['details']
            details_html = "<details style='margin-top: 12px; cursor: pointer; border-top: 1px solid rgba(0,0,0,0.1); padding-top: 8px;'>"
            details_html += "<summary style='font-weight: 600; outline: none;'>View Details 📖</summary>"
            details_html += f"<div style='margin-top: 8px;'><b>What it does:</b> {d.get('what_it_does', '')}</div>"
            
            if d.get('materials_needed'):
                details_html += "<div style='margin-top: 8px;'><b>Materials Needed:</b><ul>"
                for m in d['materials_needed']: details_html += f"<li>{m}</li>"
                details_html += "</ul></div>"
                
            if d.get('preparation_steps'):
                details_html += "<div style='margin-top: 8px;'><b>Preparation:</b><ol>"
                for step in d['preparation_steps']: details_html += f"<li>{step}</li>"
                details_html += "</ol></div>"
                
            if d.get('application_steps'):
                details_html += "<div style='margin-top: 8px;'><b>Application:</b><ol>"
                for step in d['application_steps']: details_html += f"<li>{step}</li>"
                details_html += "</ol></div>"
                
            if d.get('time_commitment'):
                details_html += f"<div style='margin-top: 8px;'><b>Time Commitment:</b> {d['time_commitment']}</div>"
                
            if d.get('expected_results_timeline'):
                details_html += f"<div style='margin-top: 8px;'><b>Expected Results:</b> {d['expected_results_timeline']}</div>"
                
            if d.get('safety_notes'):
                details_html += "<div style='margin-top: 8px; color: #B91C1C;'><b>Safety Notes:</b><ul>"
                for note in d['safety_notes']: details_html += f"<li>{note}</li>"
                details_html += "</ul></div>"
                
            details_html += "</details>"
            
        html_content = f"""
<div class="treatment-card" style="background-color: {theme['bg']}; border: 1px solid {theme['border']}; color: {theme['text']};">
<div class="card-header">
<span class="card-icon">{item.get('emoji', '🌿')}</span>
{item.get('action', 'Treatment')}
</div>
<div class="card-summary">{warning_html}{item.get('summary', '')}</div>
<div class="card-instructions">
<b>How to Apply:</b> {item.get('how', '')}
<br>{freq_html}
{details_html}
</div>
</div>
"""
        st.markdown(html_content, unsafe_allow_html=True)
        
        if 'frequency' in item:
            reminder_days = reminder_days_from_frequency(item['frequency'])
            if reminder_days is not None:
                # Add uuid to prevent duplicate keys
                import uuid
                ics_data = generate_ics_file(item['action'], reminder_days)
                st.download_button(
                    label=f"📅 Add {item['action']} Reminder to Calendar",
                    data=ics_data,
                    file_name=f"{item['action'].replace(' ', '_')}_reminder.ics",
                    mime="text/calendar",
                    use_container_width=True,
                    key=f"btn_{uuid.uuid4().hex[:8]}"
                )

analysis = st.session_state.get("last_analysis")
if analysis and (analysis.get("upload_signature") == upload_signature or analysis.get("from_history")):
    final_raw_class = analysis["raw_class"]
    final_confidence = analysis["confidence"]
    display_name = DISEASE_DISPLAY_MAP.get(final_raw_class, final_raw_class.replace("_", " ").title())
    treatment_info = get_treatment_data(final_raw_class)
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 🔬 Diagnosis: **{display_name}**")
        st.progress(
            max(0, min(100, round(final_confidence))),
            text=f"Consensus AI Confidence: {final_confidence:.1f}%",
        )
    with col2:
        pdf_bytes = create_pdf(display_name, treatment_info)
        if pdf_bytes:
            st.download_button("📄 Download PDF", data=bytes(pdf_bytes), file_name=f"{display_name.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)

    fert = fertilizer_usage if 'fertilizer_usage' in locals() else ''
    water = watering_pattern if 'watering_pattern' in locals() else ''
    
    render_treatment_section("🌿 Botanical Solutions", treatment_info.get("botanical", []), "pastel_green", fert, water)
    render_treatment_section("✨ Biological Solutions", treatment_info.get("biological", []), "mint_green", fert, water)
    render_treatment_section("🌾 Cultural Practices & Garden Care", treatment_info.get("cultural", []), "soft_yellow", fert, water)
    render_treatment_section("👩‍🌾 Local Practices", treatment_info.get("local_practice", []), "peach", fert, water)
    render_treatment_section("📜 Indigenous Knowledge (IKS)", treatment_info.get("iks", []), "lavender", fert, water)

# --- Display Persistent History ---
st.markdown("---")
with st.expander("📂 View Past Scans (Saved)"):
    past_scans = get_past_scans(st.session_state.history_session_id)
    if not past_scans:
        st.write("No previous scans found in this browser session.")
    else:
        reverse_map = {v: k for k, v in DISEASE_DISPLAY_MAP.items()}
        for idx, scan in enumerate(past_scans):
            date, disease, confidence = scan
            if st.button(f"🗓️ {date} — {disease} *(Conf: {confidence:.1f}%)*", key=f"hist_{idx}"):
                raw_class = reverse_map.get(disease, disease.lower().replace(" ", "_"))
                st.session_state.last_analysis = {
                    "upload_signature": None,
                    "raw_class": raw_class,
                    "confidence": confidence,
                    "from_history": True
                }
                st.rerun()
