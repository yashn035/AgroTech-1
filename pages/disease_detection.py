import os
import sys
from PIL import Image
import streamlit as st

# Ensure project root is in sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.model_loader import load_model, get_model_input_shape, preprocess_image, predict
from utils.pesticide_mapper import get_pesticide_info

# Page Configuration
st.set_page_config(
    page_title="Disease Detection & Pesticide Guidance - AgroTech",
    page_icon="🌿",
    layout="wide"
)

# Target 30 Classes provided
CLASS_NAMES = [
    'banana_bract_mosaic_virus', 'banana_cordana', 'banana_healthy',
    'banana_insectpest', 'banana_moko', 'banana_panama',
    'banana_pestalotiopsis', 'banana_sigatoka', 'banana_yb_sigatoka',
    'cauliflower_Blackrot', 'cauliflower_bacterial _spot _rot',
    'cauliflower_downy_mildew', 'cauliflower_healthy', 'chilli_anthracnose',
    'chilli_healthy', 'chilli_leafcurl', 'chilli_leafspot',
    'chilli_whitefly', 'chilli_yellowish', 'groundnut_early_leaf_spot',
    'groundnut_early_rust', 'groundnut_healthy', 'groundnut_late_leaf_spot',
    'groundnut_nutrition_deficiency', 'groundnut_rust',
    'radish_black_leaf_spot', 'radish_downey_mildew', 'radish_flea_beetle',
    'radish_healthy', 'radish_mosaic'
]

