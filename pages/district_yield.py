import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.translations import t

# Page Configuration
st.set_page_config(
    page_title="District Yield Insights - AgroTech",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS
css_path = os.path.join("static", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

lang = st.session_state.get("language", "en")

st.markdown(f"<h1 class='main-header'>🌾 {t('nav_yield', lang)}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-header'>{t('app_subtitle', lang)}</div>", unsafe_allow_html=True)

REAL_YIELD_CSV = os.path.join("data", "yield_data_real.csv")

@st.cache_data(show_spinner="Loading real district yield dataset...")
def load_real_yield_data(csv_path=REAL_YIELD_CSV):
    """Loads real district yield dataset."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Real yield dataset not found at '{csv_path}'.")
    df = pd.read_csv(csv_path)
    return df

df_raw = load_real_yield_data()

# Sidebar Controls
st.sidebar.markdown("### 🎛️ Dashboard Filters")
all_states = sorted(df_raw["state"].unique())
selected_states = st.sidebar.multiselect(t("state", lang), options=all_states, default=all_states)

if selected_states:
    avail_districts = sorted(df_raw[df_raw["state"].isin(selected_states)]["district"].unique())
else:
    avail_districts = sorted(df_raw["district"].unique())
    
selected_districts = st.sidebar.multiselect(t("district", lang), options=avail_districts, default=avail_districts)

all_crops = sorted(df_raw["crop"].unique())
selected_crops = st.sidebar.multiselect(t("commodity", lang), options=all_crops, default=all_crops)

min_year, max_year = int(df_raw["year"].min()), int(df_raw["year"].max())
selected_years = st.sidebar.slider("Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Filtering
df_filtered = df_raw[
    (df_raw["state"].isin(selected_states if selected_states else all_states)) &
    (df_raw["district"].isin(selected_districts if selected_districts else avail_districts)) &
    (df_raw["crop"].isin(selected_crops if selected_crops else all_crops)) &
    (df_raw["year"] >= selected_years[0]) &
    (df_raw["year"] <= selected_years[1])
]

if df_filtered.empty:
    st.warning("⚠️ No yield data matching selection.")
else:
    # Metrics
    total_prod = df_filtered["production"].sum()
    avg_yield = df_filtered["yield"].mean()
    total_area = df_filtered["area_harvested"].sum()
    record_count = len(df_filtered)
    
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"<div class='card-box'><div class='metric-label'>{t('total_production', lang)}</div><div class='metric-num'>{total_prod:,.0f} T</div></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='card-box'><div class='metric-label'>{t('avg_yield', lang)}</div><div class='metric-num'>{avg_yield:,.0f} kg/ha</div></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='card-box'><div class='metric-label'>{t('area_harvested', lang)}</div><div class='metric-num'>{total_area:,.0f} ha</div></div>", unsafe_allow_html=True)
    k4.markdown(f"<div class='card-box'><div class='metric-label'>{t('district_records', lang)}</div><div class='metric-num'>{record_count:,}</div></div>", unsafe_allow_html=True)
    
    st.write("")
    st.divider()
    
    # Time Series Chart
    col_c1, col_c2 = st.columns([1.2, 1], gap="large")
    with col_c1:
        st.markdown("#### 📈 Multi-Year Trends")
        group_by = st.radio("Group By:", options=["Crop", "State"], horizontal=True)
        g_col = "crop" if group_by == "Crop" else "state"
        
        ts_df = df_filtered.groupby(["year", g_col])["yield"].mean().reset_index()
        fig_ts, ax_ts = plt.subplots(figsize=(8, 4.5))
        for g_val, g_data in ts_df.groupby(g_col):
            ax_ts.plot(g_data["year"], g_data["yield"], marker='o', label=g_val, linewidth=2)
        ax_ts.set_xlabel("Year", fontsize=10, fontweight='bold')
        ax_ts.set_ylabel("Yield (kg/ha)", fontsize=10, fontweight='bold')
        ax_ts.grid(True, linestyle='--', alpha=0.5)
        ax_ts.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        plt.tight_layout()
        st.pyplot(fig_ts)
        
    with col_c2:
        st.markdown("#### 🏆 Top 10 Districts by Yield")
        top_d = df_filtered.groupby("district")["yield"].mean().reset_index().sort_values(by="yield").tail(10)
        fig_bar, ax_bar = plt.subplots(figsize=(7, 4.5))
        ax_bar.barh(top_d["district"], top_d["yield"], color='#2d6a4f')
        ax_bar.set_xlabel("Yield (kg/ha)", fontsize=10, fontweight='bold')
        ax_bar.grid(axis='x', linestyle='--', alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig_bar)
        
    st.divider()
    
    # Heatmap Matrix
    st.markdown("#### 🌡️ Yield Intensity Heatmap Matrix (kg/ha)")
    matrix_df = df_filtered.pivot_table(index="district", columns="crop", values="yield", aggfunc="mean").fillna(0)
    st.dataframe(matrix_df.style.background_gradient(cmap="YlGn", axis=None).format("{:,.0f}"), use_container_width=True)
    
    # Export & Table
    st.markdown("#### 📋 Data Table & CSV Export")
    csv_bytes = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export Filtered Data (CSV)", data=csv_bytes, file_name="agrotech_real_yields.csv", mime="text/csv", type="primary")
    st.dataframe(df_filtered.sort_values(by=["year", "yield"], ascending=[False, False]), use_container_width=True, hide_index=True)
