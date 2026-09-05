import requests
import streamlit as st

API_ENDPOINT = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

@st.cache_data(ttl=600, show_spinner=False)
def fetch_market_prices(api_key: str, state: str, district: str = "", market: str = "", commodity: str = "", limit: int = 1000):
    """
    Fetches real-time Mandi market price records from data.gov.in API.
    
    Args:
        api_key (str): data.gov.in API key.
        state (str): State name (required filter).
        district (str): District name (optional filter).
        market (str): Market/Mandi name (optional filter).
        commodity (str): Commodity name (required filter).
        limit (int): Maximum number of records to retrieve (default 1000).
        
    Returns:
        list: List of record dictionaries returned by the API.
        
    Raises:
        ValueError: If required arguments or API key are missing.
        RuntimeError: If API call fails due to network, status, or parsing issues.
    """
    if not api_key or not api_key.strip():
        raise ValueError("MANDI_API_KEY is missing. Please configure your API key in environment variables or .env file.")
        
    if not state or not state.strip():
        raise ValueError("State is required for fetching market prices.")
        
    if not commodity or not commodity.strip():
        raise ValueError("Commodity is required for fetching market prices.")
        
    # Construct Query Parameters
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
        
        # Check HTTP status codes
        if response.status_code == 401 or response.status_code == 403:
            raise RuntimeError("Invalid or unauthorized MANDI_API_KEY. Please check your data.gov.in API key.")
        elif response.status_code == 429:
            raise RuntimeError("API rate limit exceeded. Please wait a moment before trying again.")
        elif response.status_code != 200:
            raise RuntimeError(f"Government API returned error status code {response.status_code}.")
            
        data = response.json()
        
        if not isinstance(data, dict):
            raise RuntimeError("Unexpected API response format.")
            
        # The records are under key 'records'
        records = data.get("records", [])
        return records
        
    except requests.exceptions.Timeout:
        raise RuntimeError("Request to Mandi API timed out (15s). Please check your internet connection or try again later.")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Network connection error while reaching data.gov.in API. Please check your internet connection.")
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("Failed to decode JSON response from Mandi API.")
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while fetching market prices: {str(e)}")
