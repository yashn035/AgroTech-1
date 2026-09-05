"""
AgroTech AI Agricultural Copilot Page
Provides an interactive RAG-powered chat assistant interface for farmers with chat history,
pre-populated prompt chips, source citations, and clear history functionality.
"""

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
st.markdown(
    "<div class='sub-header'>Interactive RAG-powered Generative AI assistant providing real-time crop care, disease diagnosis, and Mandi market intelligence.</div>",
    unsafe_allow_html=True
)

# Initialize Session Chat History safely
if "copilot_messages" not in st.session_state:
    st.session_state["copilot_messages"] = [
        {
            "role": "assistant",
            "content": "👋 Namaste! I am your **AI Agricultural Copilot**. How can I help with your crop health, soil nutrients, plant disease control, or Mandi prices today?",
            "sources": []
        }
    ]

# Sidebar Controls & Example Prompts
st.sidebar.markdown("### ⚙️ Copilot Controls")
if st.sidebar.button("🗑️ Clear Chat History", type="secondary", use_container_width=True):
    st.session_state["copilot_messages"] = [
        {
            "role": "assistant",
            "content": "👋 Namaste! Chat history cleared. How can I assist you now?",
            "sources": []
        }
    ]
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("### 💡 Quick Example Questions")
example_prompts = [
    "How to treat Cauliflower Black Rot?",
    "What pesticide to spray for Sigatoka Leaf Spot?",
    "How does Nitrogen help in crop growth?",
    "What to do if there is high rainfall forecast?",
    "How to control Chilli Anthracnose?"
]

selected_prompt = None
for ep in example_prompts:
    if st.sidebar.button(f"❓ {ep}", use_container_width=True, help="Click to ask this question immediately"):
        selected_prompt = ep

# Display Chat History (safely bounded)
messages = st.session_state.get("copilot_messages", [])
for msg in messages:
    with st.chat_message(msg.get("role", "assistant")):
        st.markdown(msg.get("content", ""))
        if msg.get("sources"):
            with st.expander("📚 View Verified Knowledge Sources"):
                for src in msg["sources"]:
                    st.markdown(f"- {src}")

# Handle Input (Chat Input box or Sidebar Chip)
chat_input_val = st.chat_input("Ask a question about crop care, disease, weather, or mandi prices...")
raw_query = chat_input_val or selected_prompt
user_query = raw_query.strip() if raw_query else ""

if user_query:
    # Append & display user prompt
    st.session_state["copilot_messages"].append({"role": "user", "content": user_query, "sources": []})
    with st.chat_message("user"):
        st.markdown(user_query)
        
    # Generate RAG response with spinner and exception safety
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching agricultural knowledge base & synthesizing response..."):
            try:
                res = query_rag_copilot(user_query)
                ans = res.get("answer", "Unable to generate response at this time.")
                sources = res.get("sources", [])
                
                st.markdown(ans)
                if sources:
                    with st.expander("📚 View Verified Knowledge Sources"):
                        for src in sources:
                            st.markdown(f"- {src}")
                            
                st.session_state["copilot_messages"].append({
                    "role": "assistant",
                    "content": ans,
                    "sources": sources
                })
            except Exception as e:
                err_msg = "⚠️ An unexpected error occurred while processing your request. Please try asking again."
                st.error(err_msg)
                st.session_state["copilot_messages"].append({
                    "role": "assistant",
                    "content": err_msg,
                    "sources": []
                })

    # Limit chat history to max 20 messages to preserve UI responsiveness
    if len(st.session_state["copilot_messages"]) > 20:
        st.session_state["copilot_messages"] = st.session_state["copilot_messages"][-20:]
