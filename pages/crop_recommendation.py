import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Ensure root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.translations import t

# Page Configuration
st.set_page_config(
    page_title="Smart Crop Recommendation - AgroTech",
    page_icon="🌱",
    layout="wide"
)

# Load Custom CSS
css_path = os.path.join("static", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

lang = st.session_state.get("language", "en")

# Title & Subtitle
st.markdown(f"<h1 class='main-header'>🌱 {t('nav_crop', lang)}</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Select between agronomic soil suitability or expected net profit per acre to discover your optimal crop choice.</div>", unsafe_allow_html=True)

REAL_DATA_PATH = os.path.join("data", "crop_recommendation_real.csv")

# 1. Load Real Dataset
@st.cache_data(show_spinner=False)
def load_real_crop_data(csv_path=REAL_DATA_PATH):
    """Loads real soil and climate crop dataset."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Real crop dataset missing at '{csv_path}'.")
    df = pd.read_csv(csv_path)
    return df

# 2. Train & Cache Random Forest Model
@st.cache_resource(show_spinner="Training ML Model on Real Agronomic Dataset...")
def train_crop_model_real():
    """Trains Random Forest Classifier on real agronomic dataset."""
    df = load_real_crop_data()
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    feature_names = ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Temperature (°C)', 'Humidity (%)', 'pH Level', 'Rainfall (mm)']
    feature_importances = clf.feature_importances_
    
    return clf, accuracy, feature_names, feature_importances

model, test_accuracy, feature_names, feature_importances = train_crop_model_real()

# Agronomic Yields (Qtl/acre), Mandi Prices (₹/Qtl), Production Costs (₹/acre)
CROP_PROFIT_METRICS = {
    'rice':        {'yield_acre': 18,  'price_qtl': 2250, 'cost_acre': 15000, 'risk': 'Low'},
    'maize':       {'yield_acre': 22,  'price_qtl': 1950, 'cost_acre': 14000, 'risk': 'Low'},
    'chickpea':    {'yield_acre': 9,   'price_qtl': 5440, 'cost_acre': 10000, 'risk': 'Low'},
    'kidneybeans': {'yield_acre': 8,   'price_qtl': 6800, 'cost_acre': 12000, 'risk': 'Moderate'},
    'pigeonpeas':  {'yield_acre': 7,   'price_qtl': 7000, 'cost_acre': 11000, 'risk': 'Low'},
    'mothbeans':   {'yield_acre': 5,   'price_qtl': 5800, 'cost_acre': 8000,  'risk': 'Low'},
    'mungbean':    {'yield_acre': 6,   'price_qtl': 7200, 'cost_acre': 9000,  'risk': 'Low'},
    'blackgram':   {'yield_acre': 6,   'price_qtl': 6900, 'cost_acre': 9500,  'risk': 'Low'},
    'lentil':      {'yield_acre': 7,   'price_qtl': 6100, 'cost_acre': 10000, 'risk': 'Low'},
    'pomegranate': {'yield_acre': 45,  'price_qtl': 6500, 'cost_acre': 85000, 'risk': 'High'},
    'banana':      {'yield_acre': 170, 'price_qtl': 1400, 'cost_acre': 45000, 'risk': 'Moderate'},
    'mango':       {'yield_acre': 35,  'price_qtl': 3200, 'cost_acre': 30000, 'risk': 'Moderate'},
    'grapes':      {'yield_acre': 80,  'price_qtl': 4800, 'cost_acre': 110000,'risk': 'High'},
    'watermelon':  {'yield_acre': 120, 'price_qtl': 950,  'cost_acre': 25000, 'risk': 'Moderate'},
    'muskmelon':   {'yield_acre': 90,  'price_qtl': 1200, 'cost_acre': 22000, 'risk': 'Moderate'},
    'apple':       {'yield_acre': 60,  'price_qtl': 7500, 'cost_acre': 95000, 'risk': 'High'},
    'orange':      {'yield_acre': 55,  'price_qtl': 3500, 'cost_acre': 35000, 'risk': 'Moderate'},
    'papaya':      {'yield_acre': 140, 'price_qtl': 1600, 'cost_acre': 40000, 'risk': 'Moderate'},
    'coconut':     {'yield_acre': 50,  'price_qtl': 2800, 'cost_acre': 25000, 'risk': 'Low'},
    'cotton':      {'yield_acre': 9,   'price_qtl': 6800, 'cost_acre': 18000, 'risk': 'Moderate'},
    'jute':        {'yield_acre': 12,  'price_qtl': 4600, 'cost_acre': 16000, 'risk': 'Low'},
    'coffee':      {'yield_acre': 8,   'price_qtl': 18500,'cost_acre': 45000, 'risk': 'Moderate'}
}

# Mode Selection Toggle
rec_mode = st.radio(
    "Select Recommendation Strategy:",
    options=["🌱 Soil-Based Suitability", "💰 Profit-Based Return"],
    horizontal=True
)

st.write("")

# Layout: Sliders (Left Column), Visuals (Right Column)
col_input, col_output = st.columns([1, 1.2], gap="large")

with col_input:
    st.markdown(f"### 🎛️ Field Inputs ({lang.upper()})")
    
    n_val = st.slider(t("nitrogen", lang), min_value=0, max_value=140, value=50, step=1)
    p_val = st.slider(t("phosphorus", lang), min_value=5, max_value=145, value=50, step=1)
    k_val = st.slider(t("potassium", lang), min_value=5, max_value=205, value=50, step=1)
    temp_val = st.slider(t("temperature", lang), min_value=10.0, max_value=45.0, value=25.0, step=0.5)
    hum_val = st.slider(t("humidity", lang), min_value=20.0, max_value=95.0, value=60.0, step=0.5)
    ph_val = st.slider(t("ph", lang), min_value=3.5, max_value=9.5, value=6.5, step=0.1)
    rain_val = st.slider(t("rainfall", lang), min_value=20.0, max_value=300.0, value=100.0, step=1.0)
    
    recommend_button = st.button(t("btn_recommend", lang), type="primary", use_container_width=True)

with col_output:
    st.markdown("### 📊 Analysis & Recommendation")
    
    if recommend_button or 'crop_predicted' in st.session_state:
        st.session_state['crop_predicted'] = True
        
        input_data = np.array([[n_val, p_val, k_val, temp_val, hum_val, ph_val, rain_val]])
        probs = model.predict_proba(input_data)[0]
        classes = model.classes_
        
        if "Soil-Based" in rec_mode:
            # Mode A: Soil-Based Suitability
            top_idx = int(np.argmax(probs))
            best_crop = classes[top_idx]
            best_prob = probs[top_idx]
            
            st.markdown(f"""
                <div class="card-box" style="background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%); color: white;">
                    <div style="font-size: 0.9rem; text-transform: uppercase; opacity: 0.85;">{t('optimal_crop', lang)}</div>
                    <div style="font-size: 2.3rem; font-weight: 800; color: #b7e4c7; margin: 4px 0;">{best_crop.upper()}</div>
                    <div>{t('match_confidence', lang)}: <strong>{best_prob * 100:.1f}%</strong></div>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.markdown(f"<span class='badge-live'>🎯 {t('model_accuracy', lang)}: {test_accuracy * 100:.1f}%</span>", unsafe_allow_html=True)
            st.divider()
            
            # Probabilities chart
            st.markdown("#### Crop Match Probabilities")
            prob_df = pd.DataFrame({
                'Crop': [c.capitalize() for c in classes],
                'Probability (%)': [p * 100 for p in probs]
            }).sort_values(by='Probability (%)', ascending=True).tail(10)
            
            fig_prob, ax_prob = plt.subplots(figsize=(8, 4))
            ax_prob.barh(prob_df['Crop'], prob_df['Probability (%)'], color='#2d6a4f')
            ax_prob.set_xlabel('Probability (%)', fontsize=10, fontweight='bold', color='#1b4332')
            ax_prob.set_xlim(0, 100)
            ax_prob.grid(axis='x', linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig_prob)
            
        else:
            # Mode B: Profit-Based Return
            profit_rows = []
            for crop_name, prob_score in zip(classes, probs):
                pm = CROP_PROFIT_METRICS.get(crop_name.lower(), {'yield_acre': 10, 'price_qtl': 2500, 'cost_acre': 15000, 'risk': 'Moderate'})
                
                yield_acre = pm['yield_acre']
                price_qtl = pm['price_qtl']
                cost_acre = pm['cost_acre']
                risk_lvl = pm['risk']
                
                gross_rev = yield_acre * price_qtl
                expected_profit = gross_rev - cost_acre
                
                profit_rows.append({
                    'Crop': crop_name.capitalize(),
                    'Suitability (%)': round(prob_score * 100, 1),
                    'Expected Yield (Qtl/acre)': yield_acre,
                    'Mandi Price (₹/Qtl)': price_qtl,
                    'Production Cost (₹/acre)': cost_acre,
                    'Expected Profit (₹/acre)': expected_profit,
                    'Risk Level': risk_lvl
                })
                
            df_prof = pd.DataFrame(profit_rows).sort_values(by='Expected Profit (₹/acre)', ascending=False)
            top_profit_row = df_prof.iloc[0]
            
            st.markdown(f"""
                <div class="card-box" style="background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%); color: white;">
                    <div style="font-size: 0.95rem; text-transform: uppercase; opacity: 0.85;">🏆 Highest Profit Recommended Crop</div>
                    <div style="font-size: 2.3rem; font-weight: 800; color: #b7e4c7; margin: 4px 0;">{top_profit_row['Crop'].upper()}</div>
                    <div style="font-size: 1.15rem;">Expected Net Profit: <strong>₹{top_profit_row['Expected Profit (₹/acre)']:,.0f} / acre</strong></div>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.divider()
            
            st.markdown("#### 🏆 Ranked Crop Financial Return Table")
            st.dataframe(
                df_prof,
                use_container_width=True,
                column_config={
                    "Expected Profit (₹/acre)": st.column_config.NumberColumn(format="₹%d"),
                    "Production Cost (₹/acre)": st.column_config.NumberColumn(format="₹%d"),
                    "Mandi Price (₹/Qtl)": st.column_config.NumberColumn(format="₹%d"),
                    "Suitability (%)": st.column_config.NumberColumn(format="%.1f%%")
                },
                hide_index=True
            )
            
            st.caption("ℹ️ **Data Sources:** ML Suitability (Random Forest model), Mandi Prices (data.gov.in Mandi API), Cultivation Costs (ICAR benchmark estimates per acre).")
            
    else:
        st.info("👈 Adjust sliders on the left and click recommend button.")
