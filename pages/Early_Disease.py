import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(
    page_title="Early Disease Detection & Risk Warning - AgroTech",
    page_icon="🔬",
    layout="wide"
)

# Custom Styling
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
    .risk-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }
    .badge-low {
        background-color: #d8f3dc;
        color: #1b4332;
        padding: 5px 14px;
        border-radius: 18px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-moderate {
        background-color: #fff3e0;
        color: #e65100;
        padding: 5px 14px;
        border-radius: 18px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-high {
        background-color: #ffebee;
        color: #c62828;
        padding: 5px 14px;
        border-radius: 18px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🔬 Early Stage Disease Prevention & Risk Warning</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Rule-based agronomic early warning system assessing pathogen outbreak risks based on real-time micro-climate conditions.</div>", unsafe_allow_html=True)

# 1. Agronomic Knowledge Base
EARLY_DISEASE_KB = {
    "Rice": [
        {
            "name": "Rice Blast (Magnaporthe oryzae)",
            "temp_opt": (22, 28),
            "humidity_opt": 80,
            "rainfall_opt": 100,
            "advisory": "Avoid excessive nitrogen application. Maintain field water depth and apply Tricyclazole 75% WP at early lesion detection."
        },
        {
            "name": "Sheath Blight (Rhizoctonia solani)",
            "temp_opt": (28, 32),
            "humidity_opt": 85,
            "rainfall_opt": 150,
            "advisory": "Ensure proper plant spacing for air flow. Apply Hexaconazole 5% EC or Validamycin 3% L if humidity persists."
        },
        {
            "name": "Bacterial Leaf Blight (Xanthomonas oryzae)",
            "temp_opt": (25, 34),
            "humidity_opt": 70,
            "rainfall_opt": 80,
            "advisory": "Avoid field flooding from infected channels. Spray Streptocycline (0.15 g/L) + Copper Oxychloride (2 g/L)."
        }
    ],
    "Wheat": [
        {
            "name": "Stripe / Leaf Rust (Puccinia striiformis)",
            "temp_opt": (15, 22),
            "humidity_opt": 75,
            "rainfall_opt": 40,
            "advisory": "Inspect lower canopy foliage regularly. Apply Propiconazole 25% EC at first yellow rust pustule emergence."
        },
        {
            "name": "Powdery Mildew (Blumeria graminis)",
            "temp_opt": (15, 22),
            "humidity_opt": 70,
            "rainfall_opt": 20,
            "advisory": "Reduce canopy density. Apply Wettable Sulfur 80% WP or Triadimefon 25% WP."
        },
        {
            "name": "Loose Smut (Ustilago tritici)",
            "temp_opt": (18, 24),
            "humidity_opt": 60,
            "rainfall_opt": 30,
            "advisory": "Use certified disease-free seed. Treat seeds with Carboxin 75% WP or Carbendazim prior to sowing."
        }
    ],
    "Maize": [
        {
            "name": "Northern Corn Leaf Blight (Exserohilum turcicum)",
            "temp_opt": (18, 27),
            "humidity_opt": 80,
            "rainfall_opt": 70,
            "advisory": "Rotate crops with non-graminaceous species. Apply Mancozeb 75% WP or Azoxystrobin on early leaf lesions."
        },
        {
            "name": "Common Rust (Puccinia sorghi)",
            "temp_opt": (16, 25),
            "humidity_opt": 85,
            "rainfall_opt": 50,
            "advisory": "Plant resistant hybrids. Spray Hexaconazole 5% EC if rust coverage exceeds 5% of leaf area."
        }
    ],
    "Cotton": [
        {
            "name": "Bacterial Blight / Angular Leaf Spot",
            "temp_opt": (28, 36),
            "humidity_opt": 75,
            "rainfall_opt": 80,
            "advisory": "Delint seeds with acid treatment. Spray Copper Oxychloride 50% WP + Streptocycline."
        },
        {
            "name": "Fusarium Wilt (Fusarium oxysporum)",
            "temp_opt": (25, 32),
            "humidity_opt": 55,
            "rainfall_opt": 60,
            "advisory": "Drench soil with Carbendazim 50% WP (1 g/L). Practice crop rotation and soil solarization."
        }
    ],
    "Tomato": [
        {
            "name": "Early Blight (Alternaria solani)",
            "temp_opt": (24, 30),
            "humidity_opt": 80,
            "rainfall_opt": 60,
            "advisory": "Remove lower infected leaves. Apply Chlorothalonil 75% WP or Mancozeb 75% WP at 10-day intervals."
        },
        {
            "name": "Late Blight (Phytophthora infestans)",
            "temp_opt": (15, 22),
            "humidity_opt": 85,
            "rainfall_opt": 100,
            "advisory": "Critical threat during cool, wet weather! Apply Metalaxyl + Mancozeb or Cymoxanil immediately."
        }
    ],
    "Potato": [
        {
            "name": "Late Blight (Phytophthora infestans)",
            "temp_opt": (12, 22),
            "humidity_opt": 85,
            "rainfall_opt": 90,
            "advisory": "High risk in cool humid weather. Apply prophylactic spray of Mancozeb 75% WP followed by Dimethomorph."
        },
        {
            "name": "Black Scurf & Early Blight",
            "temp_opt": (20, 28),
            "humidity_opt": 75,
            "rainfall_opt": 50,
            "advisory": "Treat seed tubers with Boric Acid 3% or Trichoderma viride prior to planting."
        }
    ]
}

# 2. Risk Scoring Logic
def calculate_disease_risk(temp, humidity, rainfall, disease_rule):
    """
    Computes disease risk score (0-100%) based on environmental proximity.
    """
    t_min, t_max = disease_rule["temp_opt"]
    mid_temp = (t_min + t_max) / 2.0
    
    # Temperature Score
    if t_min <= temp <= t_max:
        s_temp = 1.0
    else:
        dist = abs(temp - mid_temp)
        s_temp = max(0.0, 1.0 - (dist / 14.0))
        
    # Humidity Score
    h_opt = disease_rule["humidity_opt"]
    s_hum = min(1.0, max(0.0, humidity / float(h_opt)))
    
    # Rainfall Score
    r_opt = disease_rule["rainfall_opt"]
    s_rain = min(1.0, max(0.0, rainfall / float(r_opt)))
    
    # Weighted Risk Index
    risk_index = (0.40 * s_temp + 0.35 * s_hum + 0.25 * s_rain) * 100.0
    return round(risk_index, 1)

# Expander Guide
with st.expander("ℹ️ How Early Disease Risk Assessment Works"):
    st.write("""
        This early warning tool evaluates environmental micro-climate triggers before visual symptoms develop on leaves:
        - **Temperature Favorability (40% Weight):** Measures closeness to the pathogen's optimal sporulation temperature window.
        - **Relative Humidity (35% Weight):** High humidity fosters fungal spore germination and bacterial leaf multiplication.
        - **Recent Rainfall (25% Weight):** Free moisture on leaf surfaces accelerates spore splash dispersion.
    """)

# UI Layout
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("### ⛅ Current Field Weather Parameters")
    
    crop_choice = st.selectbox(
        "Select Target Crop *",
        options=list(EARLY_DISEASE_KB.keys()),
        index=0,
        help="Choose the crop you want to evaluate."
    )
    
    temp_input = st.slider(
        "Current Temperature (°C)",
        min_value=10.0, max_value=45.0, value=25.0, step=0.5,
        help="Ambient temperature recorded in the field."
    )
    
    hum_input = st.slider(
        "Relative Humidity (%)",
        min_value=20.0, max_value=95.0, value=60.0, step=1.0,
        help="Relative atmospheric humidity level."
    )
    
    rain_input = st.slider(
        "Recent Rainfall (mm)",
        min_value=0.0, max_value=300.0, value=50.0, step=5.0,
        help="Cumulative rainfall recorded over the past 7 days."
    )
    
    assess_button = st.button("🔬 Assess Disease Risk", type="primary", use_container_width=True)

with col_right:
    st.markdown(f"### 🛡️ Disease Risk Profile: {crop_choice}")
    
    if assess_button or 'assessed_disease' in st.session_state:
        st.session_state['assessed_disease'] = True
        
        diseases = EARLY_DISEASE_KB[crop_choice]
        results = []
        
        for d in diseases:
            score = calculate_disease_risk(temp_input, hum_input, rain_input, d)
            
            if score >= 70.0:
                level = "HIGH"
                badge_class = "badge-high"
                badge_text = "🔴 HIGH RISK ALERT"
            elif score >= 35.0:
                level = "MODERATE"
                badge_class = "badge-moderate"
                badge_text = "🟡 MODERATE RISK"
            else:
                level = "LOW"
                badge_class = "badge-low"
                badge_text = "🟢 LOW RISK"
                
            results.append({
                "disease": d["name"],
                "score": score,
                "level": level,
                "badge_class": badge_class,
                "badge_text": badge_text,
                "advisory": d["advisory"]
            })
            
        # Display Risk Cards
        for res in results:
            st.markdown(f"""
                <div class="risk-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 1.15rem; font-weight: 700; color: #1b4332;">{res['disease']}</span>
                        <span class="{res['badge_class']}">{res['badge_text']}</span>
                    </div>
                    <div style="font-size: 0.95rem; color: #444; margin-bottom: 6px;">
                        Calculated Outbreak Risk: <strong>{res['score']}%</strong>
                    </div>
                    <div style="background-color: #f1f3f5; padding: 10px; border-radius: 8px; font-size: 0.9rem; color: #212529;">
                        💡 <strong>Agronomic Advisory:</strong> {res['advisory']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        st.divider()
        
        # Risk Comparison Bar Chart
        st.markdown("#### 📊 Pathogen Risk Score Comparison")
        chart_df = pd.DataFrame({
            "Disease": [r["disease"].split(" (")[0] for r in results],
            "Risk Score (%)": [r["score"] for r in results]
        })
        
        fig, ax = plt.subplots(figsize=(7, 3.5))
        bars = ax.barh(chart_df["Disease"], chart_df["Risk Score (%)"], color="#2d6a4f")
        ax.set_xlabel("Outbreak Risk Score (%)", fontsize=10, fontweight='bold', color='#1b4332')
        ax.set_xlim(0, 100)
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        
        # Color bar based on score
        for bar, score in zip(bars, chart_df["Risk Score (%)"]):
            if score >= 70:
                bar.set_color("#c62828")
            elif score >= 35:
                bar.set_color("#e65100")
            else:
                bar.set_color("#2e7d32")
                
        plt.tight_layout()
        st.pyplot(fig)
        
    else:
        st.info("👈 Select a crop and weather conditions on the left, then click **Assess Disease Risk**.")
