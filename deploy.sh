#!/bin/bash
# AgroTech Automated One-Click Deployment Script

echo "🌾 Starting AgroTech Production Deployment..."

# Step 1: Check Python Environment
if command -v python3 &>/dev/null; then
    echo "✓ Python 3 detected."
else
    echo "❌ Python 3 is required."
    exit 1
fi

# Step 2: Install requirements
echo "📦 Installing production dependencies..."
pip install -r requirements.txt

# Step 3: Run Syntax & Verification Tests
echo "🧪 Running pre-deployment verification..."
python scratch/verify_code.py

if [ $? -eq 0 ]; then
    echo "✅ Verification successful!"
else
    echo "❌ Verification failed. Aborting deployment."
    exit 1
fi

# Step 4: Launch Streamlit App
echo "🚀 Launching AgroTech Platform on http://localhost:8501..."
streamlit run App.py --server.port 8501
