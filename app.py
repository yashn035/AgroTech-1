import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="AgroTech - Next-Gen Agricultural Intelligence Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Main Dashboard
st.markdown("""
    <style>
    .hero-container {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
        color: #ffffff;
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 24px rgba(27, 67, 50, 0.15);
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.92;
        max-width: 800px;
        line-height: 1.6;
    }
    .feature-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }
    .feature-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1b4332;
        margin-bottom: 0.5rem;
    }
    .badge-live {
        background-color: #2e7d32;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation Header
st.sidebar.image("https://img.icons8.com/color/96/sprout.png", width=60)
st.sidebar.title("AgroTech Hub")
st.sidebar.caption("AI-Powered Farming Ecosystem")

# Navigation Selection
st.sidebar.markdown("### 📌 Navigation")
selected_feature = st.sidebar.radio(
    "Choose a Module:",
    [
        "🏠 Home & Overview",
        "🌿 Disease Detection + Pesticide Guidance (LIVE)",
        "📊 Mandi Market Price Checker (LIVE)",
        "🌱 Smart Crop Recommendation (LIVE)",
        "🌾 District Crop Yield Estimator (LIVE)",
        "🔬 Early Stage Disease Prevention (LIVE)"
    ]
)

st.sidebar.divider()
st.sidebar.success("✅ **All 5 AgroTech Modules Are Fully Operational!**")

# Main Body Content based on selection
if selected_feature == "🌿 Disease Detection + Pesticide Guidance (LIVE)":
    st.switch_page("pages/disease_detection.py")
elif selected_feature == "📊 Mandi Market Price Checker (LIVE)":
    st.switch_page("pages/market_price.py")
elif selected_feature == "🌱 Smart Crop Recommendation (LIVE)":
    st.switch_page("pages/crop_recommendation.py")
elif selected_feature == "🌾 District Crop Yield Estimator (LIVE)":
    st.switch_page("pages/district_yield.py")
elif selected_feature == "🔬 Early Stage Disease Prevention (LIVE)":
    st.switch_page("pages/early_disease.py")
else:
    # Home Page Dashboard
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">🌾 AgroTech Platform</div>
            <div class="hero-subtitle">
                Empowering farmers and agricultural experts with AI-driven crop diagnostics, precise chemical treatment protocols, real-time market discovery, machine learning crop selection, and district yield analytics.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("## ⚡ Live Platform Modules")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <span class="badge-live">LIVE NOW</span>
                <div class="feature-title" style="margin-top: 10px;">🌿 Disease Detection & Pesticide Recommendation</div>
                <p style="color: #555; font-size: 0.95rem;">
                    Upload leaf photos to instantly diagnose 30 plant disease classes across Banana, Cauliflower, Chilli, Groundnut, and Radish. Automatically pairs diagnoses with dosage and dilution instructions.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Disease Detection ➔", key="btn_disease", type="primary"):
            st.switch_page("pages/disease_detection.py")
            
        st.write("")
        st.markdown("""
            <div class="feature-card">
                <span class="badge-live">LIVE NOW</span>
                <div class="feature-title" style="margin-top: 10px;">📊 Mandi Market Price Checker</div>
                <p style="color: #555; font-size: 0.95rem;">
                    Real-time market price integration using Government Mandi APIs (data.gov.in), tracking daily commodity prices, state-wise filters, and price trend metrics.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Market Price Checker ➔", key="btn_market"):
            st.switch_page("pages/market_price.py")

        st.write("")
        st.markdown("""
            <div class="feature-card">
                <span class="badge-live">LIVE NOW</span>
                <div class="feature-title" style="margin-top: 10px;">🌱 Smart Crop Recommendation</div>
                <p style="color: #555; font-size: 0.95rem;">
                    Random Forest ML model recommending the best crops to plant based on soil NPK ratios, pH level, temperature, humidity, and rainfall data.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Crop Recommendation ➔", key="btn_crop"):
            st.switch_page("pages/crop_recommendation.py")
        
    with col2:
        st.markdown("""
            <div class="feature-card">
                <span class="badge-live">LIVE NOW</span>
                <div class="feature-title" style="margin-top: 10px;">🌾 District Crop Yield Estimator</div>
                <p style="color: #555; font-size: 0.95rem;">
                    Predicts and analyzes crop harvest yield per hectare based on district agricultural history (2015-2023), yield heatmaps, and CSV exports.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch District Yield Estimator ➔", key="btn_yield"):
            st.switch_page("pages/district_yield.py")
        
        st.write("")
        st.markdown("""
            <div class="feature-card">
                <span class="badge-live">LIVE NOW</span>
                <div class="feature-title" style="margin-top: 10px;">🔬 Early Stage Disease Prevention</div>
                <p style="color: #555; font-size: 0.95rem;">
                    Agronomic early warning system predicting pathogen outbreak risks based on real-time micro-climate weather triggers (Temp, Humidity, Rainfall).
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Early Disease Prevention ➔", key="btn_early"):
            st.switch_page("pages/early_disease.py")

    st.divider()
    st.markdown("### 📊 System Status & Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Live Features", "5 / 5 Fully Live")
    m2.metric("Supported Crops", "12 Major Indian Crops")
    m3.metric("Disease Classes", "30 Image ML + 15 Weather Rules")
    m4.metric("Market Mandis", "Live API (data.gov.in)")
