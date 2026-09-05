# 🌾 AgroTech - Next-Gen Agricultural Intelligence Platform

**AgroTech** is a production-grade Streamlit web application designed to empower farmers, agronomists, and agricultural researchers with AI-driven crop diagnostics, instant treatment recommendations, real-time market pricing, predictive crop selection, district yield analytics, and early disease risk warnings.

---

## 📌 Features Status (All 5 Modules 100% LIVE!)

- **🌿 Disease Detection & Pesticide Guidance (LIVE)**: Deep learning model (`disease_modal_final.keras`) classifies 30 leaf disease/healthy condition classes and recommends pesticide treatment, dosage, and dilution.
- **📊 Mandi Market Price Checker (LIVE)**: Real-time Government Mandi API integration (`data.gov.in`) fetching daily arrival prices (Min, Max, Modal) for commodities across Indian states, districts, and markets.
- **🌱 Smart Crop Recommendation (LIVE)**: Machine Learning model (Random Forest Classifier) recommending optimal crops based on soil N-P-K nutrients, temperature, humidity, pH level, and rainfall.
- **🌾 District Crop Yield Estimator (LIVE)**: Interactive analytics dashboard exploring district harvest yields (kg/ha), production tonnages, multi-year trends (2015–2023), yield heatmaps, and CSV data export.
- **🔬 Early Stage Disease Prevention (LIVE)**: Rule-based agronomic early warning system assessing disease outbreak risk levels (Low, Moderate, High) and preventive advisories based on real-time temperature, humidity, and rainfall conditions.

---

## 📂 Project Structure

```
AgroTech/
├── app.py                                   # Main landing page & navigation launcher
├── pages/
│   ├── disease_detection.py                 # LIVE: Disease Detection & Pesticide Guidance
│   ├── market_price.py                      # LIVE: Mandi Market Price Checker
│   ├── crop_recommendation.py               # LIVE: Smart Crop Recommendation
│   ├── district_yield.py                    # LIVE: District Crop Yield Estimator & Analytics
│   └── early_disease.py                     # LIVE: Early Stage Disease Prevention & Risk Warning
├── utils/
│   ├── __init__.py
│   ├── model_loader.py                      # Keras model loader, preprocessing & inference
│   ├── pesticide_mapper.py                  # Cached CSV dataset lookup & mapping logic
│   └── market_api.py                        # Mandi API client (data.gov.in integration)
├── data/
│   ├── model_class_to_pesticide_mapping.csv  # 30-class disease to pesticide mapping database
│   └── pesticide_recommendation_dataset.csv  # Reference dataset
├── .env.example                             # Environment configuration template
├── .gitignore                               # Git exclusion rules
├── requirements.txt                         # Core dependencies
└── README.md                                # Documentation
```

---

## 🚀 Setup & Execution Instructions

### 1. Prerequisites
- Python 3.9+ installed.

### 2. Install Dependencies
Clone or navigate to the project directory and install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Environment & Mandi API Key Configuration
Copy `.env.example` to create your local `.env` file:
```bash
cp .env.example .env
```

Open `.env` and configure your `data.gov.in` Mandi API key:
```env
MANDI_API_KEY=your_actual_api_key_here
```
> **How to get a free Mandi API key:**
> 1. Register for a free developer account at [data.gov.in](https://data.gov.in/).
> 2. Search for the dataset: *Daily Mandi Prices*.
> 3. Generate an API Key under your account API keys dashboard.

*(If the API key is not configured, the Market Price page provides a simulated preview mode for UI testing).*

### 4. Model File Setup
Place your trained Keras model file named `disease_modal_final.keras` at the project root (`AgroTech/disease_modal_final.keras`).

---

## 💡 How to Run the Application

Launch the Streamlit web app:
```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

---

## 🛡️ Target Disease Classes & Recommended Crops

### Crop Recommendation Model (12 Targets)
`rice`, `wheat`, `maize`, `cotton`, `sugarcane`, `groundnut`, `mango`, `banana`, `tomato`, `potato`, `onion`, `chickpea`

### Disease Detection Model (30 Classes)
- **Banana**: `banana_bract_mosaic_virus`, `banana_cordana`, `banana_healthy`, `banana_insectpest`, `banana_moko`, `banana_panama`, `banana_pestalotiopsis`, `banana_sigatoka`, `banana_yb_sigatoka`
- **Cauliflower**: `cauliflower_Blackrot`, `cauliflower_bacterial _spot _rot`, `cauliflower_downy_mildew`, `cauliflower_healthy`
- **Chilli**: `chilli_anthracnose`, `chilli_healthy`, `chilli_leafcurl`, `chilli_leafspot`, `chilli_whitefly`, `chilli_yellowish`
- **Groundnut**: `groundnut_early_leaf_spot`, `groundnut_healthy`, `groundnut_late_leaf_spot`, `groundnut_nutrition_deficiency`, `groundnut_rust`
- **Radish**: `radish_black_leaf_spot`, `radish_downey_mildew`, `radish_flea_beetle`, `radish_healthy`, `radish_mosaic`
