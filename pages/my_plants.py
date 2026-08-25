import streamlit as st
import sqlite3
import datetime
import base64
import json
import io
import pandas as pd
from pathlib import Path
from PIL import Image
from ultralytics import YOLO

APP_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = APP_DIR / 'agrisage_history.db'
MODEL_PATH = APP_DIR / 'best.pt'

st.markdown('## 🌱 My Plants Dashboard')

# Sidebar — navigation
st.sidebar.markdown("### ⚙️ AgriSage")
st.sidebar.page_link("app.py", label="Scan", icon="🔬")
st.sidebar.page_link("pages/my_plants.py", label="My Plants", icon="🌱")

from streamlit_js_eval import streamlit_js_eval
import uuid

if "history_session_id" not in st.session_state:
    st.session_state.history_session_id = None

device_id = streamlit_js_eval(js_expressions="""
    (function() {
        var id = localStorage.getItem('agrisage_device_id');
        if (!id) { id = crypto.randomUUID(); localStorage.setItem('agrisage_device_id', id); }
        return id;
    })()
""", key="device_id_dashboard")

if device_id:
    st.session_state.history_session_id = device_id
elif st.session_state.history_session_id is None:
    st.session_state.history_session_id = uuid.uuid4().hex

if not device_id and not st.session_state.history_session_id:
    st.stop() # Wait for JS to return the ID

device_id = st.session_state.history_session_id

def get_tracked_plants(device_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''SELECT id, plant_name, crop_type, initial_disease, created_date, current_status, current_score, next_checkin_date 
                 FROM tracked_plants WHERE device_id = ? ORDER BY id DESC''', (device_id,))
    plants = c.fetchall()
    conn.close()
    return plants

def get_progress_entries(plant_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''SELECT date, disease_detected, confidence, health_score, status_label, ai_notes, adjusted_treatment, next_checkin_days, photo_b64 
                 FROM progress_entries WHERE plant_id = ? ORDER BY id ASC''', (plant_id,))
    entries = c.fetchall()
    conn.close()
    return entries