# Modern Custom CSS
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
    .status-badge-matched {
        background-color: #d8f3dc;
        color: #1b4332;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid #b7e4c7;
        display: inline-block;
    }
    .status-badge-healthy {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid #a5d6a7;
        display: inline-block;
    }
    .status-badge-nomatch {
        background-color: #fff3e0;
        color: #e65100;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid #ffe0b2;
        display: inline-block;
    }
    .card-box {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        margin-bottom: 1.2rem;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #666666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    .metric-value {
        font-size: 1.2rem;
        color: #1b4332;
        font-weight: 700;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Title & Description
st.markdown("<h1 class='main-header'>🌿 AI Leaf Disease Detection & Pesticide Recommendation</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Upload a clear image of a crop leaf to diagnose diseases and receive immediate treatment protocols.</div>", unsafe_allow_html=True)

MODEL_PATH = "disease_modal_final.keras"

# Check Model Availability
model_loaded = False
model = None
model_input_shape = (224, 224, 3)

try:
    if os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
        model_input_shape = get_model_input_shape(model)
        model_loaded = True
    else:
        st.warning(
            f"⚠️ **Model File Missing:** `{MODEL_PATH}` was not found in the project root directory. "
            "Please place your trained Keras model file at the root of `AgroTech/` to enable live model inference."
        )
except Exception as err:
    st.error(f"❌ **Error Loading Model:** {str(err)}")

# Section layout: File Uploader
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("### 📤 Upload Leaf Image")
    uploaded_file = st.file_uploader(
        "Select a leaf image (JPG, JPEG, PNG)",
        type=["jpg", "jpeg", "png"],
        help="Ensure the leaf lesion or symptom area is well-lit and in sharp focus."
    )
    
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Uploaded Image: {uploaded_file.name}", use_column_width=True)
            
            st.markdown(
                f"**Image Info:** {image.width}×{image.height} px | Format: {image.format} | Mode: {image.mode}"
            )
        except Exception as e:
            st.error(f"Failed to read image file: {str(e)}")
            image = None
    else:
        image = None
        st.info("👈 Upload an image to view real-time diagnosis.")

with col_right:
    st.markdown("### 🔬 Diagnosis & Treatment Protocol")
    
    if uploaded_file is not None and image is not None:
        predicted_class_name = None
        confidence_val = None
        
        if model_loaded and model is not None:
            try:
                with st.spinner("Processing image and analyzing leaf patterns..."):
                    # Step 1: Preprocess Image
                    processed_img = preprocess_image(image, input_shape=model_input_shape)
                    
                    # Step 2: Model Prediction
                    pred_idx, confidence_val, probs = predict(model, processed_img)
                    
                    # Map to target class list
                    if 0 <= pred_idx < len(CLASS_NAMES):
                        predicted_class_name = CLASS_NAMES[pred_idx]
                    else:
                        st.error(f"Predicted index ({pred_idx}) out of range for class list.")
            except Exception as e:
                st.error(f"An error occurred during model prediction: {str(e)}")
        else:
            st.info("💡 **Simulation Mode (Model not placed):** Select a sample class below to preview the pesticide recommendation engine.")
            selected_sim_class = st.selectbox(
                "Choose sample class to preview diagnosis:",
                options=CLASS_NAMES,
                index=0
            )
            predicted_class_name = selected_sim_class
            confidence_val = 0.942
            
        if predicted_class_name:
            # Display Prediction Results
            st.markdown("#### 1. Prediction Results")
            readable_label = predicted_class_name.replace("_", " ").title()
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Predicted Disease / Condition", readable_label)
            with c2:
                if confidence_val is not None:
                    st.metric("Confidence Score", f"{confidence_val * 100:.1f}%")
                    st.progress(min(max(confidence_val, 0.0), 1.0))
            
            st.caption(f"**Model Label ID:** `{predicted_class_name}`")
            st.divider()
            
            # Step 3: Pesticide Recommendation Lookup
            st.markdown("#### 2. Recommended Pesticide & Treatment")
            pesticide_info = get_pesticide_info(predicted_class_name)
            
            status = pesticide_info.get("Match_Status", "NO MATCH")
            matched_disease = pesticide_info.get("Matched_Disease_in_DB", "N/A")
            best_product = pesticide_info.get("Best_Product", "N/A")
            dose = pesticide_info.get("Formulation_dose", "N/A")
            dilution = pesticide_info.get("Dilution_in_water", "N/A")
            
            if status == "MATCHED":
                st.markdown(
                    "<span class='status-badge-matched'>✅ MATCHED - Treatment Protocol Found</span>",
                    unsafe_allow_html=True
                )
                st.write("")
                
                m1, m2 = st.columns(2)
                with m1:
                    st.markdown("""
                        <div class="card-box">
                            <div class="metric-label">Matched Disease in Database</div>
                            <div class="metric-value">{}</div>
                        </div>
                    """.format(matched_disease), unsafe_allow_html=True)
                    
                    st.markdown("""
                        <div class="card-box">
                            <div class="metric-label">Formulation Dose</div>
                            <div class="metric-value">{}</div>
                        </div>
                    """.format(dose), unsafe_allow_html=True)
                    
                with m2:
                    st.markdown("""
                        <div class="card-box">
                            <div class="metric-label">Best Product Recommendation</div>
                            <div class="metric-value">{}</div>
                        </div>
                    """.format(best_product), unsafe_allow_html=True)
                    
                    st.markdown("""
                        <div class="card-box">
                            <div class="metric-label">Dilution Rate in Water</div>
                            <div class="metric-value">{}</div>
                        </div>
                    """.format(dilution), unsafe_allow_html=True)
                    
            elif status == "N/A":
                st.markdown(
                    "<span class='status-badge-healthy'>🌱 HEALTHY CROP</span>",
                    unsafe_allow_html=True
                )
                st.write("")
                st.success("🎉 **Healthy – no pesticide needed.** Keep up standard crop monitoring and irrigation practices.")
                
            else:  # NO MATCH or fallback
                st.markdown(
                    "<span class='status-badge-nomatch'>⚠️ NO MATCH / SPECIAL ADVISORY</span>",
                    unsafe_allow_html=True
                )
                st.write("")
                st.warning(f"**Treatment Note:** {matched_disease}")
                if best_product != "N/A" and best_product != "":
                    st.info(f"**Suggested Alternative:** {best_product} (Dose: {dose})")

    else:
        st.write("Awaiting leaf upload...")
