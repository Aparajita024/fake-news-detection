from pathlib import Path
import json

# Import required packages with error handling
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    print("joblib not available. Please install it with: pip install joblib")
    JOBLIB_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("numpy not available. Please install it with: pip install numpy")
    NUMPY_AVAILABLE = False

try:
    from sklearn import __version__ as sklearn_version
    import xgboost
    ML_PACKAGES_AVAILABLE = True
except ImportError as e:
    print(f"ML packages not available: {e}")
    print("Please install required packages: pip install scikit-learn xgboost")
    ML_PACKAGES_AVAILABLE = False
    sklearn_version = None

# --- 1. Configuration ---
CORE_DIR = Path(__file__).resolve().parent
MODEL_PATH = CORE_DIR / "xgboost_model.pkl"
VECTORIZER_PATH = CORE_DIR / "tfidf_vectorizer.pkl"
VERSIONS_PATH = CORE_DIR / "model_versions.json"
CLASS_LABELS = ["Fake", "Real"]

# --- 2. Version and Component Loading ---
model = None
vectorizer = None

if not all([ML_PACKAGES_AVAILABLE, JOBLIB_AVAILABLE, NUMPY_AVAILABLE]):
    print("="*80)
    print("ERROR: Required ML packages are not available!")
    if not ML_PACKAGES_AVAILABLE:
        print("Missing: scikit-learn and/or xgboost")
    if not JOBLIB_AVAILABLE:
        print("Missing: joblib")
    if not NUMPY_AVAILABLE:
        print("Missing: numpy")
    print("Please install all required packages before running the model.")
    print("="*80)
else:
    try:
        # Load the required versions from the JSON file
        if not VERSIONS_PATH.exists():
            print("WARNING: Model versions file not found!")
        else:
            with open(VERSIONS_PATH, 'r') as f:
                required_versions = json.load(f)
            
            required_sklearn_version = required_versions.get("scikit-learn")

            # Check if the current scikit-learn version matches the required version
            if sklearn_version != required_sklearn_version:
                print("="*80)
                print(f"WARNING: Scikit-learn version mismatch!")
                print(f"Model was trained with version: {required_sklearn_version}")
                print(f"You have version installed:     {sklearn_version}")
                print("This can cause unexpected errors or incorrect predictions.")
                print(f"Please run: pip install scikit-learn=={required_sklearn_version}")
                print("="*80)

        # Load the model and vectorizer
        if not MODEL_PATH.exists():
            print(f"ERROR: Model file not found at {MODEL_PATH}")
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        if not VECTORIZER_PATH.exists():
            print(f"ERROR: Vectorizer file not found at {VECTORIZER_PATH}")
            raise FileNotFoundError(f"Vectorizer file not found at {VECTORIZER_PATH}")

        try:
            model = joblib.load(str(MODEL_PATH))
            vectorizer = joblib.load(str(VECTORIZER_PATH))
            print("Machine Learning model and vectorizer loaded successfully.")
        except Exception as e:
            print(f"ERROR: Failed to load ML components: {e}")
            raise RuntimeError(f"Failed to load ML components: {e}")

    except Exception as e:
        print(f"An error occurred during ML component loading: {e}")
        print("The predict function will return a default 'Uncertain' value.")
        model = None
        vectorizer = None

# --- 3. Prediction Function ---
def predict(text: str) -> dict:
    """
    Analyzes a given text using the pre-loaded TF-IDF vectorizer and ML model.
    """
    print("\n--- [PREDICTION START] ---")
    if model is None or vectorizer is None:
        print("[PREDICTION_ERROR] Model or vectorizer not loaded.")
        return {
            "verdict": "Uncertain",
            "confidence": 0,
            "explanation": "Model components are not available. Could not perform analysis.",
            "highlighted": []
        }

    try:
        print(f"Received text for analysis: '{text[:100]}...'")

        # Step 1: Transform the input text
        print("Step 1: Transforming text with TF-IDF vectorizer...")
        text_vector = vectorizer.transform([text])
        print(f"Vectorizer output shape: {text_vector.shape}")
        # A shape of (1, 0) means the vocabulary was empty for this input.
        if text_vector.shape[1] == 0:
            print("[PREDICTION_WARNING] Vectorizer produced an empty vector. The model may not have any features to analyze.")
            # This can happen if the input text contains only words not seen during training.

        # Step 2: Get probability predictions
        print("Step 2: Predicting probabilities with XGBoost model...")
        probabilities = model.predict_proba(text_vector)[0]
        print(f"Model output (probabilities): {probabilities}")

        # Step 3: Determine verdict
        predicted_class_index = np.argmax(probabilities)
        verdict = CLASS_LABELS[predicted_class_index]
        confidence = int(probabilities[predicted_class_index] * 100)
        print(f"Verdict: '{verdict}' with {confidence}% confidence.")

        print("--- [PREDICTION SUCCESS] ---\n")
        return {
            "verdict": verdict,
            "confidence": confidence,
            "explanation": "This verdict is based on a machine learning analysis of the text's content and structure.",
            "highlighted": []
        }
    except Exception as e:
        print(f"[PREDICTION_ERROR] An exception occurred: {e}")
        import traceback
        traceback.print_exc()
        print("--- [PREDICTION FAILED] ---\n")
        return {
            "verdict": "Uncertain",
            "confidence": 0,
            "explanation": f"An error occurred during analysis: {e}",
            "highlighted": []
        }