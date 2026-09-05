import os
import sys
import streamlit as st

# Ensure root directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils.translations import t, TRANSLATIONS
from utils.auth import login_user, register_user, logout_user, get_current_user

# Page Configuration
st.set_page_config(
    page_title="AgroTech - Next-Gen Agricultural Intelligence Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS
css_path = os.path.join("static", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar Header & Language Switcher
st.sidebar.image("https://img.icons8.com/color/96/sprout.png", width=60)
st.sidebar.title("AgroTech Hub")

# Language Selector
lang_choice = st.sidebar.selectbox(
    "🌐 Choose Language / भाषा चुनें",
    options=["English", "हिंदी (Hindi)"],
    index=0 if st.session_state.get("language", "en") == "en" else 1
)
lang = "en" if "English" in lang_choice else "hi"
st.session_state["language"] = lang

st.sidebar.divider()

# Authentication Sidebar Section
current_user = get_current_user()

if current_user:
    st.sidebar.success(f"🟢 {t('logged_in_as', lang)}: **{current_user}**")
    if st.sidebar.button(t("logout", lang), key="btn_logout", type="secondary"):
        logout_user()
        st.rerun()
else:
    st.sidebar.markdown(f"### {t('auth_header', lang)}")
    auth_mode = st.sidebar.radio("Account Mode:", [t("login", lang), t("signup", lang)], horizontal=True)
    
    with st.sidebar.form("auth_form"):
        user_input = st.text_input(t("username", lang))
        pass_input = st.text_input(t("password", lang), type="password")
        submit_auth = st.form_submit_button(t("login", lang) if auth_mode == t("login", lang) else t("signup", lang))
        
        if submit_auth:
            if auth_mode == t("login", lang):
                ok, msg = login_user(user_input, pass_input)
                if ok:
                    st.sidebar.success(msg)
                    st.rerun()
                else:
                    st.sidebar.error(msg)
            else:
                ok, msg = register_user(user_input, pass_input)
                if ok:
                    st.sidebar.success(msg)
                else:
                    st.sidebar.error(msg)

st.sidebar.divider()

# Navigation Selection
st.sidebar.markdown("### 📌 Navigation")
selected_feature = st.sidebar.radio(
    "Choose a Module:",
    [
        t("nav_home", lang),
        t("nav_decision", lang),
        t("nav_copilot", lang),
        t("nav_disease", lang),
        t("nav_market", lang),
        t("nav_crop", lang),
        t("nav_yield", lang),
        t("nav_early", lang)
    ]
)

# Navigation Redirects
if selected_feature == t("nav_decision", lang):
    st.switch_page("pages/decision_engine.py")
elif selected_feature == t("nav_copilot", lang):
    st.switch_page("pages/copilot.py")
elif selected_feature == t("nav_disease", lang):
    st.switch_page("pages/disease_detection.py")
elif selected_feature == t("nav_market", lang):
    st.switch_page("pages/market_price.py")
elif selected_feature == t("nav_crop", lang):
    st.switch_page("pages/crop_recommendation.py")
elif selected_feature == t("nav_yield", lang):
    st.switch_page("pages/district_yield.py")
elif selected_feature == t("nav_early", lang):
    st.switch_page("pages/early_disease.py")
else:
    # Main Dashboard Hero
    st.markdown(f"""
        <div class="hero-container">
            <div class="hero-title">{t('app_title', lang)}</div>
            <div class="hero-subtitle">
                {t('app_subtitle', lang)}
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("## ⚡ Live Modules")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown(f"""
            <div class="feature-card">
                <span class="badge-live">{t('live_badge', lang)}</span>
                <div class="feature-title" style="margin-top: 10px;">🚜 {t('nav_decision', lang)}</div>
                <p style="color: #555; font-size: 0.95rem;">
                    Central intelligence dashboard synthesizing soil nutrients, micro-weather, plant disease status, and Mandi price trends into a Personalised Farm Action Plan.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"{t('nav_decision', lang)} ➔", key="btn_decision", type="primary"):
            st.switch_page("pages/decision_engine.py")

        st.write("")
        st.markdown(f"""
            <div class="feature-card">
                <span class="badge-live">{t('live_badge', lang)}</span>
                <div class="feature-title" style="margin-top: 10px;">🤖 {t('nav_copilot', lang)}</div>
                <p style="color: #555; font-size: 0.95rem;">
                    RAG-powered AI chatbot assistant providing instant responses to crop care, disease control, soil fertilizing, and Mandi price queries.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"{t('nav_copilot', lang)} ➔", key="btn_copilot"):
            st.switch_page("pages/copilot.py")

        st.write("")
        st.markdown(f"""
            <div class="feature-card">
                <span class="badge-live">{t('live_badge', lang)}</span>
                <div class="feature-title" style="margin-top: 10px;">🌿 {t('nav_disease', lang)}</div>
                <p style="color: #555; font-size: 0.95rem;">
                    Diagnose 30 leaf disease classes across 5 crop species using deep learning Keras models and paired pesticide dosages.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"{t('nav_disease', lang)} ➔", key="btn_disease"):
            st.switch_page("pages/disease_detection.py")
            
        st.write("")
        st.markdown(f"""
            <div class="feature-card">
                <span class="badge-live">{t('live_badge', lang)}</span>
                <div class="feature-title" style="margin-top: 10px;">📊 {t('nav_market', lang)}</div>
                <p style="color: #555; font-size: 0.95rem;">
                    Query real-time Indian Mandi arrival prices directly from data.gov.in REST APIs.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"{t('nav_market', lang)} ➔", key="btn_market"):
            st.switch_page("pages/market_price.py")

    with col2:
        st.markdown(f"""
            <div class="feature-card">
                <span class="badge-live">{t('live_badge', lang)}</span>
                <div class="feature-title" style="margin-top: 10px;">🌱 {t('nav_crop', lang)}</div>
                <p style="color: #555; font-size: 0.95rem;">
                    Random Forest ML classifier trained on real soil-climate datasets recommending crops based on agronomic suitability or expected profit per acre.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"{t('nav_crop', lang)} ➔", key="btn_crop"):
            st.switch_page("pages/crop_recommendation.py")
        
        st.write("")
        st.markdown(f"""
            <div class="feature-card">
                <span class="badge-live">{t('live_badge', lang)}</span>
                <div class="feature-title" style="margin-top: 10px;">🌾 {t('nav_yield', lang)}</div>
                <p style="color: #555; font-size: 0.95rem;">
                    District harvest yield analytics, multi-year progression (2015-2023), heatmaps, and CSV data export.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"{t('nav_yield', lang)} ➔", key="btn_yield"):
            st.switch_page("pages/district_yield.py")
        
        st.write("")
        st.markdown(f"""
            <div class="feature-card">
                <span class="badge-live">{t('live_badge', lang)}</span>
                <div class="feature-title" style="margin-top: 10px;">🔬 {t('nav_early', lang)}</div>
                <p style="color: #555; font-size: 0.95rem;">
                    Rule-based early disease warning system calculating pathogen outbreak risk scores based on micro-climate weather triggers.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"{t('nav_early', lang)} ➔", key="btn_early"):
            st.switch_page("pages/early_disease.py")

    st.divider()
    st.markdown("### 📊 System Specs")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Production Status", "100% Live & Containerized")
    m2.metric("AI Copilot", "Active RAG Assistant")
    m3.metric("Supported Languages", "English & हिंदी (Hindi)")
    m4.metric("Authentication", "Encrypted bcrypt / local JSON")
