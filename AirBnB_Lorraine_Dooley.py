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

# ── Session state defaults ────────────────────────────────────────────────────
if "dark_mode"  not in st.session_state: st.session_state.dark_mode  = False
if "large_text" not in st.session_state: st.session_state.large_text = False
if "active_tab" not in st.session_state: st.session_state.active_tab = 0

# ── Palette ───────────────────────────────────────────────────────────────────
AIRBNB_RED  = "#FF385C"
AIRBNB_DARK = "#222222"
AIRBNB_GRAY = "#F7F7F7"
AIRBNB_PINK = "#FF8CA0"

dark  = st.session_state.dark_mode
large = st.session_state.large_text

bg       = "#1A1A1A" if dark else AIRBNB_GRAY
card_bg  = "#2A2A2A" if dark else "#FFFFFF"
text_col = "#F7F7F7" if dark else "#111111"
sub_col  = "#CCCCCC" if dark else "#333333"
border   = "#555555" if dark else "#CCCCCC"
plot_bg  = "#2A2A2A" if dark else "#FFFFFF"

# ── Text sizes ────────────────────────────────────────────────────────────────
base_body     = "1.15rem" if large else "1rem"
metric_val_sz = "2.4rem"  if large else "2rem"
metric_lbl_sz = "1.1rem"  if large else "0.95rem"
section_sz    = "1.1rem"  if large else "0.95rem"
caption_sz    = "1rem"    if large else "0.85rem"

