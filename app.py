import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

from Dataset.src.predict import predict_dengue_risk

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="DengueGuard AI",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Dot-matrix mosquito (each "#" is a glowing dot, "." is a faint grid dot)
# ----------------------------------------------------------------------------
MOSQUITO = [
    "..........................###....",
    "......................#####......",
    "...................#####.........",
    "................#####............",
    "..........#...####...............",
    ".........#...##..................",
    ".........#..####.................",
    "........#########................",
    "........############.............",
    "......################...........",
    "....##......####.########........",
    "..##........#.#.#....#######.....",
    "##.........#..#..#.......######..",
    "..........#..#....#..........###.",
    ".........#...#.....#.............",
    ".........#..#......#.............",
    ".........#..#.......#............",
    "........#..#........#............",
    "........#..#.........#...........",
    "...........#.........#...........",
]


def mosquito_svg(cell=14, radius=4.2):
    rows, cols = len(MOSQUITO), len(MOSQUITO[0])
    parts = []
    for y, row in enumerate(MOSQUITO):
        for x, ch in enumerate(row):
            cx = x * cell + cell / 2
            cy = y * cell + cell / 2
            if ch == "#":
                delay = (x + y) * 0.09
                parts.append(
                    f'<circle class="md-on" cx="{cx}" cy="{cy}" r="{radius}" '
                    f'style="animation-delay:{delay:.2f}s"/>'
                )
            else:
                parts.append(f'<circle class="md-off" cx="{cx}" cy="{cy}" r="1.5"/>')
    return (
        f'<svg class="mosq" viewBox="0 0 {cols * cell} {rows * cell}" '
        f'xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'
    )


# ----------------------------------------------------------------------------
# Risk configuration (colour appears only as a small accent)
# ----------------------------------------------------------------------------
RISK_LEVELS = {
    "Low": {
        "level": 1,
        "color": "#4ADE80",
        "headline": "Looking good",
        "message": "Conditions are favourable right now. Keep up the great prevention work and stay consistent.",
        "actions": [
            "Continue routine mosquito surveillance.",
            "Keep drains and water containers clean and covered.",
            "Keep community awareness messaging going.",
        ],
    },
    "Medium": {
        "level": 2,
        "color": "#FACC15",
        "headline": "Stay one step ahead",
        "message": "Risk is moderate. A few simple steps now can keep this ward safe.",
        "actions": [
            "Inspect breeding sites such as stagnant water, tyres and pots.",
            "Run a short awareness drive in the ward.",
            "Prepare local clinics for a possible rise in cases.",
        ],
    },
    "High": {
        "level": 3,
        "color": "#FB923C",
        "headline": "Time to act. Early action works",
        "message": "Conditions favour active transmission, but a timely response makes a real difference.",
        "actions": [
            "Start targeted larval source reduction.",
            "Alert nearby clinics and hospitals to expect more patients.",
            "Encourage nets, repellents and early care for fever.",
        ],
    },
    "Critical": {
        "level": 4,
        "color": "#F87171",
        "headline": "Urgent, and manageable together",
        "message": "A significant outbreak is likely without intervention. A coordinated response saves lives.",
        "actions": [
            "Escalate to city health authorities now.",
            "Mobilise emergency vector-control teams in the ward.",
            "Confirm hospital beds, IV fluids and testing capacity.",
        ],
    },
}


def level_bar(level, color):
    segments = "".join(
        f'<div class="seg" style="--i:{i};background:{color if i < level else "rgba(255,255,255,0.10)"}"></div>'
        for i in range(4)
    )
    return f'<div class="level-bar">{segments}</div>'


# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html { scroll-behavior: smooth; }

html, body, [class*="css"], .stApp, p, label, li {
    font-family: 'Inter', sans-serif;
}

