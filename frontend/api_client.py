import os
import requests
import logging

logger = logging.getLogger("frontend.api_client")

# Backend Service Base URL
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000").rstrip("/")
DEFAULT_TIMEOUT = 30  # seconds


class APIError(Exception):
    """Custom exception class for backend API errors."""
    def __init__(self, message, status_code=None, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def _handle_response(response):
    """Parse HTTP response and raise APIError if non-2xx status code."""
    try:
        data = response.json()
    except Exception:
        data = {"error": response.text or "Unknown response format from backend"}

    if not response.ok:
        err_msg = data.get("error", f"API request failed with status code {response.status_code}")
        details = data.get("validation_errors") or data.get("details")
        raise APIError(message=err_msg, status_code=response.status_code, details=details)

    return data


def check_health():
    """Call GET /api/health to check backend availability."""
    url = f"{BACKEND_URL}/api/health"
    try:
        res = requests.get(url, timeout=5)
        return _handle_response(res)
    except requests.RequestException as e:
        raise APIError(f"Backend service unreachable at {BACKEND_URL}: {str(e)}")


def get_features():
    """Call GET /api/features to fetch 19 feature metadata for dynamic UI form building."""
    url = f"{BACKEND_URL}/api/features"
    try:
        res = requests.get(url, timeout=DEFAULT_TIMEOUT)
        return _handle_response(res)
    except requests.RequestException as e:
        raise APIError(f"Failed to fetch feature metadata from backend: {str(e)}")


def predict_single(customer_dict):
    """Call POST /api/predict for single customer prediction."""
    url = f"{BACKEND_URL}/api/predict"
    try:
        res = requests.post(url, json=customer_dict, timeout=DEFAULT_TIMEOUT)
        return _handle_response(res)
    except requests.RequestException as e:
        raise APIError(f"Failed single prediction request: {str(e)}")


def predict_single_with_explain(customer_dict):
    """Call POST /api/predict/explain for single customer prediction + SHAP explanation."""
    url = f"{BACKEND_URL}/api/predict/explain"
    try:
        res = requests.post(url, json=customer_dict, timeout=DEFAULT_TIMEOUT)
        return _handle_response(res)
    except requests.RequestException as e:
        raise APIError(f"Failed prediction and explanation request: {str(e)}")


def predict_batch(file_bytes, filename="uploaded_batch.csv"):
    """Call POST /api/predict/batch with CSV file bytes."""
    url = f"{BACKEND_URL}/api/predict/batch"
    try:
        files = {"file": (filename, file_bytes, "text/csv")}
        res = requests.post(url, files=files, timeout=60)
        return _handle_response(res)
    except requests.RequestException as e:
        raise APIError(f"Failed batch prediction request: {str(e)}")


def explain_batch_row(customer_dict, row_index=0):
    """Call POST /api/explain/batch-row for a specific batch customer row."""
    url = f"{BACKEND_URL}/api/explain/batch-row"
    try:
        payload = {"customer": customer_dict, "row_index": row_index}
        res = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
        return _handle_response(res)
    except requests.RequestException as e:
        raise APIError(f"Failed batch row SHAP explanation request: {str(e)}")


def get_model_insights():
    """Call GET /api/model/insights to fetch model metrics, comparison table, global SHAP, and limitations."""
    url = f"{BACKEND_URL}/api/model/insights"
    try:
        res = requests.get(url, timeout=DEFAULT_TIMEOUT)
        return _handle_response(res)
    except requests.RequestException as e:
        raise APIError(f"Failed to fetch model insights: {str(e)}")