# ── Tab definitions ───────────────────────────────────────────────────────────
TABS = [
    ("📊", "Overview",        "Summary figures at a glance"),
    ("🏘️", "Neighbourhoods",  "Explore areas of Amsterdam"),
    ("🗺️", "Map",             "See where listings are located"),
    ("🛏️", "Room Types",      "Compare types of accommodation"),
]
N_TABS = len(TABS)
active = st.session_state.active_tab

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{
      background-color: {bg};
      color: {text_col};
      font-family: 'Segoe UI', system-ui, sans-serif;
      font-size: {base_body};
  }}
  .dashboard-title {{
      font-size: 2rem;
      font-weight: 700;
      color: {AIRBNB_RED};
      margin: 0;
  }}

  /* ── Tab buttons — all inactive tabs ── */
  button[kind="secondary"] {{
      height: auto !important;
      padding: 0.8rem 0.4rem !important;
      border-radius: 12px !important;
      border: 2px solid {border} !important;
      background: {card_bg} !important;
      color: {sub_col} !important;
      font-size: 0.95rem !important;
      font-weight: 600 !important;
      line-height: 1.4 !important;
      transition: all 0.15s !important;
  }}
  button[kind="secondary"]:hover {{
      border-color: {AIRBNB_RED} !important;
      color: {AIRBNB_RED} !important;
      background: {"#3A2020" if dark else "#FFF5F6"} !important;
  }}

  /* ── Active tab — primary button styled red ── */
  button[kind="primary"] {{
      height: auto !important;
      padding: 0.8rem 0.4rem !important;
      border-radius: 12px !important;
      border: 2px solid {AIRBNB_RED} !important;
      background: {AIRBNB_RED} !important;
      color: #ffffff !important;
      font-size: 0.95rem !important;
      font-weight: 700 !important;
      line-height: 1.4 !important;
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
  .metric-value   {{ font-size: {metric_val_sz}; font-weight: 700; color: {AIRBNB_RED}; line-height: 1.2; }}
  .metric-label   {{ font-size: {metric_lbl_sz}; font-weight: 600; color: {sub_col}; margin-top: 5px; }}
  .metric-caption {{ font-size: {caption_sz}; color: {sub_col}; margin-top: 6px; line-height: 1.4; }}

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

  /* ── Glossary boxes ── */
  .help-box {{
      background: {card_bg};
      border: 1.5px solid {border};
      border-left: 5px solid {AIRBNB_RED};
      border-radius: 10px;
      padding: 1rem 1.2rem;
      margin-bottom: 1rem;
  }}
  .help-term {{ font-weight: 700; color: {AIRBNB_RED}; font-size: {base_body}; }}
  .help-def  {{ color: {text_col}; font-size: {base_body}; line-height: 1.6; }}

  /* ── Hide Streamlit chrome ── */
  header[data-testid="stHeader"] {{ display: none; }}
  #MainMenu {{ visibility: hidden; }}
  footer {{ visibility: hidden; }}
  [data-testid="manage-app-button"] {{ display: none !important; }}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
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
    t1, t2 = st.columns(2)
    with t1:
        if st.button("☀️ Light mode" if dark else "🌙 Dark mode",
                     use_container_width=True,
                     help="Switch between light and dark display"):
            st.session_state.dark_mode = not dark
            st.rerun()
    with t2:
        if st.button("🔡 Normal text" if large else "🔠 Larger text",
                     use_container_width=True,
                     help="Make all text bigger or smaller"):
            st.session_state.large_text = not large
            st.rerun()

st.markdown("---")

# ── Tab strip ─────────────────────────────────────────────────────────────────
tab_cols = st.columns(N_TABS)
for i, (icon, label, hint) in enumerate(TABS):
    with tab_cols[i]:
        btn_label = f"{icon} {label}"
        btn_type  = "primary" if i == active else "secondary"
        if st.button(btn_label, key=f"tab_{i}", use_container_width=True,
                     help=hint, type=btn_type):
            st.session_state.active_tab = i
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── Helper: Prev / Next nav ───────────────────────────────────────────────────
def nav_buttons(current_idx: int):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    prev_col, spacer, next_col = st.columns([2, 5, 2])
    if current_idx > 0:
        prev_icon, prev_label, _ = TABS[current_idx - 1]
        with prev_col:
            if st.button(f"← {prev_icon} {prev_label}",
                         key=f"prev_{current_idx}",
                         use_container_width=True,
                         help=f"Go back to {prev_label}"):
                st.session_state.active_tab = current_idx - 1
                st.rerun()
    if current_idx < N_TABS - 1:
        next_icon, next_label, _ = TABS[current_idx + 1]
        with next_col:
            if st.button(f"{next_icon} {next_label} →",
                         key=f"next_{current_idx}",
                         use_container_width=True,
                         type="primary",
                         help=f"Continue to {next_label}"):
                st.session_state.active_tab = current_idx + 1
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 0 — Overview
# ─────────────────────────────────────────────────────────────────────────────
if active == 0:
    avg_price  = df["price"].mean()
    total_list = len(df)
    avg_rating = df["review_scores_rating"].mean()
    avg_avail  = df["availability_365"].mean()

    k1, k2, k3, k4 = st.columns(4)
    cards = [
        (k1, f"€{avg_price:.0f}",    "Avg Nightly Price",
         "The typical cost of one night in an Amsterdam listing."),
        (k2, f"{total_list:,}",       "Total Listings",
         "The number of homes and rooms available across Amsterdam."),
        (k3, f"{avg_rating:.1f}/100", "Avg Review Score",
         "Guests rate stays out of 100. Anything above 90 is excellent."),
        (k4, f"{avg_avail:.0f} days", "Avg Availability/yr",
         "On average, how many days per year each listing is open to book."),
    ]
    for col, val, label, cap in cards:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{val}</div>'
                f'<div class="metric-label">{label}</div>'
                f'<div class="metric-caption">{cap}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.2])

    with c1:
        st.markdown('<p class="section-heading">Room Type</p>', unsafe_allow_html=True)
        st.markdown('<p class="chart-caption">Shows the split between entire homes, private rooms, and shared rooms across all listings.</p>', unsafe_allow_html=True)
        room_counts = df["room_type"].value_counts().reset_index()
        room_counts.columns = ["Room Type", "Count"]
        fig_room = px.pie(
            room_counts, values="Count", names="Room Type",
            color_discrete_sequence=["#FF385C", "#333333", "#FF8CA0"],
            hole=0.55,
        )
        fig_room.update_traces(textinfo="percent+label", textfont_size=14)
        fig_room.update_layout(
            showlegend=True,
            legend=dict(font=dict(size=14), orientation="h", y=-0.15),
            margin=dict(l=0, r=0, t=10, b=40),
            paper_bgcolor=plot_bg, height=280,
            font=dict(family="Segoe UI", size=14, color=text_col),
        )
        st.plotly_chart(fig_room, use_container_width=True)

    with c2:
        st.markdown('<p class="section-heading">Property Types</p>', unsafe_allow_html=True)
        st.markdown('<p class="chart-caption">The six most common property types in Amsterdam. Apartments make up the large majority.</p>', unsafe_allow_html=True)
        prop_counts = df["property_type"].value_counts().head(6).reset_index()
        prop_counts.columns = ["Property Type", "Count"]
        fig_prop = px.bar(
            prop_counts, x="Count", y="Property Type", orientation="h",
            color="Count",
            color_continuous_scale=["#FFB3BF", "#FF385C", "#C0392B"],
            text="Count",
        )
        fig_prop.update_traces(textposition="outside", textfont_size=14)
        fig_prop.update_layout(
            showlegend=False, coloraxis_showscale=False,
            plot_bgcolor=plot_bg, paper_bgcolor=plot_bg,
            margin=dict(l=0, r=70, t=10, b=0), height=280,
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
        plot_bgcolor=plot_bg, paper_bgcolor=plot_bg,
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        xaxis=dict(showgrid=False, title="Price per night (€)",
                   title_font=dict(size=14, color=text_col),
                   tickfont=dict(size=13, color=text_col)),
        yaxis=dict(showgrid=True,
                   gridcolor="#E0E0E0" if not dark else "#3A3A3A",
                   title="Number of listings",
                   title_font=dict(size=14, color=text_col),
                   tickfont=dict(size=13, color=text_col)),
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1,
                    font=dict(size=14, color=text_col), title_text="Room type"),
        font=dict(family="Segoe UI", size=14, color=text_col),
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    nav_buttons(0)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Neighbourhoods
# ─────────────────────────────────────────────────────────────────────────────
elif active == 1:
    st.markdown('<p class="section-heading">Average Nightly Price by Neighbourhood</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-caption">The bars show the average price per night in each area of Amsterdam. Hover over a bar to see the exact figure.</p>', unsafe_allow_html=True)

    hood_price = (
        df.groupby("neighbourhood_cleansed")["price"]
        .mean()
        .reset_index()
        .rename(columns={"neighbourhood_cleansed": "Neighbourhood", "price": "Avg Price (€)"})
        .sort_values("Avg Price (€)", ascending=True)
    )
    fig_hp = px.bar(
        hood_price, x="Avg Price (€)", y="Neighbourhood", orientation="h",
        color="Avg Price (€)",
        color_continuous_scale=["#FFB3BF", "#FF385C", "#C0392B"],
        text=hood_price["Avg Price (€)"].apply(lambda x: f"€{x:.0f}"),
    )
    fig_hp.update_traces(textposition="outside", textfont_size=13)
    fig_hp.update_layout(
        showlegend=False, coloraxis_showscale=False,
        plot_bgcolor=plot_bg, paper_bgcolor=plot_bg,
        margin=dict(l=0, r=80, t=10, b=0), height=520,
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, title="", tickfont=dict(size=13, color=text_col)),
        font=dict(family="Segoe UI", size=13, color=text_col),
    )
    st.plotly_chart(fig_hp, use_container_width=True)

    st.markdown('<p class="section-heading">Average Review Score by Neighbourhood</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-caption">Shows how highly guests rated each neighbourhood on average. Scores are out of 100 — anything above 90 is considered excellent.</p>', unsafe_allow_html=True)

    hood_rating = (
        df.groupby("neighbourhood_cleansed")["review_scores_rating"]
        .mean()
        .reset_index()
        .rename(columns={"neighbourhood_cleansed": "Neighbourhood", "review_scores_rating": "Avg Rating"})
        .sort_values("Avg Rating", ascending=True)
    )
    fig_hr = px.bar(
        hood_rating, x="Avg Rating", y="Neighbourhood", orientation="h",
        color="Avg Rating",
        color_continuous_scale=["#FFB3BF", "#FF385C", "#C0392B"],
        text=hood_rating["Avg Rating"].apply(lambda x: f"{x:.1f}"),
    )
    fig_hr.update_traces(textposition="outside", textfont_size=13)
    fig_hr.update_layout(
        showlegend=False, coloraxis_showscale=False,
        plot_bgcolor=plot_bg, paper_bgcolor=plot_bg,
        margin=dict(l=0, r=60, t=10, b=0), height=520,
        xaxis=dict(showgrid=False, visible=False, range=[
            hood_rating["Avg Rating"].min() - 2,
            hood_rating["Avg Rating"].max() + 2,
        ]),
        yaxis=dict(showgrid=False, title="", tickfont=dict(size=13, color=text_col)),
        font=dict(family="Segoe UI", size=13, color=text_col),
    )
    st.plotly_chart(fig_hr, use_container_width=True)

    st.markdown('<p class="section-heading">Number of Listings by Neighbourhood</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-caption">How many listings are available in each area. More listings means more choice, but areas with fewer listings may feel quieter and more local.</p>', unsafe_allow_html=True)

    hood_count = (
        df.groupby("neighbourhood_cleansed")
        .size()
        .reset_index(name="Listings")
        .rename(columns={"neighbourhood_cleansed": "Neighbourhood"})
        .sort_values("Listings", ascending=True)
    )
    fig_hc = px.bar(
        hood_count, x="Listings", y="Neighbourhood", orientation="h",
        color="Listings",
        color_continuous_scale=["#FFB3BF", "#FF385C", "#C0392B"],
        text="Listings",
    )
    fig_hc.update_traces(textposition="outside", textfont_size=13)
    fig_hc.update_layout(
        showlegend=False, coloraxis_showscale=False,
        plot_bgcolor=plot_bg, paper_bgcolor=plot_bg,
        margin=dict(l=0, r=60, t=10, b=0), height=520,
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, title="", tickfont=dict(size=13, color=text_col)),
        font=dict(family="Segoe UI", size=13, color=text_col),
    )
    st.plotly_chart(fig_hc, use_container_width=True)

    nav_buttons(1)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Map
