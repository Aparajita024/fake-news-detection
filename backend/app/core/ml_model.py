import joblib
import numpy as np
from pathlib import Path

# --- 1. Configuration ---
# Resolve the model path relative to this file so loading works regardless of cwd.
MODEL_PATH = Path(__file__).resolve().parent / "xgboost_model.pkl"
# Define the class labels your model was trained on, in the correct order.
CLASS_LABELS = ["Fake", "Real"]

# --- 2. Model Loading ---
# Load the model once when the application starts to avoid reloading on every request.
try:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(str(MODEL_PATH))

    model = joblib.load(str(MODEL_PATH))
    print(f"Machine Learning model loaded successfully from {MODEL_PATH}")
except FileNotFoundError:
    print(f"Error: Model file not found at {MODEL_PATH}. The predict function will return a default value.")
    model = None
except Exception as e:
    print(f"An unexpected error occurred while loading the model: {e}")
    model = None

# --- 3. Prediction Function ---
def predict(text: str) -> dict:
    """
    Analyzes a given text using the pre-loaded ML model.

    Args:
        text: The input string to analyze.

    Returns:
        A dictionary containing the 'verdict', 'confidence', 'explanation', and 'highlighted' keys.
    """
    if model is None:
        # Fallback response if the model failed to load
        return {
            "verdict": "Uncertain",
            "confidence": 0,
            "explanation": "Model is not available. Could not perform analysis.",
            "highlighted": []
        }

    # Use a try-except block for robustness during prediction
    try:
        # Get probability predictions from the model pipeline
        probabilities = model.predict_proba([text])[0]

        # Find the winning class and its confidence
        predicted_class_index = np.argmax(probabilities)
        verdict = CLASS_LABELS[predicted_class_index]
        confidence = int(probabilities[predicted_class_index] * 100)

        return {
            "verdict": verdict,
            "confidence": confidence,
            "explanation": "This verdict is based on a machine learning analysis of the text's content and structure.",
            "highlighted": ["mock_keyword", "suspicious_phrase"] # TODO: Implement real keyword extraction
        }
    except Exception as e:
        print(f"Error during model prediction: {e}")
        return {
            "verdict": "Uncertain",
            "confidence": 0,
            "explanation": f"An error occurred during analysis: {e}",
            "highlighted": []
        }