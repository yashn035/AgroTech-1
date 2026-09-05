import os
import pandas as pd
import streamlit as st

DEFAULT_CSV_PATH = os.path.join("data", "model_class_to_pesticide_mapping.csv")

@st.cache_data(show_spinner=False)
def load_pesticide_mapping(csv_path: str = DEFAULT_CSV_PATH) -> pd.DataFrame:
    """
    Loads and caches the model-class-to-pesticide mapping CSV dataset.
    
    Args:
        csv_path (str): Path to model_class_to_pesticide_mapping.csv
        
    Returns:
        pd.DataFrame: Loaded mapping dataframe.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Pesticide mapping database not found at '{csv_path}'.")
    try:
        df = pd.read_csv(csv_path, keep_default_na=False)
        # Strip column names and string fields
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        raise RuntimeError(f"Error reading pesticide mapping file: {str(e)}")

def get_pesticide_info(class_name: str, csv_path: str = DEFAULT_CSV_PATH) -> dict:
    """
    Looks up pesticide recommendation details for a given predicted model label.
    
    Args:
        class_name (str): Predicted class label string matching 'Model_Label' in CSV.
        csv_path (str): Path to CSV file.
        
    Returns:
        dict: Dictionary containing Match_Status, Matched_Disease_in_DB, Best_Product, Formulation_dose, Dilution_in_water.
    """
    try:
        df = load_pesticide_mapping(csv_path)
    except Exception as e:
        return {
            "Match_Status": "ERROR",
            "Matched_Disease_in_DB": f"Data lookup failed: {str(e)}",
            "Best_Product": "N/A",
            "Formulation_dose": "N/A",
            "Dilution_in_water": "N/A"
        }
        
    # Match on Model_Label
    matched_row = df[df["Model_Label"] == class_name.strip()]
    
    if matched_row.empty:
        return {
            "Match_Status": "NO MATCH",
            "Matched_Disease_in_DB": f"No registered pesticide recommendation found in database for class '{class_name}'. Consult an agricultural extension specialist.",
            "Best_Product": "N/A",
            "Formulation_dose": "N/A",
            "Dilution_in_water": "N/A"
        }
        
    row = matched_row.iloc[0]
    
    return {
        "Match_Status": str(row.get("Match_Status", "NO MATCH")),
        "Matched_Disease_in_DB": str(row.get("Matched_Disease_in_DB", "N/A")),
        "Best_Product": str(row.get("Best_Product", "N/A")),
        "Formulation_dose": str(row.get("Formulation_dose", "N/A")),
        "Dilution_in_water": str(row.get("Dilution_in_water", "N/A"))
    }
