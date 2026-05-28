import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px

DATA_PATH = Path(__file__).parent / "BigML_Dataset_airBnB.csv"
LOGO_PATH = Path(__file__).parent / "airbnb__Logo.png"

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

# ── Text size toggle ──────────────────────────────────────────────────────────
if "large_text" not in st.session_state:
    st.session_state.large_text = False

# ── Palette ───────────────────────────────────────────────────────────────────
AIRBNB_RED  = "#FF385C"
AIRBNB_DARK = "#222222"
AIRBNB_GRAY = "#F7F7F7"
AIRBNB_PINK = "#FF8CA0"
AIRBNB_SOFT = "#FFB3BF"
CAT_COLORS  = [AIRBNB_RED, "#484848", AIRBNB_PINK, "#767676",
               AIRBNB_SOFT, "#222222", "#FF6B80", "#AAAAAA"]

dark = st.session_state.dark_mode
large = st.session_state.large_text

bg       = "#1A1A1A" if dark else AIRBNB_GRAY
card_bg  = "#2A2A2A" if dark else "#FFFFFF"
text_col = "#F7F7F7" if dark else "#111111"   # darkened from #222 for better contrast
sub_col  = "#CCCCCC" if dark else "#333333"   # darkened from #484848 for better contrast
border   = "#555555" if dark else "#CCCCCC"
plot_bg  = "#2A2A2A" if dark else "#FFFFFF"
plot_tmpl = "plotly_dark" if dark else "plotly_white"
map_style = "carto-darkmatter" if dark else "carto-positron"

