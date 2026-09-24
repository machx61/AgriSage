import datetime

import altair as alt
import pandas as pd
import requests
import streamlit as st

from agrisage import db, ui
from agrisage.disease_map import display_name
from agrisage.gemini_tracker import analyze_progress
from agrisage.images import make_jpeg
from agrisage.session import get_device_id

db.init_db()
ui.setup_page("My Plants · AgriSage")
ui.header("plants")

device_id = get_device_id("device_id_dashboard")

RISKY_DISEASE_WORDS = ["rust", "blight", "mildew", "rot", "scab", "smut", "spot"]


@st.cache_data(ttl=3600, show_spinner="📡 Checking the weather forecast...")
def get_weather_alert(lat, lon):
    if lat is None or lon is None:
        return None
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "daily": ["precipitation_sum", "relative_humidity_2m_max"],
                "timezone": "auto", "forecast_days": 3,
            },
            timeout=5,
        ).json()
    except (requests.RequestException, ValueError):
        return None
    daily = r.get("daily", {})
    for day, precip, humidity in zip(daily.get("time", []), daily.get("precipitation_sum", []),
                                     daily.get("relative_humidity_2m_max", [])):
        if precip is not None and humidity is not None and precip > 5.0 and humidity > 80:
            return {"day": day, "precip": precip, "humidity": humidity}
    return None


def due_info(next_date_str, today):
    """(css tone, text) describing when the next check-in is due."""
    if not next_date_str:
        return "", "No check-in scheduled"
    days = (datetime.datetime.strptime(next_date_str, "%Y-%m-%d").date() - today).days
    if days < 0:
        return "bad", f"⏰ Check-in overdue by {-days} day{'s' if days != -1 else ''}"
    if days == 0:
        return "warn", "📸 Check-in due today"
    return "", f"Next check-in in {days} day{'s' if days != 1 else ''}"


plants = db.get_tracked_plants(device_id)
today = db.now_ist().date()

weather_alert = get_weather_alert(st.session_state.get("user_lat"), st.session_state.get("user_lon"))
if weather_alert:
    susceptible = [p[1] for p in plants if any(risk in (p[3] or "").lower() for risk in RISKY_DISEASE_WORDS)]
    if susceptible:
        st.error(f"🌧️ **Risky weather on {weather_alert['day']}:** {weather_alert['precip']} mm rain and {weather_alert['humidity']}% humidity expected. Keep a close eye on **{', '.join(susceptible)}**.")

if not plants:
    with st.container(key="card_empty"):
        ui.section("No plants tracked yet", "Scan a leaf, then tap “Start tracking” under the result to follow its recovery here.")
        st.page_link("app.py", label="Scan a leaf", icon="🔬")
    st.stop()

due_tones = [due_info(p[7], today)[0] for p in plants]
overdue = due_tones.count("bad")
due_today = due_tones.count("warn")
st.markdown(f"""
<div class="stats">
  <div class="stat"><b>{len(plants)}</b><span>Tracked</span></div>
  <div class="stat {'warn' if due_today else ''}"><b>{due_today}</b><span>Due today</span></div>
  <div class="stat {'bad' if overdue else ''}"><b>{overdue}</b><span>Overdue</span></div>
</div>
""", unsafe_allow_html=True)

for p in plants:
    p_id, p_name, p_crop, p_init_disease, p_created, p_status, p_score, p_next_date = p
    disease_label = display_name(p_init_disease)
    entries = db.get_progress_entries(p_id)
    latest_photo = next((e["photo"] for e in reversed(entries) if e["photo"]), None)
    due_tone, due_text = due_info(p_next_date, today)
    score = max(0, min(100, p_score or 0))

    with st.container(key=f"card_plant_{p_id}"):
        st.markdown(f"""
        <div class="plant">
          {ui.img_tag(latest_photo, ui.CROP_EMOJI.get(p_crop, "🌿"))}
          <div class="plant-body">
            <div class="plant-top"><div class="plant-name">{ui.esc(p_name)}</div>{ui.status_pill(p_status)}</div>
            <div class="plant-sub">{ui.esc(disease_label)}</div>
            {ui.meter(score, "Health", f"{score}/100", ui.health_tone(score))}
            <div class="plant-due {due_tone}">{due_text}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"History & check-in ({len(entries)} entr{'y' if len(entries) == 1 else 'ies'})"):
            if len(entries) > 1:
                # Numbered check-ins keep the axis readable on phones; dates are in the timeline below
                df = pd.DataFrame({"Check-in": range(1, len(entries) + 1),
                                   "Health": [e["health_score"] for e in entries]})
                chart = alt.Chart(df).mark_line(point=alt.OverlayMarkDef(color="#2F6B3F", size=70), color="#2F6B3F", strokeWidth=3).encode(
                    x=alt.X("Check-in:O", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Health:Q", scale=alt.Scale(domain=[0, 100])),
                ).properties(height=170)
                st.altair_chart(chart, use_container_width=True)

            timeline = []
            for entry in reversed(entries):
                tip = f'<div class="tl-tip">💡 {ui.esc(entry["adjusted_treatment"])}</div>' if entry["adjusted_treatment"] else ""
                timeline.append(f"""
                <div class="tl">
                  {ui.img_tag(entry["photo"], "📷")}
                  <div>
                    <div class="tl-top"><span class="tl-date">{ui.esc(entry["date"])}</span>{ui.status_pill(entry["status_label"])}<span class="tl-score">{entry["health_score"]}/100</span></div>
                    <div class="tl-notes">{ui.esc(entry["ai_notes"])}</div>
                    {tip}
                  </div>
                </div>""")
            st.markdown("".join(timeline), unsafe_allow_html=True)

            with st.form(key=f'form_followup_{p_id}', clear_on_submit=True):
                uploaded_file = st.file_uploader('📸 New photo of this plant', type=['jpg', 'jpeg', 'png', 'webp'], key=f'followup_{p_id}')
                submit_photo = st.form_submit_button("🔬 Check progress", type="primary", use_container_width=True)

            if submit_photo and uploaded_file is not None:
                try:
                    gemini_key = st.secrets.get("GEMINI_API_KEY")
                except FileNotFoundError:
                    gemini_key = None
                if not gemini_key:
                    st.warning("Progress checks are unavailable right now.")
                else:
                    try:
                        current_photo = make_jpeg(uploaded_file.getvalue(), 400, quality=60)
                    except Exception as exc:
                        st.error(f"Could not read that photo: {exc}")
                        st.stop()

                    prev = entries[-1] if entries else None
                    with st.spinner('🔬 Comparing with the last photo…'):
                        result = analyze_progress(
                            gemini_key,
                            prev["photo"] if prev else None,
                            current_photo,
                            disease_label,
                            prev["health_score"] if prev else p_score,
                            prev["adjusted_treatment"] if prev else "",
                        )
                    # Follow-ups skip re-diagnosis since the baseline disease is already known
                    db.add_checkin(p_id, disease_label, 100.0, result, current_photo)
                    st.rerun()

            with st.popover("🗑️ Stop tracking", use_container_width=True):
                st.write(f"Delete **{p_name}** and all its check-ins? This can't be undone.")
                if st.button("Yes, delete", key=f"del_plant_{p_id}", use_container_width=True):
                    db.delete_plant(p_id)
                    st.rerun()
