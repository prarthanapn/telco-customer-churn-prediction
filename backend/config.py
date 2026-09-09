import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

# Model & Data Paths
MODEL_PATH = os.environ.get(
    "MODEL_PATH",
    os.path.join(BASE_DIR, "models", "churn_dnn_optimized.keras")
)

PREPROCESSOR_PATH = os.environ.get(
    "PREPROCESSOR_PATH",
    os.path.join(BASE_DIR, "models", "preprocessor_optimized.joblib")
)

SHAP_BACKGROUND_PATH = os.environ.get(
    "SHAP_BACKGROUND_PATH",
    os.path.join(BASE_DIR, "explainability", "shap_background.joblib")
)

DATA_PATH = os.environ.get(
    "DATA_PATH",
    os.path.join(PROJECT_ROOT, "data", "WA_Fn-UseC_-Telco-Customer-Churn.csv")
)

# Classification Threshold
CLASSIFICATION_THRESHOLD = 0.45

# Server Config
FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))
DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
