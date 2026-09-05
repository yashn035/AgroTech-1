import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(
    page_title="District Yield Insights - AgroTech",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS Styling
st.markdown("""
    <style>
    .main-header {
        color: #1b4332;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #40916c;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }
    .metric-num {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1b4332;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #666666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🌾 District Crop Yield Estimator & Analytics</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Explore historical district-level crop harvest yields, production trends, and regional performance benchmarks across India (2015–2023).</div>", unsafe_allow_html=True)

# 1. Dataset Generator
STATE_DISTRICT_MAP = {
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"],
    "Maharashtra": ["Nashik", "Pune", "Nagpur", "Aurangabad", "Solapur"],
    "Uttar Pradesh": ["Varanasi", "Lucknow", "Agra", "Kanpur", "Prayagraj"],
    "Gujarat": ["Ahmedabad", "Surat", "Rajkot", "Vadodara", "Junagadh"],
    "Karnataka": ["Bengaluru Rural", "Belagavi", "Mysuru", "Hubballi", "Dharwad"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner"],
    "Madhya Pradesh": ["Indore", "Bhopal", "Ujjain", "Jabalpur", "Gwalior"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga"],
    "West Bengal": ["Hooghly", "Burdwan", "Nadia", "Murshidabad", "Birbhum"],
    "Tamil Nadu": ["Coimbatore", "Madurai", "Salem", "Thanjavur", "Tiruchirappalli"]
}

TARGET_CROPS = [
    'rice', 'wheat', 'maize', 'cotton', 'sugarcane', 
    'groundnut', 'mango', 'banana', 'tomato', 'potato', 
    'onion', 'chickpea'
]

CROP_BASE_YIELDS = {
    'rice': 3800, 'wheat': 3600, 'maize': 3100, 'cotton': 1900,
    'sugarcane': 72000, 'groundnut': 2200, 'mango': 8800, 'banana': 44000,
    'tomato': 25000, 'potato': 23000, 'onion': 18000, 'chickpea': 1200
}

STATE_BOOSTS = {
    'Punjab': {'wheat': 1.35, 'rice': 1.25},
    'Uttar Pradesh': {'sugarcane': 1.3, 'wheat': 1.2, 'potato': 1.25},
    'Maharashtra': {'cotton': 1.25, 'onion': 1.3, 'sugarcane': 1.15},
    'West Bengal': {'rice': 1.35, 'potato': 1.2},
    'Tamil Nadu': {'banana': 1.3, 'rice': 1.2},
    'Gujarat': {'groundnut': 1.35, 'cotton': 1.25},
    'Madhya Pradesh': {'chickpea': 1.3, 'wheat': 1.15},
    'Karnataka': {'maize': 1.25, 'mango': 1.2}
}

@st.cache_data(show_spinner="Generating district yield dataset...")
def generate_yield_data():
    """
    Generates synthetic multi-year district yield dataset (2015-2023).
    """
    np.random.seed(42)
    rows = []
    
    for year in range(2015, 2024):
        year_trend = 1.0 + (year - 2015) * 0.018  # ~1.8% annual productivity growth
        
        for state, districts in STATE_DISTRICT_MAP.items():
            for district in districts:
                # Assign 4-6 crops per district for realism
                selected_crops = np.random.choice(TARGET_CROPS, size=5, replace=False)
                
                for crop in selected_crops:
                    base_y = CROP_BASE_YIELDS[crop]
                    state_mult = STATE_BOOSTS.get(state, {}).get(crop, 1.0)
                    
                    # Random district-level variation
                    dist_variation = np.random.normal(1.0, 0.08)
                    
                    # Calculate actual yield (kg/ha)
                    actual_yield = base_y * state_mult * year_trend * dist_variation
                    actual_yield = max(actual_yield, 100.0)
                    
                    # Random area harvested (5,000 to 75,000 hectares)
                    area_ha = np.random.uniform(5000, 75000)
                    
                    # Total production in tonnes: (yield_kg_ha * area_ha) / 1000
                    production_tonnes = (actual_yield * area_ha) / 1000.0
                    
                    rows.append({
                        "state": state,
                        "district": district,
                        "crop": crop.capitalize(),
                        "year": year,
                        "area_harvested": round(area_ha, 1),
                        "production": round(production_tonnes, 1),
                        "yield": round(actual_yield, 1)
                    })
                    
    df = pd.DataFrame(rows)
    return df

# Load cached data
df_raw = generate_yield_data()

# Sidebar Controls
st.sidebar.markdown("### 🎛️ Dashboard Filters")

all_states = sorted(df_raw["state"].unique())
selected_states = st.sidebar.multiselect("State(s)", options=all_states, default=all_states)

# Filter available districts based on state selection
if selected_states:
    avail_districts = sorted(df_raw[df_raw["state"].isin(selected_states)]["district"].unique())
else:
    avail_districts = sorted(df_raw["district"].unique())
    
selected_districts = st.sidebar.multiselect("District(s)", options=avail_districts, default=avail_districts)

all_crops = sorted(df_raw["crop"].unique())
selected_crops = st.sidebar.multiselect("Crop(s)", options=all_crops, default=all_crops)

min_year, max_year = int(df_raw["year"].min()), int(df_raw["year"].max())
selected_years = st.sidebar.slider("Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Filter Dataframe
df_filtered = df_raw[
    (df_raw["state"].isin(selected_states if selected_states else all_states)) &
    (df_raw["district"].isin(selected_districts if selected_districts else avail_districts)) &
    (df_raw["crop"].isin(selected_crops if selected_crops else all_crops)) &
    (df_raw["year"] >= selected_years[0]) &
    (df_raw["year"] <= selected_years[1])
]

# Expander Guide
with st.expander("ℹ️ How to Interpret District Yield Metrics"):
    st.write("""
        - **Total Production (Tonnes):** Sum of gross harvested crop weight across selected districts and timeframe.
        - **Average Yield (kg/ha):** Production efficiency metric calculated as `(Production in kg / Area Harvested in ha)`.
        - **Area Harvested (ha):** Total cultivated agricultural land area under active production.
        - **Productivity Growth:** Upward trend reflect regional agricultural technology adoption and improved seed varieties.
    """)

if df_filtered.empty:
    st.warning("⚠️ No yield data matching the selected filter criteria. Please broaden your sidebar selection.")
else:
    # 1. KPI Summary Section
    total_prod = df_filtered["production"].sum()
    avg_yield = df_filtered["yield"].mean()
    total_area = df_filtered["area_harvested"].sum()
    record_count = len(df_filtered)
    
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"<div class='metric-card'><div class='metric-label'>Total Production</div><div class='metric-num'>{total_prod:,.0f} <span style='font-size:1rem;'>T</span></div></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='metric-card'><div class='metric-label'>Average Yield</div><div class='metric-num'>{avg_yield:,.0f} <span style='font-size:1rem;'>kg/ha</span></div></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='metric-card'><div class='metric-label'>Total Area Harvested</div><div class='metric-num'>{total_area:,.0f} <span style='font-size:1rem;'>ha</span></div></div>", unsafe_allow_html=True)
    k4.markdown(f"<div class='metric-card'><div class='metric-label'>District Records</div><div class='metric-num'>{record_count:,}</div></div>", unsafe_allow_html=True)
    
    st.write("")
    st.divider()
    
    # 2. Time-Series Progression Chart
    col_chart1, col_chart2 = st.columns([1.2, 1], gap="large")
    
    with col_chart1:
        st.markdown("#### 📈 Multi-Year Production & Yield Trends")
        group_by_opt = st.radio("Group Time-Series By:", options=["Crop", "State"], horizontal=True)
        
        group_col = "crop" if group_by_opt == "Crop" else "state"
        ts_df = df_filtered.groupby(["year", group_col])["yield"].mean().reset_index()
        
        fig_ts, ax_ts = plt.subplots(figsize=(8, 4.5))
        for group_val, group_data in ts_df.groupby(group_col):
            ax_ts.plot(group_data["year"], group_data["yield"], marker='o', label=group_val, linewidth=2)
            
        ax_ts.set_xlabel("Year", fontsize=10, fontweight='bold', color='#1b4332')
        ax_ts.set_ylabel("Average Yield (kg/ha)", fontsize=10, fontweight='bold', color='#1b4332')
        ax_ts.grid(True, linestyle='--', alpha=0.5)
        ax_ts.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True, fontsize=8)
        
        plt.tight_layout()
        st.pyplot(fig_ts)
        
    with col_chart2:
        st.markdown("#### 🏆 Top 10 Districts by Average Yield")
        top_dist_df = df_filtered.groupby("district")["yield"].mean().reset_index()
        top_dist_df = top_dist_df.sort_values(by="yield", ascending=True).tail(10)
        
        fig_bar, ax_bar = plt.subplots(figsize=(7, 4.5))
        ax_bar.barh(top_dist_df["district"], top_dist_df["yield"], color='#2d6a4f')
        ax_bar.set_xlabel("Average Yield (kg/ha)", fontsize=10, fontweight='bold', color='#1b4332')
        ax_bar.grid(axis='x', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        st.pyplot(fig_bar)
        
    st.divider()
    
    # 3. Heatmap / Matrix View
    st.markdown("#### 🌡️ District-Crop Yield Intensity Heatmap Matrix (kg/ha)")
    matrix_df = df_filtered.pivot_table(index="district", columns="crop", values="yield", aggfunc="mean").fillna(0)
    
    st.dataframe(
        matrix_df.style.background_gradient(cmap="YlGn", axis=None).format("{:,.0f}"),
        use_container_width=True
    )
    
    st.write("")
    
    # 4. Filtered Data Table & Export
    st.markdown("#### 📋 District Yield Dataset & Export")
    
    col_tb1, col_tb2 = st.columns([3, 1])
    with col_tb1:
        st.caption(f"Showing **{len(df_filtered)}** matching records.")
    with col_tb2:
        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Filtered Data (CSV)",
            data=csv_data,
            file_name=f"agrotech_district_yields_{selected_years[0]}_{selected_years[1]}.csv",
            mime="text/csv",
            type="primary"
        )
        
    st.dataframe(
        df_filtered.sort_values(by=["year", "yield"], ascending=[False, False]),
        use_container_width=True,
        column_config={
            "state": "State",
            "district": "District",
            "crop": "Crop",
            "year": "Year",
            "area_harvested": st.column_config.NumberColumn("Area (ha)", format="%.1f ha"),
            "production": st.column_config.NumberColumn("Production (Tonnes)", format="%.1f T"),
            "yield": st.column_config.NumberColumn("Yield (kg/ha)", format="%.1f kg/ha")
        },
        hide_index=True
    )
