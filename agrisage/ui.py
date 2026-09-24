"""Shared look & feel for all pages: page setup, navigation and HTML building blocks."""

import base64
import html

import streamlit as st

CROP_EMOJI = {"corn": "🌽", "okra": "🫛", "potato": "🥔", "rice": "🍚", "tomato": "🍅", "wheat": "🌾"}

STATUS_STYLE = {  # status_label -> (pill tone, text)
    "improving": ("good", "Improving"),
    "recovered": ("star", "Recovered"),
    "stable": ("warn", "Stable"),
    "worsening": ("bad", "Worsening"),
    # Free-text labels from the first assessment
    "critical": ("bad", "Critical"),
    "severe": ("bad", "Severe"),
    "moderate": ("warn", "Moderate"),
    "mild": ("good", "Mild"),
    "healthy": ("good", "Healthy"),
}

_MANIFEST = """
{
  "name": "AgriSage",
  "short_name": "AgriSage",
  "display": "standalone",
  "background_color": "#F7F5EC",
  "theme_color": "#2F6B3F",
  "start_url": "/",
  "icons": [{
      "src": "https://cdn-icons-png.flaticon.com/512/628/628283.png",
      "sizes": "512x512",
      "type": "image/png"
  }]
}
"""

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Average+Sans&display=swap');

:root {
  --ink: #1E2A22; --ink-soft: #5A665E; --paper: #F7F5EC; --card: #FFFFFF; --line: #E6E1D1;
  --forest: #2F6B3F; --leaf: #4C9A5B; --leaf-tint: #E7F2E6;
  --clay: #B5523B; --clay-tint: #F9E9E3; --amber: #A86B12; --amber-tint: #FBF1DC;
  --radius: 18px;
  --shadow: 0 1px 2px rgba(30,42,34,.05), 0 6px 20px rgba(30,42,34,.06);
}

