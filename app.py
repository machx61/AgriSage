# app.py
import os
import sqlite3
import streamlit as st
import requests
import datetime
import base64
from PIL import Image
from ultralytics import YOLO
from treatments_db import get_treatment_data, THEME_COLORS
from disease_map import DISEASE_DISPLAY_MAP

# --- Database Setup for Persistent History ---
def init_db():
    """Creates a local database file if it doesn't exist."""
    conn = sqlite3.connect("agrisage_history.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scans
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  disease TEXT,
                  confidence REAL)''')
    conn.commit()
    conn.close()

def save_scan(disease_name, confidence):
    """Saves a new scan to the database."""
    conn = sqlite3.connect("agrisage_history.db")
    c = conn.cursor()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO scans (date, disease, confidence) VALUES (?, ?, ?)", 
              (date_str, disease_name, confidence))
    conn.commit()
    conn.close()

def get_past_scans():
    """Retrieves the last 10 scans."""
    conn = sqlite3.connect("agrisage_history.db")
    c = conn.cursor()
    c.execute("SELECT date, disease, confidence FROM scans ORDER BY id DESC LIMIT 10")
    data = c.fetchall()
    conn.close()
    return data

# Initialize DB on startup
init_db()

# Weather and Location config
def get_current_location_coordinates():
    try:
        res = requests.get("https://ipapi.co/json/", timeout=4)
        if res.status_code == 200:
            data = res.json()
            return {
                "lat": float(data.get("latitude")),
                "lon": float(data.get("longitude")),
                "city": data.get("city", "Local Area")
            }
    except Exception:
        pass
    return {"lat": 31.5960, "lon": 77.3520, "city": "Himachal Pradesh"}

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
    model_path = "best.pt"
    if not os.path.exists(model_path):
        st.error("⚠️ `best.pt` not found! Place your 3.2 MB model in this directory.")
        return None
    return YOLO(model_path)

model = load_yolo()

# App Header
st.markdown("## 🌱 Agrisage Vision")
st.caption("Botanical Plant Pathology Engine")

# Live Weather Widget
loc_info = get_current_location_coordinates()
weather = get_local_weather(loc_info["lat"], loc_info["lon"])

if weather["temp"] != "N/A":
    st.markdown(f"""
    <div style="background-color: #F0FDF4; border: 1px solid #86EFAC; border-radius: 12px; padding: 10px 14px; margin-bottom: 12px;">
        <div style="font-weight: 600; font-size: 0.85rem; color: #166534;">📍 {loc_info['city']} Live Weather</div>
        <div style="font-size: 0.95rem; color: #14532D; margin-top: 2px;">
            🌡️ <b>{weather['temp']}°C</b> &nbsp;|&nbsp; 
            💧 Humidity: <b>{weather['humidity']}%</b> &nbsp;|&nbsp; 
            🌧️ Rain: <b>{weather['precip']} mm</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if weather["humidity"] != "N/A" and float(weather["humidity"]) >= 80:
        st.warning("⚠️ **High Humidity Advisory:** Elevated risk for fungal blight and rust. Avoid overhead watering.")

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

with st.expander("🌾 Add Field Notes (Optional)", expanded=False):
    elevation_zone = st.selectbox("Elevation Zone", ["Mid Hill (900–1500m)", "Low Hill (<900m)", "High Hill (1500–3000m)"])
    weather_note = st.text_input("Recent Weather", "Recent rainfall / high humidity")

# Helper function defined BEFORE inference
def generate_ics_file(treatment_name, days_until_next_spray):
    """Generates a raw .ics file string for calendar imports."""
    event_date = datetime.datetime.now() + datetime.timedelta(days=days_until_next_spray)
    date_str = event_date.strftime("%Y%m%dT090000") # Set for 9:00 AM
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:🌿 Agrisage: Apply {treatment_name}
DTSTART:{date_str}
DTEND:{date_str}
DESCRIPTION:Time to reapply the treatment for your crop as diagnosed by Agrisage.
END:VEVENT
END:VCALENDAR"""
    return ics_content

# --- Multi-Leaf Prediction & Diagnosis ---
if images_to_process and model:
    st.markdown("---")
    st.write(f"🔍 Analyzing {len(images_to_process)} leaf image(s)...")

    predictions = []
    confidences = []

    # Loop through batch
    for file in images_to_process:
        img = Image.open(file)
        st.image(img, caption=f"Analyzed: {file.name}", use_container_width=True)
        temp_path = f"temp_{file.name}"
        img.convert("RGB").save(temp_path)

        # Run YOLO model
        results = model(temp_path)
        probs = results[0].probs
        top_idx = probs.top1
        raw_class = results[0].names[top_idx]
        conf = probs.top1conf.item() * 100

        predictions.append(raw_class)
        confidences.append(conf)

        if os.path.exists(temp_path):
            os.remove(temp_path) # Clean up temp file

    # Aggregate Results
    final_raw_class = max(set(predictions), key=predictions.count)
    avg_conf = sum(confidences) / len(confidences)

    display_name = DISEASE_DISPLAY_MAP.get(final_raw_class, final_raw_class.replace('_', ' ').title())
    treatment_info = get_treatment_data(final_raw_class)

    # Save to Persistent Database
    save_scan(display_name, avg_conf)

    st.markdown("---")
    # Display the beautiful name from your mapping dictionary
    st.markdown(f"### 🔬 Diagnosis: **{display_name}**")
    st.progress(int(avg_conf), text=f"Aggregate AI Confidence: {avg_conf:.1f}%")

    # Render Biological Treatments
    st.markdown("#### ✨ Botanical & Biological Solutions")
    for item in treatment_info.get("biological", []):
        theme = THEME_COLORS.get(item.get("theme", "mint_green"), THEME_COLORS["mint_green"])
        freq_html = f"""<div class="freq-badge">⏱️ {item['frequency']}</div>""" if "frequency" in item else ""
        
        st.markdown(f"""
        <div class="treatment-card" style="background-color: {theme['bg']}; border: 1px solid {theme['border']}; color: {theme['text']};">
            <div class="card-header">
                <span class="card-icon">{item.get('emoji', '🌿')}</span>
                {item.get('action', 'Treatment')}
            </div>
            <div class="card-summary">{item.get('summary', '')}</div>
            <div class="card-instructions">
                <b>How to Apply:</b> {item.get('how', '')}
                <br>{freq_html}
            </div>
        </div>
        
        """, unsafe_allow_html=True)
        
        if "frequency" in item:
            # Assuming 'item' is the treatment dictionary from your database
            # Just extract a generic number of days for the prototype (e.g., 7 days)
            ics_data = generate_ics_file(item['action'], 7)
            
            st.download_button(
                label=f"📅 Add {item['action']} Reminder to Calendar",
                data=ics_data,
                file_name=f"{item['action'].replace(' ', '_')}_reminder.ics",
                mime="text/calendar",
                use_container_width=True
            )

    # Render Cultural Treatments
    st.markdown("#### 🌾 Cultural Practices & Garden Care")
    for item in treatment_info.get("cultural", []):
        theme = THEME_COLORS.get(item.get("theme", "soft_yellow"), THEME_COLORS["soft_yellow"])
        freq_html = f"""<div class="freq-badge">⏱️ {item['frequency']}</div>""" if "frequency" in item else ""
        
        st.markdown(f"""
        <div class="treatment-card" style="background-color: {theme['bg']}; border: 1px solid {theme['border']}; color: {theme['text']};">
            <div class="card-header">
                <span class="card-icon">{item.get('emoji', '🌱')}</span>
                {item.get('action', 'Action')}
            </div>
            <div class="card-summary">{item.get('summary', '')}</div>
            <div class="card-instructions">
                <b>Action Plan:</b> {item.get('how', '')}
                <br>{freq_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Display Persistent History ---
st.markdown("---")
with st.expander("📂 View Past Scans (Saved)"):
    past_scans = get_past_scans()
    if not past_scans:
        st.write("No previous scans found on this device.")
    else:
        for scan in past_scans:
            date, disease, confidence = scan
            st.markdown(f"**{date}** — {disease} *(Conf: {confidence:.1f}%)*")