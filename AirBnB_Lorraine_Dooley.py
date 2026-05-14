import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = Path(__file__).parent / "BigML_Dataset_airBnB.csv"
LOGO_PATH = Path(__file__).parent / "airbnb_logo.png"


import base64
def get_logo_b64():
    with open(LOGO_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode()
logo_b64 = get_logo_b64()
 
 
# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Airbnb Amsterdam",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)
 
# ── Theme toggle ──────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
 
# ── Palette (Minty-inspired) ──────────────────────────────────────────────────
AIRBNB_RED   = "#FF385C"
AIRBNB_DARK  = "#222222"
AIRBNB_GRAY  = "#F7F7F7"
AIRBNB_PINK  = "#FF8CA0"
AIRBNB_SOFT  = "#FFB3BF"
SEQ_SCALE    = [[0, "#FFB3BF"], [0.5, "#FF385C"], [1, "#222222"]]
CAT_COLORS   = [AIRBNB_RED, "#484848", AIRBNB_PINK, "#767676",
                AIRBNB_SOFT, "#222222", "#FF6B80", "#AAAAAA"]
 
dark = st.session_state.dark_mode
bg        = "#1A1A1A" if dark else AIRBNB_GRAY
card_bg   = "#2A2A2A" if dark else "#FFFFFF"
text_col  = "#F7F7F7" if dark else AIRBNB_DARK
sub_col   = "#AAAAAA" if dark else "#484848"
border    = "#444444" if dark else "#DDDDDD"
plot_tmpl = "plotly_dark" if dark else "plotly_white"
map_style = "carto-darkmatter" if dark else "carto-positron"
 
# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{
      background-color: {bg};
      color: {text_col};
      font-family: 'Segoe UI', system-ui, sans-serif;
  }}
  .dashboard-title {{
      font-size: 1.85rem;
      font-weight: 700;
      color: {AIRBNB_RED};
      margin: 0;
  }}
  .dashboard-title span {{ color: {text_col}; }}
  .metric-card {{
      background: {card_bg};
      border: 1px solid {border};
      border-radius: 12px;
      padding: 1.1rem 1.2rem;
      text-align: center;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  .metric-value {{
      font-size: 1.9rem;
      font-weight: 700;
      color: {AIRBNB_RED};
  }}
  .metric-label {{
      font-size: 1.2rem;
      color: {sub_col};
      margin-top: 3px;
  }}
  /* ── Chevron tab strip ── */
  .stTabs [data-baseweb="tab-list"] {{
      background: transparent;
      border: none;
      padding: 0;
      gap: 0;
      display: flex;
      width: 100%;
      overflow: visible !important;
  }}
  .stTabs [data-baseweb="tab"] {{
      position: relative;
      flex: 1;
      justify-content: center;
      background: {border};
      color: {sub_col};
      font-weight: 600;
      font-size: 30px;
      padding: 1.5rem 1.5rem;
      border: none;
      border-radius: 0;
      margin: 0;
      clip-path: polygon(0 0, calc(100% - 18px) 0, 100% 50%, calc(100% - 18px) 100%, 0 100%, 18px 50%);
      transition: background 0.2s, color 0.2s;
      z-index: 1;
  }}
  .stTabs [data-baseweb="tab"] p {{
      font-size: 30px !important;
      font-weight: 600;
  }}
  .stTabs [aria-selected="true"] {{
      background: {AIRBNB_RED} !important;
      color: #fff !important;
      z-index: 2;
  }}
  .stTabs [data-baseweb="tab"]:not([aria-selected="true"]):hover {{
      background: {AIRBNB_DARK} !important;
      color: #fff !important;
  }}
  .section-heading {{
      font-size: 1rem;
      font-weight: 600;
      color: {text_col};
      margin: 1rem 0 0.4rem;
      border-left: 4px solid {AIRBNB_RED};
      padding-left: 0.6rem;
  }}
  header[data-testid="stHeader"] {{ display: none; }}
  .stTabs [data-baseweb="tab-highlight"] {{ display: none; }}
  .stTabs [data-baseweb="tab-border"] {{ display: none; }}
  /* Font Awesome icons on tabs via ::before */
  .stTabs [data-baseweb="tab"]:nth-child(1) p::before {{
      font-family: "Font Awesome 6 Free";
      font-weight: 900;
      content: "\f080  ";
      color: white;
  }}
  .stTabs [data-baseweb="tab"]:nth-child(2) p::before {{
      font-family: "Font Awesome 6 Free";
      font-weight: 900;
      content: "\f015  ";
      color: white;
  }}
  .stTabs [data-baseweb="tab"]:nth-child(3) p::before {{
      font-family: "Font Awesome 6 Free";
      font-weight: 900;
      content: "\f279  ";
      color: white;
  }}
  .stTabs [data-baseweb="tab"]:nth-child(4) p::before {{
      font-family: "Font Awesome 6 Free";
      font-weight: 900;
      content: "\f236  ";
      color: white;
  }}
  /* Make unselected tab icons match tab text colour */
  .stTabs [data-baseweb="tab"]:not([aria-selected="true"]) p::before {{
      color: {sub_col};
  }}
</style>
""", unsafe_allow_html=True)
 
# ── Font Awesome ──────────────────────────────────────────────────────────────
st.markdown(
    '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v6.4.2/css/all.css">',
    unsafe_allow_html=True,
)
 
# ── Data loading & cleaning ───────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    # Fix European decimal separators in lat/lon
    df["latitude"]  = df["latitude"].astype(str).str.replace(",", ".").astype(float)
    df["longitude"] = df["longitude"].astype(str).str.replace(",", ".").astype(float)

    # Boolean columns
    df["host_is_superhost"] = df["host_is_superhost"].map({"t": True, "f": False})
    df["instant_bookable"]  = df["instant_bookable"].map({"t": True, "f": False})

    # Drop extreme price outliers (keep 1st–99th percentile)
    p1, p99 = df["price"].quantile(0.01), df["price"].quantile(0.99)
    df = df[(df["price"] >= p1) & (df["price"] <= p99)]

    return df

df = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_toggle = st.columns([6, 1])
with col_title:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:1rem;">'  
        f'<img src="data:image/png;base64,{logo_b64}" style="height:60px;width:auto;">'  
        f'<p class="dashboard-title" style="margin:0;">Airbnb Amsterdam — Data Analysis</p>'  
        f'</div>',
        unsafe_allow_html=True,
    )
with col_toggle:
    label = "☀️ Light" if dark else "🌙 Dark"
    if st.button(label, use_container_width=True):
        st.session_state.dark_mode = not dark
        st.rerun()

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_overview, tab_neighbourhoods, tab_map, tab_rooms = st.tabs(
    ["📊 Overview", "🏘️ Neighbourhoods", "🗺️ Map", "🛏️ Room Types"]
)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Overview
# ─────────────────────────────────────────────────────────────────────────────
with tab_overview:
    avg_price     = df["price"].mean()
    total_list    = len(df)
    avg_rating    = df["review_scores_rating"].mean()
    superhost_pct = df["host_is_superhost"].mean() * 100
    avg_avail     = df["availability_365"].mean()

    k1, k2, k3, k4 = st.columns(4)
    for col, val, label in [
        (k1, f"€{avg_price:.0f}",      "Avg Nightly Price"),
        (k2, f"{total_list:,}",         "Total Listings"),
        (k3, f"{avg_rating:.1f}/100",   "Avg Review Score"),
        (k4, f"{avg_avail:.0f} days",   "Avg Availability/yr"),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{val}</div>'
                f'<div class="metric-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Neighbourhood
# ─────────────────────────────────────────────────────────────────────────────
with tab_neighbourhoods:
    st.info("Neighborhood Data.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Map 
# ─────────────────────────────────────────────────────────────────────────────
with tab_map:
    st.info("Map Data")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Room Types
# ─────────────────────────────────────────────────────────────────────────────
with tab_rooms:
    st.info("Room Information.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f'<p style="text-align:center;color:{sub_col};font-size:0.8rem;">'
    f"Airbnb Amsterdam · {len(df):,} listings · Built with Streamlit. Designed for People 65+"
    "</p>",
    unsafe_allow_html=True,
)

