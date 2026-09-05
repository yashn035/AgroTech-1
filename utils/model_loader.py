import os
import numpy as np
from PIL import Image
import streamlit as st

try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    tf = None

@st.cache_resource(show_spinner="Loading AI Model...")
def load_model(model_path: str):
    """
    Loads and caches the Keras plant disease detection model.
    
    Args:
        model_path (str): Path to the .keras or .h5 model file.
        
    Returns:
        tf.keras.Model: Loaded Keras model object.
    """
    if not HAS_TENSORFLOW:
        raise ImportError(
            "TensorFlow is not installed in the active Python environment. Please run 'pip install tensorflow' to enable live Keras model inference."
        )
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found at '{model_path}'. Please ensure 'disease_modal_final.keras' is placed at the project root."
        )
    try:
        model = tf.keras.models.load_model(model_path, compile=False)
        return model
    except Exception as e:
        raise RuntimeError(f"Failed to load the model file: {str(e)}")

def get_model_input_shape(model):
    """
    Inspects the input layer of the model to determine target height, width, and channels.
    Defaults to (224, 224, 3) if input shape is undefined or variable.
    """
    try:
        if hasattr(model, 'input_shape') and model.input_shape:
            shape = model.input_shape
            # shape is usually (None, height, width, channels)
            if len(shape) == 4 and shape[1] is not None and shape[2] is not None:
                return (int(shape[1]), int(shape[2]), int(shape[3]) if shape[3] else 3)
    except Exception:
        pass
    return (224, 224, 3)

def preprocess_image(image: Image.Image, input_shape=(224, 224, 3)) -> np.ndarray:
    """
    Preprocesses PIL image for Keras model prediction.
    - Converts image to RGB mode
    - Resizes to target (height, width)
    - Converts to float32 numpy array normalized to [0, 1]
    - Adds batch dimension: (1, height, width, channels)
    
    Args:
        image (Image.Image): Uploaded PIL image object.
        input_shape (tuple): Target shape (height, width, channels).
        
    Returns:
        np.ndarray: Preprocessed image tensor with shape (1, height, width, channels).
    """
    target_height, target_width = input_shape[0], input_shape[1]
    
    # Ensure RGB mode
    if image.mode != "RGB":
        image = image.convert("RGB")
        
    # Resize image to model expected input size
    image_resized = image.resize((target_width, target_height), Image.Resampling.BILINEAR)
    
    # Convert to array and scale pixel values to [0, 1]
    img_array = np.array(image_resized, dtype=np.float32) / 255.0
    
    # Expand dims for batch size 1
    img_batch = np.expand_dims(img_array, axis=0)
    
    return img_batch

def predict(model, processed_image: np.ndarray):
    """
    Runs model inference on preprocessed image batch.
    
    Args:
        model: Loaded Keras model.
        processed_image (np.ndarray): Tensor of shape (1, H, W, C).
        
    Returns:
        tuple: (predicted_class_index, confidence_score, all_probabilities)
    """
    predictions = model.predict(processed_image, verbose=0)
    
    # Handle single output array
    if isinstance(predictions, list):
        predictions = predictions[0]
        
    probs = predictions[0]
    predicted_idx = int(np.argmax(probs))
    confidence = float(probs[predicted_idx])
    
    return predicted_idx, confidence, probs