# ─────────────────────────────────────────────────────────────────────────────
elif active == 2:
    st.markdown('<p class="section-heading">Where Are the Listings?</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-caption">Each dot on the map is an Airbnb listing in Amsterdam. The colour shows the price per night — darker red means more expensive. Use the zoom buttons or scroll to explore the map.</p>', unsafe_allow_html=True)

    map_df = df[["latitude", "longitude", "price", "room_type",
                 "neighbourhood_cleansed", "review_scores_rating"]].dropna()
    map_df = map_df[map_df["price"] < 500]

    # Filter controls
    fc1, fc2 = st.columns(2)
    with fc1:
        room_options = ["All room types"] + sorted(map_df["room_type"].unique().tolist())
        selected_room = st.selectbox("Filter by room type", room_options,
                                     help="Show only listings of a particular type")
    with fc2:
        max_price = st.slider("Maximum price per night (€)", 50, 500,
                              300, step=10,
                              help="Drag to hide listings above this price")

    filtered = map_df[map_df["price"] <= max_price]
    if selected_room != "All room types":
        filtered = filtered[filtered["room_type"] == selected_room]

    st.markdown(
        f'<p class="chart-caption">Showing <strong>{len(filtered):,}</strong> listings after filters.</p>',
        unsafe_allow_html=True,
    )

    fig_map = px.scatter_mapbox(
        filtered,
        lat="latitude", lon="longitude",
        color="price",
        color_continuous_scale=["#FFB3BF", "#FF385C", "#8B0000"],
        size_max=8,
        zoom=11,
        center={"lat": 52.3676, "lon": 4.9041},
        mapbox_style="open-street-map",
        hover_data={
            "latitude": False,
            "longitude": False,
            "price": ":€.0f",
            "room_type": True,
            "neighbourhood_cleansed": True,
            "review_scores_rating": True,
        },
        labels={
            "price": "Price (€/night)",
            "room_type": "Room type",
            "neighbourhood_cleansed": "Neighbourhood",
            "review_scores_rating": "Review score",
        },
        height=560,
    )
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=plot_bg,
        font=dict(family="Segoe UI", size=13, color=text_col),
    )
    fig_map.update_coloraxes(
        colorbar=dict(
            title="Price (€)",
            tickfont=dict(size=13, color=text_col),
            titlefont=dict(size=14, color=text_col),
        )
    )
    st.plotly_chart(fig_map, use_container_width=True)

    nav_buttons(2)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Room Types
