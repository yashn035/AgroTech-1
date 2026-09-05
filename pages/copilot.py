import os
import sys
import streamlit as st

# Ensure root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.translations import t
from utils.rag_engine import query_rag_copilot

# Page Configuration
st.set_page_config(
    page_title="AI Agricultural Copilot - AgroTech",
    page_icon="🤖",
    layout="wide"
)

# Custom Styling
css_path = os.path.join("static", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

lang = st.session_state.get("language", "en")

# Title & Subtitle
st.markdown(f"<h1 class='main-header'>🤖 {t('nav_copilot', lang)}</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Interactive RAG-powered Generative AI assistant providing real-time crop care, disease diagnosis, and Mandi market intelligence.</div>", unsafe_allow_html=True)

# Initialize Chat History
if "copilot_messages" not in st.session_state:
    st.session_state.copilot_messages = [
        {
            "role": "assistant",
            "content": "👋 Namaste! I am your **AI Agricultural Copilot**. How can I help with your crops, soil, disease management, or market prices today?"
        }
    ]

# Sidebar Example Prompts
st.sidebar.markdown("### 💡 Example Prompts")
example_prompts = [
    "How to treat Cauliflower Black Rot?",
    "What pesticide to spray for Sigatoka Leaf Spot?",
    "How does Nitrogen help in crop growth?",
    "What to do if there is high rainfall forecast?",
    "How to control Chilli Anthracnose?"
]

selected_prompt = None
for ep in example_prompts:
    if st.sidebar.button(f"❓ {ep}", use_container_width=True):
        selected_prompt = ep

# Display Chat History
for msg in st.session_state.copilot_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("📚 View RAG Sources & Knowledge Context"):
                for src in msg["sources"]:
                    st.markdown(f"- {src}")

# Handle Input
user_query = st.chat_input("Ask a question about crop care, disease, weather, or mandi prices...") or selected_prompt

if user_query:
    # Append user prompt
    st.session_state.copilot_messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
        
    # Generate RAG response
    with st.chat_message("assistant"):
        with st.spinner("Searching agricultural knowledge base & synthesizing response..."):
            res = query_rag_copilot(user_query)
            ans = res["answer"]
            sources = res["sources"]
            
            st.markdown(ans)
            if sources:
                with st.expander("📚 View RAG Sources & Knowledge Context"):
                    for src in sources:
                        st.markdown(f"- {src}")
                        
            st.session_state.copilot_messages.append({
                "role": "assistant",
                "content": ans,
                "sources": sources
            })
