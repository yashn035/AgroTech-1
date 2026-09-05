# 🌾 AgroTech - Next-Gen Agricultural Intelligence Platform

**AgroTech** is a production-grade, multi-page Streamlit web application designed to empower farmers, agronomists, and agricultural researchers with AI-driven crop diagnostics, instant treatment recommendations, real-time market pricing, predictive crop selection, district yield analytics, early disease risk warnings, personalized farm action plans, profit-based crop selection, and an interactive **RAG AI Agricultural Copilot**.

---

## 📌 Features Status (100% LIVE Ecosystem)

- **🤖 AI Agricultural Copilot (LIVE - Phase 11)**: Retrieval-Augmented Generation (RAG) generative AI chatbot (`pages/copilot.py` & `utils/rag_engine.py`) indexing disease treatment databases, crop parameters, Mandi market pricing, and general agronomic advisories with source citations.
- **🌱 Smart Crop Recommendation (LIVE - Phase 7 Upgrade)**: Toggle between **Soil-Based Suitability** and **Profit-Based Return** (`pages/crop_recommendation.py`). Calculates net estimated profit per acre:
  $$\text{Expected Profit (₹/acre)} = (\text{Yield (Qtl/acre)} \times \text{Mandi Price (₹/Qtl)}) - \text{Cost (₹/acre)}$$
- **🌿 Disease Detection & Pesticide Guidance (LIVE)**: Deep learning model (`disease_modal_final.keras`) classifies 30 leaf disease/healthy condition classes and recommends pesticide treatment, dosage, and dilution.
- **📊 Mandi Market Price Checker (LIVE)**: Real-time Government Mandi API integration (`data.gov.in`) fetching daily arrival prices (Min, Max, Modal) for commodities across Indian states, districts, and markets.
- **🌾 District Crop Yield Estimator (LIVE)**: Interactive analytics dashboard exploring real district harvest yields (kg/ha), production tonnages, multi-year trends (2015–2023), yield heatmaps, and CSV data export.
- **🔬 Early Stage Disease Prevention (LIVE)**: Rule-based agronomic early warning system assessing disease outbreak risk levels (Low, Moderate, High) and preventive advisories based on real-time temperature, humidity, and rainfall conditions.
- **🌐 Multi-Language Support**: Full bilingual UI support for **English (`en`)** and **Hindi (`hi` 🇮🇳)** selectable via the sidebar.
- **🔐 User Authentication**: User registration and login with encrypted password storage (`bcrypt`) and session persistence.
- **🐳 Docker & Container Deployment**: Containerized configuration with `Dockerfile`, `docker-compose.yml`, and `deploy.sh`.

---

## 📂 Project Structure

```
AgroTech/
├── app.py                                   # Main landing page & navigation launcher
├── pages/
│   ├── copilot.py                           # LIVE: AI Agricultural Copilot Chatbot (RAG)
│   ├── crop_recommendation.py               # LIVE: Smart Crop Recommendation (Soil & Profit Toggles)
│   ├── disease_detection.py                 # LIVE: Disease Detection & Pesticide Guidance
│   ├── market_price.py                      # LIVE: Mandi Market Price Checker
│   ├── district_yield.py                    # LIVE: District Crop Yield Estimator & Analytics
│   └── early_disease.py                     # LIVE: Early Stage Disease Prevention & Risk Warning
├── utils/
│   ├── __init__.py
│   ├── rag_engine.py                        # RAG knowledge base & semantic retrieval engine
│   ├── model_loader.py                      # Keras model loader, preprocessing & inference
│   ├── pesticide_mapper.py                  # Cached CSV dataset lookup & mapping logic
│   ├── market_api.py                        # Mandi API client (data.gov.in integration)
│   ├── translations.py                      # Multi-language dictionary (English & Hindi)
│   └── auth.py                              # User authentication & password hashing
├── data/
│   ├── model_class_to_pesticide_mapping.csv  # 30-class disease to pesticide mapping database
│   ├── pesticide_recommendation_dataset.csv  # Reference dataset
│   ├── crop_recommendation_real.csv          # Real 22-crop soil-climate dataset
│   └── yield_data_real.csv                   # Real district harvest yield dataset
├── static/
│   └── style.css                            # Custom styling & mobile responsiveness
├── .env.example                             # Environment configuration template
├── .gitignore                               # Git exclusion rules
├── requirements.txt                         # Production dependencies
├── Dockerfile                               # Container build configuration
├── docker-compose.yml                       # Multi-container orchestration
├── deploy.sh                                # One-click deployment shell script
└── README.md                                # Documentation
```

---

## 🚀 Setup & Local Execution Instructions

### 1. Prerequisites
- Python 3.9+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment & Mandi API Key Configuration
Copy `.env.example` to create your local `.env` file:
```bash
cp .env.example .env
```
Set your `MANDI_API_KEY` in `.env`:
```env
MANDI_API_KEY=your_actual_api_key_here
```

### 4. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 Deployment Instructions

### Option A: Deployment to Streamlit Cloud (Recommended)
1. Fork or push this repository to GitHub: `https://github.com/yashn035/AgroTech-1.git`.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. Click **New app**, select repository `yashn035/AgroTech-1`, branch `main`, and main file `app.py`.
4. In Advanced Settings, add your environment variables under **Secrets**:
   ```toml
   MANDI_API_KEY = "your_actual_api_key_here"
   ```
5. Click **Deploy!**

### Option B: Deployment using Docker
1. Build the Docker image:
   ```bash
   docker build -t agrotech-app .
   ```
2. Run the Docker container:
   ```bash
   docker run -d -p 8501:8501 --name agrotech --env-file .env agrotech-app
   ```
3. Alternatively, launch with Docker Compose:
   ```bash
   docker-compose up -d
   ```