/* ---------- Background: black into ash with a soft light ---------- */
.stApp {
    background:
        radial-gradient(900px 500px at 85% -5%, rgba(120,122,128,0.28) 0%, transparent 60%),
        radial-gradient(700px 400px at 0% 100%, rgba(90,92,98,0.18) 0%, transparent 60%),
        linear-gradient(180deg, #08080A 0%, #111214 55%, #1A1B1E 100%);
    background-attachment: fixed;
    color: #F4F4F5;
}

#MainMenu, footer, header[data-testid="stHeader"] {visibility: hidden; height: 0;}
.block-container {padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1150px;}

hr {border-color: rgba(255,255,255,0.08) !important;}
[data-testid="stCaptionContainer"] {color: #8E8E96;}

/* ---------- Motion ---------- */
@keyframes fadeUp {
    from {opacity: 0; transform: translateY(16px);}
    to   {opacity: 1; transform: translateY(0);}
}
@keyframes shine {
    0%, 100% {opacity: 0.45;}
    45% {opacity: 1;}
}
@keyframes floaty {
    0%, 100% {transform: translateY(0);}
    50% {transform: translateY(-8px);}
}
@keyframes sweep {
    0% {transform: translateX(-120%);}
    55%, 100% {transform: translateX(120%);}
}
@keyframes grow {
    from {transform: scaleX(0); opacity: 0;}
    to   {transform: scaleX(1); opacity: 1;}
}
@keyframes pulse {
    0%, 100% {opacity: 1;}
    50% {opacity: 0.3;}
}

.fade {animation: fadeUp .8s cubic-bezier(.2,.8,.2,1) both;}
.fade-2 {animation-delay: .12s;}
.fade-3 {animation-delay: .24s;}

/* ---------- Hero ---------- */
.hero {
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 24px;
    padding: 38px 46px;
    margin-bottom: 30px;
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,0.09);
    background:
        radial-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
        linear-gradient(135deg, #0A0A0C 0%, #17181B 100%);
    background-size: 20px 20px, 100% 100%;
    box-shadow: 0 20px 60px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.06);
}
.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(115deg, transparent 35%, rgba(255,255,255,0.07) 50%, transparent 65%);
    animation: sweep 8s ease-in-out infinite;
    pointer-events: none;
}
.hero-text {position: relative; z-index: 1; max-width: 560px;}
.hero-tag {
    display: inline-flex; align-items: center; gap: 9px;
    font-size: 11.5px; font-weight: 600; letter-spacing: 2px;
    text-transform: uppercase; color: #A1A1AA;
    margin-bottom: 14px;
}
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #fff;
    box-shadow: 0 0 10px rgba(255,255,255,0.9);
    animation: pulse 2s ease-in-out infinite;
}
.hero-title {
    font-size: 44px; font-weight: 800; line-height: 1.1;
    color: #fff; margin: 0 0 12px 0;
    text-shadow: 0 0 30px rgba(255,255,255,0.18);
}
.hero-sub {font-size: 15.5px; color: #A1A1AA; line-height: 1.7; font-weight: 400;}

.mosq-wrap {
    position: relative; z-index: 1;
    width: 330px; max-width: 100%;
    animation: floaty 6s ease-in-out infinite;
}
.mosq {width: 100%; height: auto; filter: drop-shadow(0 0 9px rgba(255,255,255,0.55));}
.md-on {fill: #fff; animation: shine 3.6s ease-in-out infinite;}
.md-off {fill: rgba(255,255,255,0.09);}

/* ---------- Headings ---------- */
.section-title {font-size: 21px; font-weight: 700; color: #fff; margin: 4px 0 2px 0; letter-spacing: -0.2px;}
.section-caption {font-size: 14px; color: #8E8E96; margin-bottom: 16px;}

/* ---------- Legend chips ---------- */
.chip-row {display: flex; gap: 12px; flex-wrap: wrap;}
.chip {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 18px; border-radius: 999px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    font-size: 13.5px; font-weight: 500; color: #E4E4E7;
    transition: all .35s cubic-bezier(.2,.8,.2,1);
}
.chip:hover {
    background: rgba(255,255,255,0.09);
    border-color: rgba(255,255,255,0.25);
    transform: translateY(-2px);
}
.chip-dot {width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 10px currentColor;}

/* ---------- Form ---------- */
[data-testid="stForm"] {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 20px;
    padding: 24px 28px;
    backdrop-filter: blur(8px);
    box-shadow: 0 10px 40px rgba(0,0,0,0.35);
    animation: fadeUp .8s cubic-bezier(.2,.8,.2,1) both;
    transition: border-color .35s ease;
}
[data-testid="stForm"]:hover {border-color: rgba(255,255,255,0.16);}

.stNumberInput label p {font-size: 13px !important; font-weight: 500 !important; color: #C4C4CA;}
div[data-baseweb="input"] {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    background: rgba(255,255,255,0.05) !important;
    transition: all .3s ease;
}
div[data-baseweb="input"]:focus-within {
    border-color: rgba(255,255,255,0.7) !important;
    box-shadow: 0 0 0 4px rgba(255,255,255,0.08), 0 0 20px rgba(255,255,255,0.10);
}
div[data-baseweb="input"] input {
    color: #fff !important;
    -webkit-text-fill-color: #fff !important;
    background: transparent !important;
}
.stNumberInput button {
    background: transparent !important;
    color: #D4D4D8 !important;
    border: none !important;
    transition: background .25s ease;
}
.stNumberInput button:hover {background: rgba(255,255,255,0.10) !important;}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {gap: 6px; border-bottom: 1px solid rgba(255,255,255,0.09);}
.stTabs [data-baseweb="tab"] {
    font-weight: 500; font-size: 14px; color: #8E8E96; background: transparent;
    transition: color .3s ease;
}
.stTabs [data-baseweb="tab"]:hover {color: #fff;}
.stTabs [aria-selected="true"] {color: #fff;}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #fff; height: 2px;
    box-shadow: 0 0 12px rgba(255,255,255,0.8);
}

/* Button */
div.stFormSubmitButton > button {
    background: #fff;
    border: none;
    border-radius: 14px;
    padding: 14px 0;
    transition: all .35s cubic-bezier(.2,.8,.2,1);
    box-shadow: 0 0 0 rgba(255,255,255,0);
}
div.stFormSubmitButton > button p {color: #0A0A0C !important; font-size: 15.5px; font-weight: 700; letter-spacing: 0.3px;}
div.stFormSubmitButton > button:hover {
    background: #fff;
    border: none;
    transform: translateY(-2px);
    box-shadow: 0 8px 34px rgba(255,255,255,0.30);
}
div.stFormSubmitButton > button:active {transform: translateY(0);}

/* ---------- Result ---------- */
.result-card {
    text-align: center;
    padding: 34px 28px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.12);
    background:
        radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
        linear-gradient(160deg, #1B1C1F 0%, #0E0E10 100%);
    background-size: 18px 18px, 100% 100%;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.08);
    animation: fadeUp .9s cubic-bezier(.2,.8,.2,1) both;
}
.badge {
    display: inline-flex; align-items: center; gap: 9px;
    padding: 6px 15px; border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.14);
    font-size: 11.5px; font-weight: 600; letter-spacing: 1.6px;
    text-transform: uppercase; color: #C4C4CA;
}
.badge-dot {width: 8px; height: 8px; border-radius: 50%; background: var(--c); box-shadow: 0 0 12px var(--c);}
.result-value {
    font-size: 60px; font-weight: 800; color: #fff; line-height: 1.1;
    margin: 18px 0 6px 0;
    text-shadow: 0 0 40px rgba(255,255,255,0.25);
}
.result-headline {font-size: 17px; font-weight: 600; color: #F4F4F5; margin-bottom: 8px;}
.result-msg {font-size: 14px; color: #9A9AA2; line-height: 1.7; max-width: 420px; margin: 0 auto 24px auto;}
.level-bar {display: flex; gap: 7px; max-width: 360px; margin: 0 auto;}
.seg {
    flex: 1; height: 7px; border-radius: 999px; transform-origin: left;
    animation: grow .8s cubic-bezier(.2,.8,.2,1) both;
    animation-delay: calc(var(--i) * 0.14s + 0.35s);
}
.level-labels {
    display: flex; justify-content: space-between; max-width: 360px;
    margin: 9px auto 0 auto; font-size: 11.5px; color: #6B6B73; font-weight: 500;
}

/* ---------- Panels ---------- */
.panel {
    padding: 24px 28px;
    border-radius: 20px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.09);
    box-shadow: 0 10px 40px rgba(0,0,0,0.35);
    animation: fadeUp .9s .15s cubic-bezier(.2,.8,.2,1) both;
}
.panel-title {font-size: 15px; font-weight: 700; color: #fff; margin-bottom: 8px;}
.action {
    display: flex; gap: 14px; align-items: flex-start;
    padding: 12px 0; border-top: 1px solid rgba(255,255,255,0.07);
    font-size: 14px; color: #C4C4CA; line-height: 1.6;
    transition: transform .3s ease, color .3s ease;
}
.action:first-of-type {border-top: none;}
.action:hover {transform: translateX(4px); color: #fff;}
.action-num {
    min-width: 26px; height: 26px; border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.25);
    color: #fff; font-size: 12px; font-weight: 600;
    display: flex; align-items: center; justify-content: center;
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 14px 18px;
    transition: all .35s cubic-bezier(.2,.8,.2,1);
    animation: fadeUp .9s .25s cubic-bezier(.2,.8,.2,1) both;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(255,255,255,0.22);
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}
[data-testid="stMetricLabel"] p {font-size: 12.5px !important; color: #8E8E96;}
[data-testid="stMetricValue"] {font-weight: 700; color: #fff;}

.chart-label {font-size: 13px; font-weight: 500; color: #A1A1AA; margin-bottom: 6px;}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0C0C0E 0%, #151618 100%);
    border-right: 1px solid rgba(255,255,255,0.07);
}
.side-brand {font-size: 21px; font-weight: 800; color: #fff; letter-spacing: -0.3px;}
.side-sub {font-size: 12.5px; color: #8E8E96; margin-top: 3px; display: flex; align-items: center; gap: 8px;}
.side-h {
    font-size: 11px; font-weight: 600; letter-spacing: 1.8px;
    text-transform: uppercase; color: #6B6B73; margin: 24px 0 9px 0;
}
.side-text {font-size: 13.5px; color: #A1A1AA; line-height: 1.7;}
.side-step {display: flex; gap: 10px; font-size: 13.5px; color: #A1A1AA; margin-bottom: 9px;}
.side-step b {color: #fff;}

.footer-note {text-align: center; color: #6B6B73; font-size: 12.5px; margin-top: 10px;}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="side-brand">DengueGuard AI</div>
        <div class="side-sub"><span class="live-dot"></span> Risk monitoring online</div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown('<div class="side-h">About</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-text">A machine-learning tool that classifies dengue risk '
        "for a ward from recent case counts and four weeks of weather. "
        "Built to help teams act early and keep communities safe.</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-h">How it works</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="side-step"><b>01</b><span>Enter the ward and last week's cases</span></div>
        <div class="side-step"><b>02</b><span>Add four weeks of weather data</span></div>
        <div class="side-step"><b>03</b><span>Run the prediction and review next steps</span></div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption(datetime.now().strftime("%d %B %Y"))

# ----------------------------------------------------------------------------
# Hero with dot-matrix mosquito
# ----------------------------------------------------------------------------
st.markdown(
    f"""
<div class="hero fade">
    <div class="hero-text">
        <div class="hero-tag"><span class="live-dot"></span> AI-powered · Bangladesh</div>
        <div class="hero-title">DengueGuard AI</div>
        <div class="hero-sub">
            Early warning, early action. Turn weather and case data into clear
            dengue risk insight that helps protect your community.
        </div>
    </div>
    <div class="mosq-wrap">{mosquito_svg()}</div>
</div>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Risk levels (legend)
# ----------------------------------------------------------------------------
chips = "".join(
    f'<div class="chip"><span class="chip-dot" style="background:{cfg["color"]};color:{cfg["color"]}"></span>{name}</div>'
    for name, cfg in RISK_LEVELS.items()
)
st.markdown(
    f"""
    <div class="fade fade-2">
        <div class="section-title">Risk levels</div>
        <div class="section-caption">Each ward is classified into one of four levels.</div>
        <div class="chip-row">{chips}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.write("")

# ----------------------------------------------------------------------------
# Prediction form
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="fade fade-3">
        <div class="section-title">Check a ward</div>
        <div class="section-caption">Enter last week's cases and four weeks of weather.
        Week 1 is the most recent. It only takes a minute.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

WEEK_LABELS = ["1 week ago", "2 weeks ago", "3 weeks ago", "4 weeks ago"]

with st.form("prediction_form"):
    tab_ward, tab_temp, tab_rain, tab_hum = st.tabs(
        ["Ward & cases", "Temperature", "Rainfall", "Humidity"]
    )

    with tab_ward:
        c1, c2 = st.columns(2)
        with c1:
            ward_id = st.number_input(
                "Ward ID", min_value=1, step=1,
                help="Numeric ID of the ward you want to assess.",
            )
        with c2:
            cases_lag_1 = st.number_input(
                "Dengue cases in previous week", min_value=0, step=1,
                help="Reported dengue cases in this ward during the last week.",
            )

    with tab_temp:
        defaults = [28.5, 29.0, 28.0, 27.5]
        c1, c2 = st.columns(2)
        temps = []
        for i, (label, d) in enumerate(zip(WEEK_LABELS, defaults)):
            with (c1 if i % 2 == 0 else c2):
                temps.append(st.number_input(f"Temperature, {label} (°C)", value=d, key=f"t{i}"))

    with tab_rain:
        defaults = [45.0, 50.0, 35.0, 40.0]
        c1, c2 = st.columns(2)
        rains = []
        for i, (label, d) in enumerate(zip(WEEK_LABELS, defaults)):
            with (c1 if i % 2 == 0 else c2):
                rains.append(
                    st.number_input(f"Rainfall, {label} (mm)", min_value=0.0, value=d, key=f"r{i}")
                )

    with tab_hum:
        defaults = [80.0, 82.0, 78.0, 85.0]
        c1, c2 = st.columns(2)
        hums = []
        for i, (label, d) in enumerate(zip(WEEK_LABELS, defaults)):
            with (c1 if i % 2 == 0 else c2):
                hums.append(
                    st.number_input(
                        f"Humidity, {label} (%)",
                        min_value=0.0, max_value=100.0, value=d, key=f"h{i}",
                    )
                )

    submitted = st.form_submit_button("Predict dengue risk", use_container_width=True)

# ----------------------------------------------------------------------------
# Prediction
# ----------------------------------------------------------------------------
if submitted:
    input_data = {
        "ward_id": ward_id,
        "cases_lag_1": cases_lag_1,
        "avg_temp_c_lag_1": temps[0],
        "avg_temp_c_lag_2": temps[1],
        "avg_temp_c_lag_3": temps[2],
        "avg_temp_c_lag_4": temps[3],
        "rainfall_mm_lag_1": rains[0],
        "rainfall_mm_lag_2": rains[1],
        "rainfall_mm_lag_3": rains[2],
        "rainfall_mm_lag_4": rains[3],
        "relative_humidity_pct_lag_1": hums[0],
        "relative_humidity_pct_lag_2": hums[1],
        "relative_humidity_pct_lag_3": hums[2],
        "relative_humidity_pct_lag_4": hums[3],
    }

    try:
        with st.spinner("Analysing weather and dengue information..."):
            prediction = predict_dengue_risk(input_data)

        st.write("")
        st.markdown('<div class="section-title fade">Prediction result</div>', unsafe_allow_html=True)
        st.write("")

        key = str(prediction).strip().title()
        cfg = RISK_LEVELS.get(key)

        left, right = st.columns([1, 1.1], gap="large")

        with left:
            if cfg:
                st.markdown(
                    f"""
                    <div class="result-card" style="--c:{cfg['color']}">
                        <span class="badge"><span class="badge-dot"></span>Predicted risk level</span>
                        <div class="result-value">{key}</div>
                        <div class="result-headline">{cfg['headline']}</div>
                        <div class="result-msg">{cfg['message']}</div>
                        {level_bar(cfg['level'], cfg['color'])}
                        <div class="level-labels">
                            <span>Low</span><span>Medium</span><span>High</span><span>Critical</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.info(f"Predicted Risk: {prediction}")

        with right:
            if cfg:
                items = "".join(
                    f'<div class="action"><div class="action-num">{i}</div><div>{a}</div></div>'
                    for i, a in enumerate(cfg["actions"], start=1)
                )
                st.markdown(
                    f'<div class="panel"><div class="panel-title">Recommended next steps</div>{items}</div>',
                    unsafe_allow_html=True,
                )

            st.write("")
            m1, m2, m3 = st.columns(3)
            m1.metric("Ward", int(ward_id))
            m2.metric("Cases", int(cases_lag_1))
            m3.metric("Avg temp", f"{sum(temps) / 4:.1f} °C")

        # Weather trend (oldest -> most recent)
        st.write("")
        st.markdown(
            """
            <div class="section-title fade">Weather trend</div>
            <div class="section-caption">The four weeks of data behind this prediction.</div>
            """,
            unsafe_allow_html=True,
        )
        order = [3, 2, 1, 0]
        trend = pd.DataFrame(
            {
                "Week": [WEEK_LABELS[i] for i in order],
                "Temperature (°C)": [temps[i] for i in order],
                "Rainfall (mm)": [rains[i] for i in order],
                "Humidity (%)": [hums[i] for i in order],
            }
        ).set_index("Week")

        t1, t2, t3 = st.columns(3)
        with t1:
            st.markdown('<div class="chart-label">Temperature (°C)</div>', unsafe_allow_html=True)
            st.line_chart(trend[["Temperature (°C)"]], height=200, color="#FFFFFF")
        with t2:
            st.markdown('<div class="chart-label">Rainfall (mm)</div>', unsafe_allow_html=True)
            st.bar_chart(trend[["Rainfall (mm)"]], height=200, color="#FFFFFF")
        with t3:
            st.markdown('<div class="chart-label">Humidity (%)</div>', unsafe_allow_html=True)
            st.line_chart(trend[["Humidity (%)"]], height=200, color="#FFFFFF")

    except Exception as e:
        st.error(f"Prediction failed: {e}")

# ----------------------------------------------------------------------------
# Footer
# ----------------------------------------------------------------------------
st.write("")
st.divider()
st.caption(
    "Disclaimer: Risk categories are derived from the training dataset. "
    "They are not medical diagnoses or official public-health alerts."
)
st.markdown(
    '<div class="footer-note">DengueGuard AI · Machine Learning Project · Bangladesh</div>',
    unsafe_allow_html=True,
)