html, body, .stApp, [class*="css"], button, input, textarea, select {
  font-family: 'Average Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
.stApp { background: var(--paper); color: var(--ink); }
.block-container, [data-testid="stMainBlockContainer"] {
  max-width: 640px; padding: 1.25rem 1.25rem 3rem;
}

/* Hide Streamlit chrome: header bar, sidebar, footer, cloud badges */
header[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
footer, #viewerBadge, [data-testid="stHeaderActionElements"], [data-testid="stToolbar"] { display: none !important; }

/* Invisible helpers (style tags, manifest, browser-location iframes) take no space */
[data-testid="stElementContainer"]:has(style), [data-testid="stElementContainer"]:has(link[rel="manifest"]) { display: none; }
[data-testid="stElementContainer"]:has(> iframe[data-testid="stCustomComponentV1"]) {
  position: absolute; width: 0; height: 0; overflow: hidden; margin: 0; pointer-events: none;
}

/* ---------- Brand ---------- */
.brand { display: flex; align-items: center; gap: 12px; margin: 4px 0 14px; }
.brand-mark {
  width: 46px; height: 46px; border-radius: 14px; display: grid; place-items: center; font-size: 24px;
  background: linear-gradient(135deg, #5DAE6B, #2F6B3F); box-shadow: 0 6px 14px rgba(47,107,63,.28);
}
.brand-name { font-size: 1.6rem; font-weight: 700; letter-spacing: -0.01em; color: var(--forest); line-height: 1.05; }
.brand-tag { font-size: .8rem; color: var(--ink-soft); margin-top: 2px; }

/* ---------- Navigation (pill switcher; bottom tab bar on phones) ---------- */
.st-key-nav [data-testid="stHorizontalBlock"] {
  flex-wrap: nowrap !important; gap: 4px !important; align-items: center;
  background: var(--card); border: 1px solid var(--line); border-radius: 999px; padding: 5px; box-shadow: var(--shadow);
}
.st-key-nav [data-testid="stColumn"], .st-key-nav [data-testid="column"] {
  width: auto !important; flex: 1 1 0 !important; min-width: 0 !important;
}
.st-key-nav [data-testid="stMarkdownContainer"] { margin-bottom: 0 !important; }
.st-key-nav [data-testid="stMarkdownContainer"] p { margin: 0; }
.st-key-nav [data-testid="stPageLink"] { margin: 0; }
.nav-active {
  background: var(--forest); color: #fff; border-radius: 999px; text-align: center;
  font-weight: 700; font-size: .95rem; line-height: 22px; padding: 9px 0;
}
.st-key-nav [data-testid="stPageLink-NavLink"] { justify-content: center; border-radius: 999px; padding: 9px 0; margin: 0; line-height: 22px; }
.st-key-nav [data-testid="stPageLink-NavLink"] p { font-weight: 600; color: var(--ink-soft); font-size: .95rem; }
.st-key-nav [data-testid="stPageLink-NavLink"]:hover { background: var(--leaf-tint); }

/* ---------- Generic card containers: st.container(key="card_...") ---------- */
[class*="st-key-card_"] {
  background: var(--card); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 16px; box-shadow: var(--shadow);
}
/* Streamlit gives elements a fixed pixel width measured from the page; fit them to the card instead */
[class*="st-key-card_"] [data-testid="stElementContainer"],
[class*="st-key-card_"] [data-testid="stElementContainer"] > div { width: 100% !important; }
.sec-title { font-size: 1.2rem; font-weight: 700; letter-spacing: -0.01em; color: var(--ink); margin: 0; }
.sec-hint { font-size: .84rem; color: var(--ink-soft); margin: 2px 0 6px; }
.gap { height: 4px; }

/* ---------- Chips ---------- */
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 2px 0 10px; }
.chip {
  display: inline-flex; align-items: center; gap: 6px; background: var(--card); border: 1px solid var(--line);
  border-radius: 999px; padding: 5px 11px; font-size: .82rem; font-weight: 600; color: var(--ink);
}
.chip.soft { background: var(--paper); }
.chip.muted { color: var(--ink-soft); font-weight: 500; }
.chip.warn { background: var(--amber-tint); border-color: #EBD3A0; color: #7A4E0E; }

/* ---------- Streamlit widgets ---------- */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  border-radius: 14px; min-height: 46px; font-weight: 600;
}
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, #4C9A5B, #2F6B3F); border: none; color: #fff;
  box-shadow: 0 6px 16px rgba(47,107,63,.28); min-height: 54px; font-size: 1.05rem;
}
.stButton > button[kind="primary"]:disabled, [data-testid="stBaseButton-primary"]:disabled {
  background: #D9D5C7; box-shadow: none; color: #8A8A80;
}
[data-testid="stFileUploaderDropzone"] {
  border: 2px dashed #BCD6BC; background: #FBFDF8; border-radius: var(--radius); padding: 1.1rem;
}
[data-testid="stExpander"] details {
  border-radius: var(--radius); border: 1px solid var(--line); background: var(--card); box-shadow: var(--shadow);
}
[data-testid="stExpander"] summary p { font-weight: 600; }
[data-testid="stAlert"] { border-radius: 14px; }
[data-testid="stCameraInput"] video, [data-testid="stCameraInput"] img { border-radius: var(--radius); }

.stTabs [data-baseweb="tab-list"] { gap: 6px; overflow-x: auto; scrollbar-width: none; padding-bottom: 2px; }
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
  background: var(--card); border: 1px solid var(--line); border-radius: 999px;
  padding: 6px 14px; height: auto; white-space: nowrap;
}
.stTabs [data-baseweb="tab"] p { font-weight: 600; font-size: .88rem; }
.stTabs [aria-selected="true"] { background: var(--forest); border-color: var(--forest); }
.stTabs [aria-selected="true"] p { color: #fff; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* ---------- Diagnosis card ---------- */
.dx {
  border-radius: 22px; padding: 16px; border: 1px solid var(--line); box-shadow: var(--shadow);
  display: flex; gap: 16px; align-items: center; margin: 6px 0 10px; background: var(--card);
}
.dx.sick { background: linear-gradient(180deg, #FFF6F2, #FFFFFF); border-color: #F0D5CB; }
.dx.healthy { background: linear-gradient(180deg, #F1F9F0, #FFFFFF); border-color: #CFE5CD; }
.dx img, .dx .ph { width: 96px; height: 96px; object-fit: cover; border-radius: 16px; flex-shrink: 0; }
.dx .ph { display: grid; place-items: center; font-size: 2.6rem; background: var(--leaf-tint); }
.dx-body { flex: 1; min-width: 0; }
.dx-kicker { font-size: .7rem; letter-spacing: .09em; text-transform: uppercase; font-weight: 700; }
.dx.sick .dx-kicker { color: var(--clay); }
.dx.healthy .dx-kicker { color: var(--leaf); }
.dx-title { font-size: 1.45rem; font-weight: 700; letter-spacing: -0.01em; line-height: 1.15; color: var(--ink); margin: 2px 0 3px; }
.dx-sub { font-size: .84rem; color: var(--ink-soft); margin-bottom: 10px; }

.meter { height: 8px; background: #ECE7D8; border-radius: 999px; overflow: hidden; }
.meter > span { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, #86C48C, #2F6B3F); }
.meter.bad > span { background: linear-gradient(90deg, #E39A83, #B5523B); }
.meter.warn > span { background: linear-gradient(90deg, #EFC77A, #A86B12); }
.meter-label { display: flex; justify-content: space-between; font-size: .76rem; color: var(--ink-soft); margin-top: 5px; font-weight: 600; }

/* ---------- Treatment cards ---------- */
.tcard {
  background: var(--card); border: 1px solid var(--line); border-left: 5px solid;
  border-radius: var(--radius); padding: 16px; margin: 6px 0 8px; box-shadow: var(--shadow);
}
.tcard-head { display: flex; gap: 12px; align-items: center; margin-bottom: 10px; }
.tcard-icon { width: 44px; height: 44px; border-radius: 12px; display: grid; place-items: center; font-size: 1.4rem; flex-shrink: 0; }
.tcard-title { font-weight: 700; font-size: 1.02rem; color: var(--ink); line-height: 1.25; }
.tcard-freq { font-size: .78rem; color: var(--ink-soft); font-weight: 600; margin-top: 3px; }
.tcard-summary { font-size: .92rem; color: var(--ink-soft); margin: 0 0 10px; line-height: 1.5; }
.tcard-how { border-radius: 12px; padding: 12px 14px; font-size: .9rem; line-height: 1.55; color: var(--ink); }
.tcard-how .lbl { display: block; font-size: .68rem; letter-spacing: .09em; text-transform: uppercase; font-weight: 700; margin-bottom: 4px; }
.tcard-alert { background: var(--clay-tint); color: #8A2E1C; border-radius: 10px; padding: 8px 12px; font-size: .85rem; font-weight: 600; margin-bottom: 10px; }
.tcard details { margin-top: 10px; font-size: .88rem; line-height: 1.5; }
.tcard summary { cursor: pointer; font-weight: 700; color: var(--forest); }
.tcard details ul, .tcard details ol { padding-left: 1.2rem; margin: 4px 0; }

/* ---------- My Plants ---------- */
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 2px 0 12px; }
.stat { background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 12px 8px; text-align: center; box-shadow: var(--shadow); }
.stat b { display: block; font-weight: 700; font-size: 1.7rem; color: var(--ink); line-height: 1.1; }
.stat span { font-size: .74rem; color: var(--ink-soft); font-weight: 600; }
.stat.warn b { color: var(--amber); }
.stat.bad b { color: var(--clay); }

.plant { display: flex; gap: 14px; align-items: center; }
.plant img, .plant .ph { width: 68px; height: 68px; border-radius: 14px; object-fit: cover; flex-shrink: 0; }
.plant .ph { display: grid; place-items: center; font-size: 2rem; background: var(--leaf-tint); }
.plant-body { flex: 1; min-width: 0; }
.plant-top { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.plant-name { font-weight: 700; font-size: 1.05rem; color: var(--ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.plant-sub { font-size: .8rem; color: var(--ink-soft); margin: 2px 0 8px; }
.plant-due { font-size: .76rem; font-weight: 700; margin-top: 6px; color: var(--ink-soft); }
.plant-due.bad { color: var(--clay); }
.plant-due.warn { color: var(--amber); }

.pill { display: inline-block; font-size: .7rem; font-weight: 700; padding: 3px 10px; border-radius: 999px; background: #EEE9DA; color: var(--ink-soft); white-space: nowrap; }
.pill.good { background: var(--leaf-tint); color: #24663A; }
.pill.warn { background: var(--amber-tint); color: #7A4E0E; }
.pill.bad { background: var(--clay-tint); color: #8A2E1C; }
.pill.star { background: #EFE7FA; color: #5B3B8C; }

.tl { display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px dashed var(--line); }
.tl:last-child { border-bottom: none; }
.tl img, .tl .ph { width: 56px; height: 56px; border-radius: 12px; object-fit: cover; flex-shrink: 0; }
.tl .ph { display: grid; place-items: center; background: var(--paper); font-size: 1.4rem; }
.tl-top { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.tl-date { font-size: .78rem; color: var(--ink-soft); font-weight: 600; }
.tl-score { font-size: .78rem; font-weight: 700; color: var(--ink); }
.tl-notes { font-size: .88rem; margin-top: 4px; line-height: 1.5; color: var(--ink); }
.tl-tip { font-size: .82rem; color: var(--forest); margin-top: 4px; font-weight: 600; }

/* ---------- History list ---------- */
.st-key-history .stButton > button {
  justify-content: flex-start; text-align: left; background: var(--paper); border: 1px solid var(--line); min-height: 50px;
}
.st-key-history .stButton > button:hover { border-color: var(--leaf); color: var(--forest); }

/* ---------- Phones ---------- */
@media (max-width: 640px) {
  .block-container, [data-testid="stMainBlockContainer"] { padding: .75rem .9rem 7rem; }
  .st-key-nav { position: fixed; left: 12px; right: 12px; bottom: 14px; z-index: 1000; width: auto !important; }
  .st-key-nav [data-testid="stHorizontalBlock"] { box-shadow: 0 10px 30px rgba(30,42,34,.20); padding: 6px; }
  .nav-active, .st-key-nav [data-testid="stPageLink-NavLink"] { padding-top: 11px; padding-bottom: 11px; }
  .brand { margin-bottom: 10px; }
  .dx { gap: 12px; padding: 14px; }
  .dx img, .dx .ph { width: 78px; height: 78px; }
  .dx-title { font-size: 1.25rem; }
  .tcard { padding: 14px; }
}
</style>
"""


def setup_page(title: str):
    """Page config, shared styles and PWA tags. Call first on every page."""
    st.set_page_config(page_title=title, page_icon="🌱", layout="centered", initial_sidebar_state="collapsed")
    b64_manifest = base64.b64encode(_MANIFEST.encode("utf-8")).decode("utf-8")
    st.markdown(f"""
        <link rel="manifest" href="data:application/manifest+json;base64,{b64_manifest}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="theme-color" content="#F7F5EC">
    """, unsafe_allow_html=True)
    st.markdown(_CSS, unsafe_allow_html=True)


def header(active: str):
    """Brand header plus the Scan / My Plants switcher. `active` is "scan" or "plants"."""
    st.markdown("""
    <div class="brand">
      <div class="brand-mark">🌱</div>
      <div>
        <div class="brand-name">AgriSage</div>
        <div class="brand-tag">Leaf disease scanner · natural remedies for hill farms</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    pages = [("scan", "app.py", "Scan", "🔬"), ("plants", "pages/my_plants.py", "My Plants", "🌱")]
    with st.container(key="nav"):
        for col, (name, page, label, icon) in zip(st.columns(len(pages)), pages):
            with col:
                if name == active:
                    st.markdown(f'<div class="nav-active">{icon} {label}</div>', unsafe_allow_html=True)
                else:
                    st.page_link(page, label=label, icon=icon, use_container_width=True)


def esc(text) -> str:
    return html.escape(str(text)) if text is not None else ""


def img_tag(jpeg: bytes | None, placeholder: str = "🌿") -> str:
    if not jpeg:
        return f'<div class="ph">{placeholder}</div>'
    return f'<img src="data:image/jpeg;base64,{base64.b64encode(jpeg).decode()}" alt="">'


def section(title: str, hint: str | None = None):
    hint_html = f'<div class="sec-hint">{esc(hint)}</div>' if hint else ""
    st.markdown(f'<div class="sec-title">{esc(title)}</div>{hint_html}', unsafe_allow_html=True)


def chips(items: list[str], tone: str = "") -> str:
    return '<div class="chips">' + "".join(f'<span class="chip {tone}">{i}</span>' for i in items) + "</div>"


def meter(value: float, left: str, right: str, tone: str = "") -> str:
    pct = max(0, min(100, round(value)))
    return (f'<div class="meter {tone}"><span style="width:{pct}%"></span></div>'
            f'<div class="meter-label"><span>{esc(left)}</span><span>{esc(right)}</span></div>')


def health_tone(score: int) -> str:
    return "" if score >= 70 else ("warn" if score >= 40 else "bad")


def weather_chips(weather: dict | None, located: bool) -> str:
    if weather and weather.get("temp") is not None:
        items = [f"🌡️ {weather['temp']}°C", f"💧 {weather['humidity']}%", f"🌧️ {weather['precip']} mm"]
        html_out = chips(items)
        if weather.get("humidity") is not None and weather["humidity"] >= 80:
            html_out += chips(["⚠️ High humidity: fungal risk. Avoid overhead watering."], "warn")
        return html_out
    if located:
        return chips(["🌤️ Weather unavailable right now"], "muted")
    return chips(["📍 Allow location to see local weather"], "muted")


def diagnosis_card(title: str, subtitle: str, confidence: float, healthy: bool, photo: bytes | None, crop_emoji: str) -> str:
    kind = "healthy" if healthy else "sick"
    kicker = "✓ Healthy leaf" if healthy else "Disease detected"
    return f"""
    <div class="dx {kind}">
      {img_tag(photo, crop_emoji)}
      <div class="dx-body">
        <div class="dx-kicker">{kicker}</div>
        <div class="dx-title">{esc(title)}</div>
        <div class="dx-sub">{esc(subtitle)}</div>
        {meter(confidence, "Confidence", f"{confidence:.0f}%")}
      </div>
    </div>
    """


def treatment_card(item: dict, theme: dict) -> str:
    freq = f'<div class="tcard-freq">⏱️ {esc(item["frequency"])}</div>' if item.get("frequency") else ""
    alert = f'<div class="tcard-alert">{item["_highlight_warning"]}</div>' if item.get("_highlight_warning") else ""
    summary = f'<p class="tcard-summary">{esc(item["summary"])}</p>' if item.get("summary") else ""
    how = (f'<div class="tcard-how" style="background:{theme["bg"]}"><span class="lbl" style="color:{theme["text"]}">How to apply</span>'
           f'{esc(item["how"])}</div>') if item.get("how") else ""

    details = ""
    d = item.get("details")
    if d:
        parts = []
        if d.get("what_it_does"):
            parts.append(f"<p><b>What it does:</b> {esc(d['what_it_does'])}</p>")
        for key, label, tag in [("materials_needed", "Materials needed", "ul"),
                                ("preparation_steps", "Preparation", "ol"),
                                ("application_steps", "Application", "ol"),
                                ("safety_notes", "⚠️ Safety notes", "ul")]:
            if d.get(key):
                lis = "".join(f"<li>{esc(x)}</li>" for x in d[key])
                parts.append(f"<b>{label}:</b><{tag}>{lis}</{tag}>")
        for key, label in [("time_commitment", "Time needed"), ("expected_results_timeline", "Expected results")]:
            if d.get(key):
                parts.append(f"<p><b>{label}:</b> {esc(d[key])}</p>")
        details = f"<details><summary>Full recipe &amp; steps</summary>{''.join(parts)}</details>"

    # Colours go straight into style attributes: Streamlit strips CSS variables from them
    return f"""
    <div class="tcard" style="border-left-color:{theme['border']}">
      <div class="tcard-head">
        <div class="tcard-icon" style="background:{theme['bg']}">{esc(item.get('emoji', '🌿'))}</div>
        <div><div class="tcard-title">{esc(item.get('action', 'Treatment'))}</div>{freq}</div>
      </div>
      {alert}{summary}{how}{details}
    </div>
    """


def status_pill(status: str | None) -> str:
    tone, text = STATUS_STYLE.get((status or "").lower(), ("", status or "New"))
    return f'<span class="pill {tone}">{esc(text)}</span>'
