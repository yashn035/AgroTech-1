import os
import sys
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Ensure root directory is in sys.path and load environment variables
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from utils.market_api import fetch_market_prices

# Page Configuration
st.set_page_config(
    page_title="Mandi Market Price Checker - AgroTech",
    page_icon="📊",
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
    .form-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .metric-num {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1b4332;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #666666;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>📊 Mandi Market Price Checker</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Fetch live crop arrival prices directly from official Indian agricultural mandi APIs (data.gov.in).</div>", unsafe_allow_html=True)

# Retrieve API key safely from environment or secrets
api_key = os.getenv("MANDI_API_KEY")
if not api_key:
    try:
        if "MANDI_API_KEY" in st.secrets:
            api_key = st.secrets["MANDI_API_KEY"]
    except Exception:
        api_key = None

# API Key Validation Notice
has_key = bool(api_key and api_key.strip() and api_key != "your_key_here")

if not has_key:
    st.error(
        "🔑 **MANDI_API_KEY Not Configured!**\n\n"
        "To query live mandi market data from data.gov.in, set `MANDI_API_KEY` in your `.env` file or environment variables.\n"
        "*(You can obtain a free API key at [data.gov.in](https://data.gov.in/))*"
    )
    st.info("💡 **Demo Preview Available:** You can test the search form with sample preview data below.")

# Filter Search Form
st.markdown("### 🔍 Search Commodity Prices")
with st.form("market_search_form"):
    col1, col2 = st.columns(2)
    with col1:
        state_input = st.text_input("State *", value="Maharashtra", help="Required. E.g., Maharashtra, Punjab, Uttar Pradesh")
        district_input = st.text_input("District (Optional)", value="", help="Optional. E.g., Pune, Nashik, Ludhiana")
    with col2:
        commodity_input = st.text_input("Commodity *", value="Onion", help="Required. E.g., Onion, Potato, Wheat, Tomato")
        market_input = st.text_input("Market (Optional)", value="", help="Optional. E.g., Pune, Lasalgaon")
        
    submit_button = st.form_submit_button("Fetch Market Prices ➔", type="primary", use_container_width=True)

if submit_button:
    # Form Validation
    state = state_input.strip()
    commodity = commodity_input.strip()
    district = district_input.strip()
    market = market_input.strip()
    
    if not state or not commodity:
        st.warning("⚠️ Please provide both **State** and **Commodity** fields.")
    else:
        records = []
        fetch_error = None
        
        if has_key:
            try:
                with st.spinner(f"Fetching live Mandi price records for '{commodity}' in '{state}'..."):
                    records = fetch_market_prices(
                        api_key=api_key,
                        state=state,
                        district=district,
                        market=market,
                        commodity=commodity
                    )
            except Exception as e:
                fetch_error = str(e)
        else:
            # Simulated sample dataset for demonstration when key is missing
            st.info("ℹ️ Displaying simulated sample records for demonstration...")
            records = [
                {
                    "state": state, "district": district or "Pune", "market": market or "Pune (F&V)",
                    "commodity": commodity, "min_price": "1200", "max_price": "2400",
                    "modal_price": "1850", "arrival_date": "05/09/2026"
                },
                {
                    "state": state, "district": district or "Nashik", "market": market or "Lasalgaon",
                    "commodity": commodity, "min_price": "1100", "max_price": "2200",
                    "modal_price": "1650", "arrival_date": "05/09/2026"
                },
                {
                    "state": state, "district": district or "Ahmednagar", "market": market or "Rahuri",
                    "commodity": commodity, "min_price": "1350", "max_price": "2650",
                    "modal_price": "2100", "arrival_date": "05/09/2026"
                }
            ]

        if fetch_error:
            st.error(f"❌ **API Error:** {fetch_error}")
        elif not records:
            st.warning("⚠️ No price data found for this selection today. Try broadening your search filters.")
        else:
            st.success(f"✅ Found **{len(records)}** mandi price record(s).")
            
            # Convert records to Pandas DataFrame
            df = pd.DataFrame(records)
            
            # Ensure standard required columns exist
            target_cols = ["state", "district", "market", "commodity", "min_price", "max_price", "modal_price", "arrival_date"]
            
            # Keep only existing target columns
            existing_cols = [c for c in target_cols if c in df.columns]
            df_display = df[existing_cols].copy()
            
            # Clean numeric values for sorting
            if "modal_price" in df_display.columns:
                df_display["modal_price_numeric"] = pd.to_numeric(df_display["modal_price"], errors="coerce").fillna(0)
                # Sort by modal_price ascending by default
                df_display = df_display.sort_values(by="modal_price_numeric", ascending=True)
                df_display = df_display.drop(columns=["modal_price_numeric"])
                
            # Formatting Summary Metrics
            if "modal_price" in df.columns:
                modal_series = pd.to_numeric(df["modal_price"], errors="coerce").dropna()
                if not modal_series.empty:
                    min_val = modal_series.min()
                    max_val = modal_series.max()
                    avg_val = modal_series.mean()
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.markdown(f"<div class='metric-card'><div class='metric-title'>Total Mandis</div><div class='metric-num'>{len(df)}</div></div>", unsafe_allow_html=True)
                    m2.markdown(f"<div class='metric-card'><div class='metric-title'>Min Modal Price</div><div class='metric-num'>₹{min_val:,.0f}</div></div>", unsafe_allow_html=True)
                    m3.markdown(f"<div class='metric-card'><div class='metric-title'>Avg Modal Price</div><div class='metric-num'>₹{avg_val:,.0f}</div></div>", unsafe_allow_html=True)
                    m4.markdown(f"<div class='metric-card'><div class='metric-title'>Max Modal Price</div><div class='metric-num'>₹{max_val:,.0f}</div></div>", unsafe_allow_html=True)
                    st.write("")

            # Display Dataframe Table
            st.dataframe(
                df_display,
                use_container_width=True,
                column_config={
                    "state": "State",
                    "district": "District",
                    "market": "Market",
                    "commodity": "Commodity",
                    "min_price": st.column_config.NumberColumn("Min Price (₹/Qtl)", format="₹%d"),
                    "max_price": st.column_config.NumberColumn("Max Price (₹/Qtl)", format="₹%d"),
                    "modal_price": st.column_config.NumberColumn("Modal Price (₹/Qtl)", format="₹%d"),
                    "arrival_date": "Arrival Date"
                },
                hide_index=True
            )
