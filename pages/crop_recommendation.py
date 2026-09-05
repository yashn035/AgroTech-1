import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Page Configuration
st.set_page_config(
    page_title="Smart Crop Recommendation - AgroTech",
    page_icon="🌱",
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
    .recommendation-card {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
        color: #ffffff;
        padding: 1.8rem;
        border-radius: 14px;
        box-shadow: 0 6px 20px rgba(27, 67, 50, 0.15);
        margin-bottom: 1.5rem;
    }
    .recommendation-title {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.85;
    }
    .recommendation-crop {
        font-size: 2.3rem;
        font-weight: 800;
        margin-top: 4px;
        margin-bottom: 4px;
        color: #b7e4c7;
    }
    .accuracy-badge {
        background: #d8f3dc;
        color: #1b4332;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
        margin-top: 6px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🌱 Smart Crop Recommendation Engine</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Enter your soil nutrients (N-P-K) and climate parameters to identify the optimal crop for your field.</div>", unsafe_allow_html=True)

TARGET_CROPS = [
    'rice', 'wheat', 'maize', 'cotton', 'sugarcane', 
    'groundnut', 'mango', 'banana', 'tomato', 'potato', 
    'onion', 'chickpea'
]

# 1. Synthetic Dataset Generator
def generate_crop_data(n_samples=2000):
    """
    Generates synthetic agricultural dataset with realistic conditional soil-climate distributions.
    """
    np.random.seed(42)
    samples_per_crop = n_samples // len(TARGET_CROPS)
    
    crop_profiles = {
        'rice':       {'N': (80, 15),  'P': (45, 10), 'K': (40, 8),  'temp': (24, 3), 'hum': (82, 5), 'ph': (6.4, 0.4), 'rain': (230, 25)},
        'wheat':      {'N': (115, 15), 'P': (60, 10), 'K': (40, 8),  'temp': (18, 3), 'hum': (60, 6), 'ph': (6.8, 0.4), 'rain': (130, 20)},
        'maize':      {'N': (90, 15),  'P': (50, 10), 'K': (25, 6),  'temp': (25, 4), 'hum': (65, 6), 'ph': (6.5, 0.4), 'rain': (90, 15)},
        'cotton':     {'N': (115, 12), 'P': (48, 8),  'K': (25, 5),  'temp': (30, 3), 'hum': (52, 6), 'ph': (7.0, 0.4), 'rain': (80, 15)},
        'sugarcane':  {'N': (100, 15), 'P': (32, 8),  'K': (55, 10), 'temp': (28, 3), 'hum': (82, 5), 'ph': (7.2, 0.5), 'rain': (200, 20)},
        'groundnut':  {'N': (28, 8),   'P': (50, 10), 'K': (25, 6),  'temp': (28, 3), 'hum': (58, 6), 'ph': (6.5, 0.4), 'rain': (75, 12)},
        'mango':      {'N': (28, 8),   'P': (28, 6),  'K': (38, 8),  'temp': (32, 3), 'hum': (58, 6), 'ph': (6.5, 0.4), 'rain': (120, 20)},
        'banana':     {'N': (105, 12), 'P': (82, 8),  'K': (55, 8),  'temp': (29, 2), 'hum': (84, 4), 'ph': (6.5, 0.4), 'rain': (200, 20)},
        'tomato':     {'N': (95, 12),  'P': (62, 8),  'K': (50, 8),  'temp': (23, 3), 'hum': (62, 6), 'ph': (6.5, 0.3), 'rain': (90, 15)},
        'potato':     {'N': (105, 12), 'P': (58, 8),  'K': (55, 8),  'temp': (17, 2), 'hum': (70, 5), 'ph': (5.8, 0.3), 'rain': (100, 15)},
        'onion':      {'N': (75, 10),  'P': (48, 8),  'K': (25, 6),  'temp': (20, 3), 'hum': (60, 6), 'ph': (6.6, 0.3), 'rain': (65, 10)},
        'chickpea':   {'N': (35, 8),   'P': (68, 8),  'K': (85, 8),  'temp': (21, 3), 'hum': (32, 5), 'ph': (7.2, 0.4), 'rain': (55, 10)},
    }

    data_rows = []
    for crop in TARGET_CROPS:
        prof = crop_profiles[crop]
        for _ in range(samples_per_crop):
            n = np.clip(np.random.normal(prof['N'][0], prof['N'][1]), 0, 140)
            p = np.clip(np.random.normal(prof['P'][0], prof['P'][1]), 5, 145)
            k = np.clip(np.random.normal(prof['K'][0], prof['K'][1]), 5, 205)
            t = np.clip(np.random.normal(prof['temp'][0], prof['temp'][1]), 10, 45)
            h = np.clip(np.random.normal(prof['hum'][0], prof['hum'][1]), 20, 95)
            ph = np.clip(np.random.normal(prof['ph'][0], prof['ph'][1]), 3.5, 9.5)
            r = np.clip(np.random.normal(prof['rain'][0], prof['rain'][1]), 20, 300)
            
            data_rows.append({
                'N': n, 'P': p, 'K': k,
                'temperature': t, 'humidity': h,
                'ph': ph, 'rainfall': r,
                'label': crop
            })
            
    df = pd.DataFrame(data_rows)
    return df

# 2. Train & Cache Random Forest Model
@st.cache_resource(show_spinner="Training Machine Learning Crop Model...")
def train_crop_model():
    """
    Trains and caches the Random Forest Classifier for crop recommendation.
    """
    df = generate_crop_data(n_samples=2400)
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

# Load Model
model, test_accuracy, feature_names, feature_importances = train_crop_model()

# Expander: How it Works
with st.expander("ℹ️ How the Crop Recommendation Model Works"):
    st.write("""
        This machine learning system utilizes a **Random Forest Classifier** trained on high-dimensional agricultural soil and environmental data.
        - **Soil Parameters:** Nitrogen (N), Phosphorus (P), Potassium (K), and pH balance.
        - **Climate Factors:** Ambient Temperature, Humidity percentage, and Annual Rainfall.
        The algorithm calculates class probability distributions across all 12 candidate crops and highlights key feature importances.
    """)

# UI Layout: Sliders (Left Column), Results & Visuals (Right Column)
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.markdown("### 🎛️ Field & Climate Parameters")
    
    n_val = st.slider("Nitrogen (N) ratio in soil (mg/kg)", min_value=0, max_value=140, value=50, step=1)
    p_val = st.slider("Phosphorus (P) ratio in soil (mg/kg)", min_value=5, max_value=145, value=50, step=1)
    k_val = st.slider("Potassium (K) ratio in soil (mg/kg)", min_value=5, max_value=205, value=50, step=1)
    temp_val = st.slider("Average Temperature (°C)", min_value=10.0, max_value=45.0, value=25.0, step=0.5)
    hum_val = st.slider("Relative Humidity (%)", min_value=20.0, max_value=95.0, value=60.0, step=0.5)
    ph_val = st.slider("Soil pH level", min_value=3.5, max_value=9.5, value=6.5, step=0.1)
    rain_val = st.slider("Rainfall (mm)", min_value=20.0, max_value=300.0, value=100.0, step=1.0)
    
    recommend_button = st.button("🌱 Recommend Optimal Crop", type="primary", use_container_width=True)

with col_output:
    st.markdown("### 📊 Recommendation & Insights")
    
    if recommend_button or 'crop_predicted' in st.session_state:
        st.session_state['crop_predicted'] = True
        
        # Prepare input sample
        input_data = np.array([[n_val, p_val, k_val, temp_val, hum_val, ph_val, rain_val]])
        
        # Inference
        probs = model.predict_proba(input_data)[0]
        classes = model.classes_
        
        # Top Crop
        top_idx = int(np.argmax(probs))
        best_crop = classes[top_idx]
        best_prob = probs[top_idx]
        
        # Display Top Crop Banner
        st.markdown(f"""
            <div class="recommendation-card">
                <div class="recommendation-title">✅ Optimal Recommended Crop</div>
                <div class="recommendation-crop">{best_crop.upper()}</div>
                <div style="font-size: 1.05rem;">Match Confidence: <strong>{best_prob * 100:.1f}%</strong></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<span class='accuracy-badge'>🎯 ML Model Test Accuracy: {test_accuracy * 100:.1f}%</span>", unsafe_allow_html=True)
        st.write("")
        st.divider()
        
        # 1. Probability Bar Chart
        st.markdown("#### 1. Crop Match Probabilities")
        prob_df = pd.DataFrame({
            'Crop': [c.capitalize() for c in classes],
            'Probability (%)': [p * 100 for p in probs]
        }).sort_values(by='Probability (%)', ascending=True)
        
        fig_prob, ax_prob = plt.subplots(figsize=(8, 4))
        bars = ax_prob.barh(prob_df['Crop'], prob_df['Probability (%)'], color='#2d6a4f')
        ax_prob.set_xlabel('Probability (%)', fontsize=10, fontweight='bold', color='#1b4332')
        ax_prob.set_xlim(0, 100)
        ax_prob.grid(axis='x', linestyle='--', alpha=0.5)
        
        # Highlight top bar
        bars[-1].set_color('#1b4332')
        
        plt.tight_layout()
        st.pyplot(fig_prob)
        
        # 2. Feature Importance Horizontal Bar Chart
        st.markdown("#### 2. Soil & Climate Feature Influence")
        imp_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance (%)': feature_importances * 100
        }).sort_values(by='Importance (%)', ascending=True)
        
        fig_imp, ax_imp = plt.subplots(figsize=(8, 3.5))
        ax_imp.barh(imp_df['Feature'], imp_df['Importance (%)'], color='#52b788')
        ax_imp.set_xlabel('Importance (%)', fontsize=10, fontweight='bold', color='#1b4332')
        ax_imp.grid(axis='x', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        st.pyplot(fig_imp)
    else:
        st.info("👈 Adjust soil & climate parameters on the left and click **Recommend Optimal Crop**.")