# ── Text sizes — normal vs large ──────────────────────────────────────────────
base_body     = "1.15rem"  if large else "1rem"
metric_val_sz = "2.4rem"   if large else "2rem"
metric_lbl_sz = "1.1rem"   if large else "0.95rem"
tab_font_sz   = "1.15rem"  if large else "1rem"
section_sz    = "1.1rem"   if large else "0.95rem"
caption_sz    = "1rem"     if large else "0.85rem"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* ── Base ── */
  .stApp {{
      background-color: {bg};
      color: {text_col};
      font-family: 'Segoe UI', system-ui, sans-serif;
      font-size: {base_body};
  }}

  /* ── Title ── */
  .dashboard-title {{
      font-size: 2rem;
      font-weight: 700;
      color: {AIRBNB_RED};
      margin: 0;
  }}

  /* ── Metric cards ── */
  .metric-card {{
      background: {card_bg};
      border: 1.5px solid {border};
      border-radius: 14px;
      padding: 1.4rem 1.2rem;
      text-align: center;
      box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  }}
  .metric-value {{
      font-size: {metric_val_sz};
      font-weight: 700;
      color: {AIRBNB_RED};
      line-height: 1.2;
  }}
  .metric-label {{
      font-size: {metric_lbl_sz};
      font-weight: 600;
      color: {sub_col};
      margin-top: 5px;
  }}
  .metric-caption {{
      font-size: {caption_sz};
      color: {sub_col};
      margin-top: 6px;
      line-height: 1.4;
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
      font-weight: 700;
      font-size: {tab_font_sz};
      padding: 1.2rem 1.5rem;
      border: none;
      border-radius: 0;
      margin: 0;
      clip-path: polygon(0 0, calc(100% - 18px) 0, 100% 50%, calc(100% - 18px) 100%, 0 100%, 18px 50%);
      transition: background 0.2s, color 0.2s;
      z-index: 1;
  }}
  .stTabs [data-baseweb="tab"] p {{
      font-size: {tab_font_sz} !important;
      font-weight: 700;
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
  .stTabs [data-baseweb="tab-highlight"] {{ display: none; }}
  .stTabs [data-baseweb="tab-border"]    {{ display: none; }}

  /* ── Section headings ── */
  .section-heading {{
      font-size: {section_sz};
      font-weight: 700;
      color: {text_col};
      margin: 1.2rem 0 0.5rem;
      border-left: 4px solid {AIRBNB_RED};
      padding-left: 0.6rem;
  }}

  /* ── Chart captions ── */
  .chart-caption {{
      font-size: {caption_sz};
      color: {sub_col};
      margin-top: 4px;
      margin-bottom: 12px;
      font-style: italic;
      line-height: 1.5;
  }}

  /* ── Glossary / help box ── */
  .help-box {{
      background: {card_bg};
      border: 1.5px solid {border};
      border-left: 5px solid {AIRBNB_RED};
      border-radius: 10px;
      padding: 1rem 1.2rem;
      margin-bottom: 1rem;
  }}
  .help-term {{
      font-weight: 700;
      color: {AIRBNB_RED};
      font-size: {base_body};
  }}
  .help-def {{
      color: {text_col};
      font-size: {base_body};
      line-height: 1.6;
  }}

  /* ── Toggle buttons row ── */
  .toggle-row {{
      display: flex;
      gap: 0.6rem;
      align-items: center;
      justify-content: flex-end;
  }}

  /* ── Hide Streamlit chrome ── */
  header[data-testid="stHeader"] {{ display: none; }}
  #MainMenu {{ visibility: hidden; }}
  footer {{ visibility: hidden; }}
  [data-testid="manage-app-button"] {{ display: none !important; }}
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
    df["latitude"]  = df["latitude"].astype(str).str.replace(",", ".").astype(float)
    df["longitude"] = df["longitude"].astype(str).str.replace(",", ".").astype(float)
    df["host_is_superhost"] = df["host_is_superhost"].map({"t": True, "f": False})
    df["instant_bookable"]  = df["instant_bookable"].map({"t": True, "f": False})
    p1, p99 = df["price"].quantile(0.01), df["price"].quantile(0.99)
    df = df[(df["price"] >= p1) & (df["price"] <= p99)]
    return df

df = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_toggles = st.columns([5, 2])

with col_title:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:1rem;">'
        f'<img src="data:image/png;base64,{logo_b64}" style="height:60px;width:auto;">'
        f'<h1 class="dashboard-title">airbnb Amsterdam — Data Analysis</h1>'
        f'</div>',
        unsafe_allow_html=True,
    )

with col_toggles:
    st.markdown('<div class="toggle-row">', unsafe_allow_html=True)
    t1, t2 = st.columns(2)
    with t1:
        dark_label = "☀️ Light mode" if dark else "🌙 Dark mode"
        if st.button(dark_label, use_container_width=True, help="Switch between light and dark display"):
            st.session_state.dark_mode = not dark
            st.rerun()
    with t2:
        text_label = "🔡 Normal text" if large else "🔠 Larger text"
        if st.button(text_label, use_container_width=True, help="Make all text bigger or smaller"):
            st.session_state.large_text = not large
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_overview, tab_neighbourhoods, tab_map, tab_rooms, tab_help = st.tabs([
    "📊 Overview",
    "🏘️ Neighbourhoods",
    "🗺️ Map",
    "🛏️ Room Types",
    "❓ Help & Glossary",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Overview
# ─────────────────────────────────────────────────────────────────────────────
with tab_overview:

    avg_price = df["price"].mean()
    total_list = len(df)
    avg_rating = df["review_scores_rating"].mean()
    avg_avail  = df["availability_365"].mean()

    k1, k2, k3, k4 = st.columns(4)
    cards = [
        (k1, f"€{avg_price:.0f}",     "Avg Nightly Price",
         "The typical cost of one night in an Amsterdam listing."),
        (k2, f"{total_list:,}",        "Total Listings",
         "The number of homes and rooms available across Amsterdam."),
        (k3, f"{avg_rating:.1f}/100",  "Avg Review Score",
         "Guests rate stays out of 100. Anything above 90 is excellent."),
        (k4, f"{avg_avail:.0f} days",  "Avg Availability/yr",
         "On average, how many days per year each listing is open to book."),
    ]
    for col, val, label, caption in cards:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{val}</div>'
                f'<div class="metric-label">{label}</div>'
                f'<div class="metric-caption">{caption}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.2])

    with c1:
        st.markdown('<p class="section-heading">Room Type</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="chart-caption">Shows the split between entire homes, private rooms, and shared rooms across all listings.</p>',
            unsafe_allow_html=True,
        )
        room_counts = df["room_type"].value_counts().reset_index()
        room_counts.columns = ["Room Type", "Count"]
        fig_room = px.pie(
            room_counts, values="Count", names="Room Type",
            color_discrete_sequence=["#FF385C", "#333333", "#FF8CA0"],
            hole=0.55,
        )
        fig_room.update_traces(
            textinfo="percent+label",
            textfont_size=14,       # larger slice labels
        )
        fig_room.update_layout(
            showlegend=True,
            legend=dict(font=dict(size=14), orientation="h", y=-0.15),
            margin=dict(l=0, r=0, t=10, b=40),
            paper_bgcolor=plot_bg,
            height=280,
            font=dict(family="Segoe UI", size=14, color=text_col),
        )
        st.plotly_chart(fig_room, use_container_width=True)

    with c2:
        st.markdown('<p class="section-heading">Property Types</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="chart-caption">The six most common property types listed in Amsterdam. Apartments make up the large majority.</p>',
            unsafe_allow_html=True,
        )
        prop_counts = df["property_type"].value_counts().head(6).reset_index()
        prop_counts.columns = ["Property Type", "Count"]
        fig_prop = px.bar(
            prop_counts, x="Count", y="Property Type", orientation="h",
            color="Count",
            color_continuous_scale=["#FFB3BF", "#FF385C", "#C0392B"],
            text="Count",
        )
        fig_prop.update_traces(
            textposition="outside",
            textfont_size=14,       
        )
        fig_prop.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            plot_bgcolor=plot_bg,
            paper_bgcolor=plot_bg,
            margin=dict(l=0, r=70, t=10, b=0),
            height=280,
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False, title="", tickfont=dict(size=14, color=text_col)),
            font=dict(family="Segoe UI", size=14, color=text_col),
        )
        st.plotly_chart(fig_prop, use_container_width=True)

    st.markdown('<p class="section-heading">Price Distribution</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="chart-caption">Most listings in Amsterdam are priced between €50 and €200 per night. '
        'Each colour represents a different room type. Use the legend to identify them.</p>',
        unsafe_allow_html=True,
    )
    fig_hist = px.histogram(
        df[df["price"] < 500], x="price", nbins=60,
        color="room_type",
        color_discrete_sequence=["#FF385C", "#333333", "#FF8CA0"],
        labels={"price": "Price per night (€)", "room_type": "Room type"},
        barmode="overlay", opacity=0.85,
    )
    fig_hist.update_layout(
        plot_bgcolor=plot_bg,
        paper_bgcolor=plot_bg,
        margin=dict(l=0, r=0, t=10, b=0),
        height=300,
        xaxis=dict(
            showgrid=False,
            title="Price per night (€)",
            title_font=dict(size=14, color=text_col),
            tickfont=dict(size=13, color=text_col),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#E0E0E0" if not dark else "#3A3A3A",
            title="Number of listings",
            title_font=dict(size=14, color=text_col),
            tickfont=dict(size=13, color=text_col),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1, xanchor="right", x=1,
            font=dict(size=14, color=text_col),
            title_text="Room type",
        ),
        font=dict(family="Segoe UI", size=14, color=text_col),
    )
    st.plotly_chart(fig_hist, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Neighbourhoods
# ─────────────────────────────────────────────────────────────────────────────
with tab_neighbourhoods:
    st.info("Neighbourhood data.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Map
# ─────────────────────────────────────────────────────────────────────────────
with tab_map:
    st.info("Map data.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Room Types
# ─────────────────────────────────────────────────────────────────────────────
with tab_rooms:
    st.info("Room type data.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — Help & Glossary
# ─────────────────────────────────────────────────────────────────────────────
with tab_help:
    st.markdown('<p class="section-heading">Help & Glossary</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:{base_body}; color:{sub_col}; margin-bottom:1.2rem;">'
        "Not sure what a term means? Find plain-English explanations for everything on this dashboard below."
        "</p>",
        unsafe_allow_html=True,
    )

    glossary = [
        ("Avg Nightly Price",
         "The average cost of staying one night across all Amsterdam listings in this dataset."),
        ("Total Listings",
         "The total number of homes, apartments, and rooms available to book on Airbnb in Amsterdam."),
        ("Avg Review Score",
         "Guests leave a score out of 100 after their stay. A score above 90 means guests are very satisfied. "
         "A score above 95 is outstanding."),
        ("Avg Availability/yr",
         "On average, how many days per year a listing is available to book. A higher number means the host "
         "keeps the listing open for longer periods."),
        ("Entire home/apt",
         "You have the whole property to yourself — no shared spaces. Best for couples or anyone who values privacy."),
        ("Private room",
         "You have your own bedroom, but may share common areas such as the kitchen or living room with the host "
         "or other guests."),
        ("Shared room",
         "You share a bedroom or open sleeping space with other guests. This is the most affordable option."),
        ("Superhost",
         "A superhost is an experienced, highly-rated Airbnb host who consistently receives excellent reviews "
         "and responds quickly to guests."),
        ("Instant Bookable",
         "Some listings can be booked immediately without waiting for the host to approve your request. "
         "These are marked as instant bookable."),
        ("Review Score — Accuracy",
         "Did the listing look the same as it did in the photos and description? A high score means no surprises."),
        ("Review Score — Cleanliness",
         "How clean guests found the property when they arrived."),
        ("Review Score — Location",
         "How guests rated the neighbourhood — things like transport links, nearby shops, and safety."),
        ("Review Score — Value",
         "Whether guests felt the price they paid was fair for what they received."),
    ]

    for term, definition in glossary:
        st.markdown(
            f'<div class="help-box">'
            f'<div class="help-term">{term}</div>'
            f'<div class="help-def">{definition}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f'<p style="text-align:center;color:{sub_col};font-size:{caption_sz};">'
    f"Airbnb Amsterdam · {len(df):,} listings · Built with Streamlit · Designed for people aged 65+"
    "</p>",
    unsafe_allow_html=True,
)