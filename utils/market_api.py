"""
AgroTech Mandi Market Price API Utility
Queries live Mandi arrival prices from data.gov.in REST API with caching and error handling.
"""

import os
import requests
import streamlit as st

API_ENDPOINT = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

@st.cache_data(ttl=300, show_spinner=False)
def fetch_market_prices(api_key: str = None, state: str = "", district: str = "", market: str = "", commodity: str = "", limit: int = 1000) -> list:
    """
    Fetches real-time Mandi market price records from data.gov.in API.
    
    Args:
        api_key (str, optional): data.gov.in API key. If None, retrieves from env.
        state (str): State name filter.
        district (str): District name filter.
        market (str): Market/Mandi name filter.
        commodity (str): Commodity name filter.
        limit (int): Maximum number of records to retrieve.
        
    Returns:
        list: List of record dictionaries returned by the API.
    """
    if not api_key:
        api_key = os.getenv("MANDI_API_KEY")
        if not api_key:
            try:
                if "MANDI_API_KEY" in st.secrets:
                    api_key = st.secrets["MANDI_API_KEY"]
            except Exception:
                api_key = None
                
    if not api_key or not api_key.strip():
        raise ValueError("MANDI_API_KEY is missing. Please set MANDI_API_KEY in environment variables or .env file.")
        
    if not state or not state.strip():
        raise ValueError("State is required for fetching market prices.")
        
    if not commodity or not commodity.strip():
        raise ValueError("Commodity is required for fetching market prices.")
        
    params = {
        "api-key": api_key.strip(),
        "format": "json",
        "limit": limit,
        "filters[state]": state.strip(),
        "filters[commodity]": commodity.strip()
    }
    
    if district and district.strip():
        params["filters[district]"] = district.strip()
        
    if market and market.strip():
        params["filters[market]"] = market.strip()
        
    try:
        response = requests.get(API_ENDPOINT, params=params, timeout=15)
        
        if response.status_code in (401, 403):
            raise RuntimeError("Unauthorized MANDI_API_KEY. Please verify your data.gov.in API key.")
        elif response.status_code == 429:
            raise RuntimeError("API rate limit reached. Please try again shortly.")
        elif response.status_code != 200:
            raise RuntimeError(f"Mandi API error (HTTP {response.status_code}).")
            
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("Unexpected response structure from Mandi API.")
            
        return data.get("records", [])
        
    except requests.exceptions.Timeout:
        raise RuntimeError("Mandi API connection timed out (15s).")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Unable to connect to data.gov.in API.")
    except Exception as e:
        raise RuntimeError(f"Error fetching mandi prices: {str(e)}")