# ─────────────────────────────────────────────────────────────────────────────
elif active == 3:
    st.markdown('<p class="section-heading">What Type of Stay Is Right for You?</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:{base_body}; color:{sub_col}; margin-bottom:1rem; line-height:1.7;">'
        "Amsterdam listings come in three main types. An <strong>Entire home</strong> gives you full privacy — "
        "the whole property is yours. A <strong>Private room</strong> is your own bedroom inside someone's home, "
        "often with shared kitchen or living areas. A <strong>Shared room</strong> means sharing a sleeping space "
        "with others and is the most budget-friendly option."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown('<p class="section-heading">Average Price by Room Type</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-caption">Entire homes cost more on average but offer the most comfort and privacy. Private rooms offer a good balance of price and independence.</p>', unsafe_allow_html=True)

    room_price = (
        df.groupby("room_type")["price"]
        .mean()
        .reset_index()
        .rename(columns={"room_type": "Room Type", "price": "Avg Price (€)"})
        .sort_values("Avg Price (€)", ascending=False)
    )
    fig_rp = px.bar(
        room_price, x="Room Type", y="Avg Price (€)",
        color="Room Type",
        color_discrete_sequence=["#FF385C", "#333333", "#FF8CA0"],
        text=room_price["Avg Price (€)"].apply(lambda x: f"€{x:.0f}"),
    )
    fig_rp.update_traces(textposition="outside", textfont_size=14)
    fig_rp.update_layout(
        showlegend=False,
        plot_bgcolor=plot_bg, paper_bgcolor=plot_bg,
        margin=dict(l=0, r=0, t=20, b=0), height=300,
        xaxis=dict(showgrid=False, title="", tickfont=dict(size=14, color=text_col)),
        yaxis=dict(showgrid=True, gridcolor="#E0E0E0" if not dark else "#3A3A3A",
                   title="Avg price per night (€)",
                   title_font=dict(size=13, color=text_col),
                   tickfont=dict(size=13, color=text_col)),
        font=dict(family="Segoe UI", size=14, color=text_col),
    )
    st.plotly_chart(fig_rp, use_container_width=True)

    st.markdown('<p class="section-heading">Average Review Score by Room Type</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-caption">All three room types are rated highly by guests. Private rooms often score slightly higher on value because guests pay less for a similar quality of hospitality.</p>', unsafe_allow_html=True)

    room_rating = (
        df.groupby("room_type")["review_scores_rating"]
        .mean()
        .reset_index()
        .rename(columns={"room_type": "Room Type", "review_scores_rating": "Avg Rating"})
        .sort_values("Avg Rating", ascending=False)
    )
    fig_rr = px.bar(
        room_rating, x="Room Type", y="Avg Rating",
        color="Room Type",
        color_discrete_sequence=["#FF385C", "#333333", "#FF8CA0"],
        text=room_rating["Avg Rating"].apply(lambda x: f"{x:.1f}"),
    )
    fig_rr.update_traces(textposition="outside", textfont_size=14)
    fig_rr.update_layout(
        showlegend=False,
        plot_bgcolor=plot_bg, paper_bgcolor=plot_bg,
        margin=dict(l=0, r=0, t=20, b=0), height=300,
        xaxis=dict(showgrid=False, title="", tickfont=dict(size=14, color=text_col)),
        yaxis=dict(
            showgrid=True, gridcolor="#E0E0E0" if not dark else "#3A3A3A",
            title="Avg review score (out of 100)",
            title_font=dict(size=13, color=text_col),
            tickfont=dict(size=13, color=text_col),
            range=[room_rating["Avg Rating"].min() - 5, 100],
        ),
        font=dict(family="Segoe UI", size=14, color=text_col),
    )
    st.plotly_chart(fig_rr, use_container_width=True)

    st.markdown('<p class="section-heading">Review Sub-Scores by Room Type</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-caption">This chart breaks down guest ratings into six quality areas — cleanliness, location, value, and more — so you can see where each room type excels.</p>', unsafe_allow_html=True)

    sub_cols_map = {
        "review_scores_cleanliness": "Cleanliness",
        "review_scores_location":    "Location",
        "review_scores_value":       "Value",
        "review_scores_accuracy":    "Accuracy",
        "review_scores_checkin":     "Check-in",
        "review_scores_communication": "Communication",
    }
    available_sub = [c for c in sub_cols_map if c in df.columns]
    if available_sub:
        sub_df = (
            df.groupby("room_type")[available_sub]
            .mean()
            .reset_index()
            .rename(columns=sub_cols_map)
        )
        sub_melted = sub_df.melt(id_vars="room_type",
                                  var_name="Category",
                                  value_name="Score")
        sub_melted.rename(columns={"room_type": "Room Type"}, inplace=True)

        fig_sub = px.bar(
            sub_melted, x="Category", y="Score",
            color="Room Type",
            color_discrete_sequence=["#FF385C", "#333333", "#FF8CA0"],
            barmode="group",
            text=sub_melted["Score"].apply(lambda x: f"{x:.1f}"),
        )
        fig_sub.update_traces(textposition="outside", textfont_size=12)
        fig_sub.update_layout(
            plot_bgcolor=plot_bg, paper_bgcolor=plot_bg,
            margin=dict(l=0, r=0, t=20, b=0), height=360,
            xaxis=dict(showgrid=False, title="", tickfont=dict(size=13, color=text_col)),
            yaxis=dict(
                showgrid=True, gridcolor="#E0E0E0" if not dark else "#3A3A3A",
                title="Score (out of 10)",
                title_font=dict(size=13, color=text_col),
                tickfont=dict(size=13, color=text_col),
                range=[sub_melted["Score"].min() - 1, 10.5],
            ),
            legend=dict(font=dict(size=13, color=text_col), title_text="Room type"),
            font=dict(family="Segoe UI", size=13, color=text_col),
        )
        st.plotly_chart(fig_sub, use_container_width=True)

    st.markdown('<p class="section-heading">Availability Throughout the Year</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-caption">Shows on average how many days per year each room type is available to book. A higher number means more flexibility when planning your trip.</p>', unsafe_allow_html=True)

    room_avail = (
        df.groupby("room_type")["availability_365"]
        .mean()
        .reset_index()
        .rename(columns={"room_type": "Room Type", "availability_365": "Avg Days Available"})
        .sort_values("Avg Days Available", ascending=False)
    )
    fig_av = px.bar(
        room_avail, x="Room Type", y="Avg Days Available",
        color="Room Type",
        color_discrete_sequence=["#FF385C", "#333333", "#FF8CA0"],
        text=room_avail["Avg Days Available"].apply(lambda x: f"{x:.0f} days"),
    )
    fig_av.update_traces(textposition="outside", textfont_size=14)
    fig_av.update_layout(
        showlegend=False,
        plot_bgcolor=plot_bg, paper_bgcolor=plot_bg,
        margin=dict(l=0, r=0, t=20, b=0), height=300,
        xaxis=dict(showgrid=False, title="", tickfont=dict(size=14, color=text_col)),
        yaxis=dict(
            showgrid=True, gridcolor="#E0E0E0" if not dark else "#3A3A3A",
            title="Avg days available per year",
            title_font=dict(size=13, color=text_col),
            tickfont=dict(size=13, color=text_col),
        ),
        font=dict(family="Segoe UI", size=14, color=text_col),
    )
    st.plotly_chart(fig_av, use_container_width=True)

    nav_buttons(3)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f'<p style="text-align:center;color:{sub_col};font-size:{caption_sz};">'
    f"Airbnb Amsterdam · {len(df):,} listings · Built with Streamlit · Designed for people aged 65+"
    "</p>",
    unsafe_allow_html=True,
)