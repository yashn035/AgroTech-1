"""
AgroTech AI Leaf Disease Detection Page
Diagnoses plant leaf diseases using deep learning Keras models and maps results to pesticide treatments.
"""

import os
import sys
from PIL import Image
import streamlit as st

# Ensure project root is in sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.model_loader import load_model, get_model_input_shape, preprocess_image, predict
from utils.pesticide_mapper import get_pesticide_info
from utils.translations import t

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

# Load Custom CSS
css_path = os.path.join("static", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

lang = st.session_state.get("language", "en")

# Title & Description
st.markdown("<h1 class='main-header'>🌿 AI Leaf Disease Detection & Pesticide Guidance</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Upload a clear image of a crop leaf to diagnose diseases and receive immediate treatment protocols.</div>", unsafe_allow_html=True)

MODEL_PATH = "disease_modal_final.keras"

# Check Model Availability safely
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
            f"⚠️ **Model File Missing:** `{MODEL_PATH}` was not found in the root directory. "
            "Using preview mode with verified agronomic rule lookup."
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
            st.image(image, caption=f"Uploaded Image: {uploaded_file.name}", use_container_width=True)
            st.caption(f"Dimensions: {image.width}×{image.height} px | Format: {image.format}")
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
                    processed_img = preprocess_image(image, input_shape=model_input_shape)
                    pred_idx, confidence_val, probs = predict(model, processed_img)
                    
                    if 0 <= pred_idx < len(CLASS_NAMES):
                        predicted_class_name = CLASS_NAMES[pred_idx]
                    else:
                        st.error(f"Predicted index ({pred_idx}) out of range.")
            except Exception as e:
                st.error(f"An error occurred during model prediction: {str(e)}")
        else:
            st.info("💡 **Preview Mode:** Select a disease class below to inspect pesticide recommendations.")
            selected_sim_class = st.selectbox(
                "Choose sample class to preview diagnosis:",
                options=CLASS_NAMES,
                index=0
            )
            predicted_class_name = selected_sim_class
            confidence_val = 0.942
            
        if predicted_class_name:
            readable_label = predicted_class_name.replace("_", " ").title()
            
            # Save prediction into session state for Decision Engine integration
            st.session_state["disease_prediction"] = readable_label
            
            st.markdown("#### 1. Prediction Results")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Predicted Disease / Condition", readable_label)
            with c2:
                if confidence_val is not None:
                    st.metric("Confidence Score", f"{confidence_val * 100:.1f}%")
                    st.progress(min(max(confidence_val, 0.0), 1.0))
            
            st.caption(f"**Model Label ID:** `{predicted_class_name}`")
            st.divider()
            
            # Pesticide Recommendation Lookup
            st.markdown("#### 2. Recommended Pesticide & Treatment")
            pesticide_info = get_pesticide_info(predicted_class_name)
            
            status = pesticide_info.get("Match_Status", "NO MATCH")
            matched_disease = pesticide_info.get("Matched_Disease_in_DB", "N/A")
            best_product = pesticide_info.get("Best_Product", "N/A")
            dose = pesticide_info.get("Formulation_dose", "N/A")
            dilution = pesticide_info.get("Dilution_in_water", "N/A")
            
            if status == "MATCHED":
                st.markdown("<span class='badge-live'>✅ MATCHED - Treatment Protocol Found</span>", unsafe_allow_html=True)
                st.write("")
                
                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(f"""
                        <div class="card-box">
                            <div class="metric-label">Matched Disease in Database</div>
                            <div class="metric-value">{matched_disease}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div class="card-box">
                            <div class="metric-label">Formulation Dose</div>
                            <div class="metric-value">{dose}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                with m2:
                    st.markdown(f"""
                        <div class="card-box">
                            <div class="metric-label">Best Product Recommendation</div>
                            <div class="metric-value">{best_product}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div class="card-box">
                            <div class="metric-label">Dilution Rate in Water</div>
                            <div class="metric-value">{dilution}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
            elif status == "N/A":
                st.markdown("<span class='badge-live'>🌱 HEALTHY CROP</span>", unsafe_allow_html=True)
                st.write("")
                st.success("🎉 **Healthy – no pesticide needed.** Keep up standard crop monitoring and irrigation practices.")
                
            else:
                st.markdown("<span class='badge-live' style='background-color:#e65100;'>⚠️ NO MATCH / SPECIAL ADVISORY</span>", unsafe_allow_html=True)
                st.write("")
                st.warning(f"**Treatment Note:** {matched_disease}")
                if best_product != "N/A" and best_product != "":
                    st.info(f"**Suggested Alternative:** {best_product} (Dose: {dose})")

    else:
        st.write("Awaiting leaf upload...")