def update_plant_status(plant_id, status, score, next_date):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''UPDATE tracked_plants SET current_status=?, current_score=?, next_checkin_date=? WHERE id=?''', 
              (status, score, next_date, plant_id))
    conn.commit()
    conn.close()

def add_progress_entry(plant_id, date, disease, confidence, score, status, notes, treatment, days, photo_b64):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO progress_entries 
                 (plant_id, date, disease_detected, confidence, health_score, status_label, ai_notes, adjusted_treatment, next_checkin_days, photo_b64) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (plant_id, date, disease, confidence, score, status, notes, treatment, days, photo_b64))
    conn.commit()
    conn.close()

def delete_plant(plant_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM progress_entries WHERE plant_id=?", (plant_id,))
    c.execute("DELETE FROM tracked_plants WHERE id=?", (plant_id,))
    conn.commit()
    conn.close()

@st.cache_resource(show_spinner="🧠 Initializing Botanical AI Engine...")
def load_model():
    return YOLO(MODEL_PATH)

@st.cache_data(ttl=3600, show_spinner="📡 Scanning horizon for weather patterns...")
def get_weather_alert(lat, lon):
    if not lat or not lon: return None
    import requests
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum,relative_humidity_2m_max&timezone=auto&forecast_days=3"
        r = requests.get(url, timeout=5).json()
        daily = r.get("daily", {})
        if not daily: return None
        for i in range(3):
            precip = daily.get("precipitation_sum", [0,0,0])[i]
            humidity = daily.get("relative_humidity_2m_max", [0,0,0])[i]
            if precip > 5.0 and humidity > 80:
                return {"day": daily.get("time", ["Today","Tomorrow","Day 3"])[i], "precip": precip, "humidity": humidity}
    except: pass
    return None

plants = get_tracked_plants(device_id)

weather_alert = get_weather_alert(st.session_state.get("user_lat"), st.session_state.get("user_lon"))
if weather_alert:
    susceptible = [p[1] for p in plants if any(risk in p[3].lower() for risk in ["rust", "blight", "mildew", "rot", "scab", "smut"])]
    if susceptible:
        st.error(f"🚨 **High Risk Weather Incoming:** Heavy rain ({weather_alert['precip']}mm) and high humidity ({weather_alert['humidity']}%) forecast for {weather_alert['day']}. Watch these susceptible plants closely: **{', '.join(susceptible)}**.")

today = datetime.date.today()
overdue_plants = []
due_today = []

for p in plants:
    p_id, p_name, p_crop, p_init_disease, p_created, p_status, p_score, p_next_date = p
    if p_next_date:
        next_date_obj = datetime.datetime.strptime(p_next_date, '%Y-%m-%d').date()
        if next_date_obj < today:
            overdue_plants.append(p_name)
        elif next_date_obj == today:
            due_today.append(p_name)

if overdue_plants:
    st.error(f"Overdue for check-in: {', '.join(overdue_plants)}")
if due_today:
    st.warning(f"Due for check-in today: {', '.join(due_today)}")
if not overdue_plants and not due_today and plants:
    st.success('All plants on track!')

if not plants:
    st.info('No plants being tracked yet. Scan a leaf on the main page and click Track This Plant!')
else:
    status_emoji_map = {'improving': '🟢', 'stable': '🟡', 'worsening': '🔴', 'recovered': '✨'}
    
    for p in plants:
        p_id, p_name, p_crop, p_init_disease, p_created, p_status, p_score, p_next_date = p
        emoji = status_emoji_map.get(p_status, '⚪')
        
        with st.expander(f"{p_name} {emoji}"):
            st.progress(p_score / 100.0, text=f"Health Score: {p_score}/100")
            st.caption(f"Created: {p_created} | Next check-in: {p_next_date}")
            
            entries = get_progress_entries(p_id)
            if entries:
                dates = [e[0] for e in entries]
                scores = [e[3] for e in entries]
                
                df = pd.DataFrame({'Health Score': scores}, index=dates)
                st.line_chart(df)
                
                for entry in entries:
                    e_date, e_disease, e_conf, e_score, e_status, e_notes, e_treat, e_days, e_photo = entry
                    st.markdown(f"**{e_date}** - Badge: {e_status} - Score: {e_score}")
                    st.write(e_notes)
                    if e_photo:
                        try:
                            img_data = base64.b64decode(e_photo)
                            st.image(img_data, width=150)
                        except:
                            pass
            
            with st.form(key=f'form_followup_{p_id}', clear_on_submit=True):
                uploaded_file = st.file_uploader('📸 Upload Follow-up Photo', type=['jpg','jpeg','png'], key=f'followup_{p_id}')
                submit_photo = st.form_submit_button("🤖 Analyze Progress")
                
            if submit_photo and uploaded_file is not None:
                gemini_key = st.secrets.get("GEMINI_API_KEY")
                if not gemini_key:
                    st.warning("Please set GEMINI_API_KEY in .streamlit/secrets.toml")
                else:
                    with st.spinner('Analyzing progress...'):
                        img = Image.open(uploaded_file)
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img.thumbnail((256, 256)) # Compress even further to speed up API upload
                        buffered = io.BytesIO()
                        img.save(buffered, format="JPEG", quality=50)
                        current_photo_b64 = base64.b64encode(buffered.getvalue()).decode()
                        
                        prev_photo_b64 = entries[-1][8] if entries and entries[-1][8] else ""
                        previous_score = entries[-1][3] if entries else p_score
                        treatment_history = entries[-1][6] if entries and entries[-1][6] else "{}"
                        
                        # Skip slow YOLO inference on follow-ups since we already know the baseline disease
                        disease_name = p_init_disease
                        confidence = 1.0
                        
                        from gemini_tracker import analyze_progress
                        
                        result = analyze_progress(gemini_key, prev_photo_b64, current_photo_b64, disease_name, previous_score, treatment_history)
                        
                        new_score = result.get('health_score', previous_score)
                        new_status = result.get('status_label', 'stable')
                        new_notes = result.get('ai_notes', '')
                        new_treatment = json.dumps(result.get('adjusted_treatment', {}))
                        new_days = result.get('next_checkin_days', 7)
                        
                        now = datetime.datetime.now()
                        new_date_str = now.strftime('%Y-%m-%d %H:%M:%S')
                        next_date_val = (now + datetime.timedelta(days=new_days)).strftime('%Y-%m-%d')
                        
                        add_progress_entry(p_id, new_date_str, disease_name, confidence, new_score, new_status, new_notes, new_treatment, new_days, current_photo_b64)
                        update_plant_status(p_id, new_status, new_score, next_date_val)
                        
                        st.success(new_notes)
                        st.rerun()
            
            st.markdown("---")
            if st.button("🗑️ Stop Tracking Plant", key=f"del_plant_{p_id}"):
                delete_plant(p_id)
                st.rerun()
