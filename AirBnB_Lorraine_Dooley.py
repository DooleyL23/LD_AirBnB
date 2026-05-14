import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = Path(__file__).parent / "BigML_Dataset_airBnB.csv"

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
MINTY_GREEN  = "#78C2AD"
MINTY_ACCENT = "#F3969A"
MINTY_YELLOW = "#FFCE67"
MINTY_BLUE   = "#6CC3D5"
MINTY_PURPLE = "#8A6BD8"
SEQ_SCALE    = [[0, MINTY_BLUE], [0.5, MINTY_GREEN], [1, MINTY_ACCENT]]
CAT_COLORS   = [MINTY_GREEN, MINTY_ACCENT, MINTY_YELLOW, MINTY_BLUE, MINTY_PURPLE,
                "#FF8C69", "#A8D8B9", "#C9B8E8"]

dark = st.session_state.dark_mode
bg        = "#1A2821" if dark else "#F8FBF9"
card_bg   = "#243328" if dark else "#FFFFFF"
text_col  = "#E2F0EC" if dark else "#2D4A3E"
sub_col   = "#8ABFB0" if dark else "#6C8F82"
border    = "#2E4A3C" if dark else "#D4EDE6"
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
      font-size: 60px;
      font-weight: 700;
      color: {MINTY_GREEN};
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
      font-size: 48px;
      font-weight: 700;
      color: {MINTY_GREEN};
  }}
  .metric-label {{
      font-size: 28px;
      color: {sub_col};
      margin-top: 3px;
  }}
  .stTabs [data-baseweb="tab-list"] {{
      background: {card_bg};
      border-radius: 10px;
      padding: 4px;
      gap: 4px;
      border: 1px solid {border};
      display: flex;
      width: 100%;
  }}
  .stTabs [data-baseweb="tab"] {{
      border-radius: 8px;
      color: {sub_col};
      font-weight: 500;
      flex: 1;
      justify-content: center;
  }}
  .stTabs [aria-selected="true"] {{
      background: {MINTY_GREEN} !important;
      color: #fff !important;
      font-sixe:30px!important;
  }}
  .section-heading {{
      font-size: 30px;
      font-weight: 600;
      color: {text_col};
      margin: 1rem 0 0.4rem;
      border-left: 4px solid {MINTY_GREEN};
      padding-left: 0.6rem;
  }}
  header[data-testid="stHeader"] {{ display: none; }}
</style>
""", unsafe_allow_html=True)

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
        '<h1 class="dashboard-title">🏠 <span>Airbnb Amsterdam — Data Analysis</span></h1>',
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

    k1, k2, k3, k4, k5 = st.columns(5)
    for col, val, label in [
        (k1, f"€{avg_price:.0f}",      "Avg Nightly Price"),
        (k2, f"{total_list:,}",         "Total Listings"),
        (k3, f"{avg_rating:.1f}/100",   "Avg Review Score"),
        (k4, f"{superhost_pct:.0f}%",   "Superhost Listings"),
        (k5, f"{avg_avail:.0f} days",   "Avg Availability/yr"),
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

