import os
from pathlib import Path

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Model & Data Paths
MODEL_PATH = os.environ.get(
    "MODEL_PATH",
    str(BASE_DIR / "models" / "churn_dnn_optimized.keras")
)

PREPROCESSOR_PATH = os.environ.get(
    "PREPROCESSOR_PATH",
    str(BASE_DIR / "models" / "preprocessor_optimized.joblib")
)

SHAP_BACKGROUND_PATH = os.environ.get(
    "SHAP_BACKGROUND_PATH",
    str(BASE_DIR / "explainability" / "shap_background.joblib")
)

DATA_PATH = os.environ.get(
    "DATA_PATH",
    str(PROJECT_ROOT / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv")
)

# Classification Threshold — production model O10-BatchNorm at 0.45
# Confirmed by: shap_metadata.json, dnn_optimized_metadata_generated.json
CLASSIFICATION_THRESHOLD = float(os.environ.get("CLASSIFICATION_THRESHOLD", "0.45"))

# Risk Level Thresholds — configurable (probability values, inclusive lower bound)
# probability >= RISK_THRESHOLDS["high"]   → High Risk
# probability >= RISK_THRESHOLDS["medium"] → Medium Risk
# probability <  RISK_THRESHOLDS["medium"] → Low Risk
RISK_THRESHOLDS = {
    "high": float(os.environ.get("RISK_HIGH_THRESHOLD", "0.60")),
    "medium": float(os.environ.get("RISK_MEDIUM_THRESHOLD", "0.30")),
}

# Server Config
FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))
DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
