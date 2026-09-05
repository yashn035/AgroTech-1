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
st.markdown(f"<div class='sub-header'>{t('app_subtitle', lang)}</div>", unsafe_allow_html=True)

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
    """
    Trains Random Forest Classifier on real agronomic dataset.
    """
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

# Expander Guide
with st.expander("ℹ️ Data Source & ML Pipeline"):
    st.write("""
        - **Data Source:** Verified ICAR/Kaggle Real Soil-Climate Dataset (`data/crop_recommendation_real.csv`).
        - **Model:** Random Forest Classifier (100 Decision Trees).
        - **Evaluation:** Evaluated on stratified 80/20 train/test split.
    """)

# Layout
col_input, col_output = st.columns([1, 1], gap="large")

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
    st.markdown(f"### 📊 Results & Analysis")
    
    if recommend_button or 'crop_predicted' in st.session_state:
        st.session_state['crop_predicted'] = True
        
        input_data = np.array([[n_val, p_val, k_val, temp_val, hum_val, ph_val, rain_val]])
        probs = model.predict_proba(input_data)[0]
        classes = model.classes_
        
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
        st.markdown(f"<span class='badge-live'>🎯 {t('model_accuracy', lang)}: {test_accuracy * 100:.1f}% (Real Dataset)</span>", unsafe_allow_html=True)
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
        st.info("👈 Adjust sliders on the left and click recommend button.")
