import os
import io
import json
import logging
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.config import FLASK_HOST, FLASK_PORT, DEBUG, CLASSIFICATION_THRESHOLD, RISK_THRESHOLDS
from backend.utils.feature_mapping import get_feature_metadata
from backend.utils.validation import validate_single_customer, validate_batch_dataframe
from backend.utils.prediction import ChurnPredictor
from backend.explainability.shap_explainer import ChurnExplainer

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("backend.app")

# Singletons loaded ONCE at application process startup
predictor = None
explainer = None


def create_app():
    global predictor, explainer

    app = Flask(__name__)
    CORS(app)  # Enable Cross-Origin Resource Sharing for Streamlit frontend

    logger.info("Initializing process-level model, preprocessor, and explainer singletons...")
    try:
        predictor = ChurnPredictor()
        explainer = ChurnExplainer(predictor=predictor)
        logger.info("Singletons initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing backend singletons: {e}", exc_info=True)
        # Process will fail at startup if model files cannot be loaded

    # ------------------ Routes ------------------

    @app.route("/api/health", methods=["GET"])
    def health():
        """Liveness and readiness health check endpoint."""
        status_ok = predictor is not None and predictor.model is not None
        return jsonify({
            "status": "ok" if status_ok else "unhealthy",
            "model_loaded": status_ok,
            "classification_threshold": predictor.threshold if predictor else CLASSIFICATION_THRESHOLD,
            "risk_thresholds": predictor.risk_thresholds if predictor else RISK_THRESHOLDS,
            "model_name": "O10-BatchNorm (Optimized DNN)"
        }), (200 if status_ok else 503)

    @app.route("/api/features", methods=["GET"])
    def features():
        """Expose 19 feature metadata for dynamic UI form generation."""
        try:
            metadata = get_feature_metadata()
            return jsonify({
                "features": metadata,
                "total_features": len(metadata)
            }), 200
        except Exception as e:
            logger.error(f"Error in /api/features: {e}")
            return jsonify({"error": "Failed to fetch feature metadata", "details": str(e)}), 500

    @app.route("/api/predict", methods=["POST"])
    def predict():
        """Single customer churn prediction."""
        try:
            payload = request.get_json()
            if not payload:
                return jsonify({"error": "Missing JSON request body"}), 400

            is_valid, errors = validate_single_customer(payload)
            if not is_valid:
                return jsonify({
                    "error": "Validation failed for input customer payload",
                    "validation_errors": errors
                }), 400

            result = predictor.predict_single(payload)
            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error in /api/predict: {e}", exc_info=True)
            return jsonify({"error": "Internal server error processing prediction", "details": str(e)}), 500

    @app.route("/api/predict/explain", methods=["POST"])
    def predict_and_explain():
        """Single customer churn prediction + SHAP local explanation."""
        try:
            payload = request.get_json()
            if not payload:
                return jsonify({"error": "Missing JSON request body"}), 400

            is_valid, errors = validate_single_customer(payload)
            if not is_valid:
                return jsonify({
                    "error": "Validation failed for input customer payload",
                    "validation_errors": errors
                }), 400

            prediction_result = predictor.predict_single(payload)
            explanation_result = explainer.explain_single(payload)

            combined_response = {
                "prediction": prediction_result,
                "explanation": explanation_result
            }
            return jsonify(combined_response), 200

        except Exception as e:
            logger.error(f"Error in /api/predict/explain: {e}", exc_info=True)
            return jsonify({"error": "Internal server error computing SHAP explanation", "details": str(e)}), 500

    @app.route("/api/predict/batch", methods=["POST"])
    def predict_batch_csv():
        """Batch CSV upload -> returns prediction dataframe as JSON."""
        try:
            if "file" not in request.files:
                return jsonify({"error": "No file uploaded in request (field 'file' required)"}), 400

            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "Uploaded file has empty filename"}), 400

            if not file.filename.lower().endswith(".csv"):
                return jsonify({"error": "Only CSV files are supported"}), 400

            csv_bytes = file.read()
            if len(csv_bytes) == 0:
                return jsonify({"error": "Uploaded CSV file is empty"}), 400

            try:
                raw_df = pd.read_csv(io.BytesIO(csv_bytes))
            except Exception as parse_err:
                return jsonify({"error": f"Failed to parse CSV: {str(parse_err)}"}), 400

            if raw_df.empty:
                return jsonify({"error": "CSV file has no data rows"}), 400

            # Validate uploaded dataframe
            is_valid, errors, cleaned_df = validate_batch_dataframe(raw_df)
            if not is_valid:
                return jsonify({
                    "error": "CSV batch payload failed validation checks",
                    "validation_errors": errors
                }), 400

            # Predict batch
            predicted_df = predictor.predict_batch(cleaned_df)

            # Keep customer IDs aligned with rows after prediction sorting.
            if "customerID" in predicted_df.columns:
                customer_ids = predicted_df.pop("customerID")
                predicted_df.insert(0, "customerID", customer_ids.values)
            elif "customerID" in raw_df.columns:
                predicted_df.insert(0, "customerID", raw_df["customerID"].values[:len(predicted_df)])

            # Use pandas JSON serialization so missing numeric values become JSON null,
            # rather than the invalid bare NaN token rejected by frontend clients.
            results = json.loads(predicted_df.to_json(orient="records"))

            return jsonify({
                "total_records": len(results),
                "predictions": results
            }), 200

        except Exception as e:
            logger.error(f"Error in /api/predict/batch: {e}", exc_info=True)
            return jsonify({"error": "Internal server error executing batch prediction", "details": str(e)}), 500

    @app.route("/api/explain/batch-row", methods=["POST"])
    def explain_batch_row():
        """Fetch SHAP explanation for a specific batch customer row payload."""
        try:
            payload = request.get_json()
            if not payload or "customer" not in payload:
                return jsonify({"error": "Request body must contain 'customer' JSON object"}), 400

            customer_dict = payload["customer"]
            row_index = payload.get("row_index", 0)

            is_valid, errors = validate_single_customer(customer_dict)
            if not is_valid:
                return jsonify({
                    "error": f"Validation failed for batch customer row {row_index}",
                    "validation_errors": errors
                }), 400

            explanation = explainer.explain_single(customer_dict)
            explanation["row_index"] = row_index

            return jsonify(explanation), 200

        except Exception as e:
            logger.error(f"Error in /api/explain/batch-row: {e}", exc_info=True)
            return jsonify({"error": "Internal server error computing batch row SHAP explanation", "details": str(e)}), 500

    @app.route("/api/model/insights", methods=["GET"])
    def model_insights():
        """Return actual model metrics, baseline comparison table, global SHAP importance, and limitations."""
        try:
            global_shap = explainer.global_importance() if explainer else []

            insights = {
                "architecture_summary": {
                    "model_name": "Optimized Deep Neural Network (O10-BatchNorm)",
                    "input_dimension": 30,
                    "layers": [
                        {"layer": 1, "type": "Dense(64, ReLU)", "regularization": "BatchNorm + Dropout(0.5)"},
                        {"layer": 2, "type": "Dense(32, ReLU)", "regularization": "BatchNorm + Dropout(0.5)"},
                        {"layer": 3, "type": "Dense(16, ReLU)", "regularization": "BatchNorm + Dropout(0.5)"},
                        {"layer": 4, "type": "Dense(1, Sigmoid)", "regularization": "None"}
                    ],
                    "optimizer": "Adam (learning_rate=0.0003)",
                    "loss_function": "Binary Crossentropy",
                    "batch_size": 32,
                    "early_stopping_patience": 10,
                    "classification_threshold": CLASSIFICATION_THRESHOLD,
                    "risk_thresholds": RISK_THRESHOLDS
                },
                # Metrics from shap_metadata.json (production source of truth, O10-BatchNorm at threshold 0.45)
                "metrics_table": {
                    "Accuracy": 0.7821,
                    "Precision": 0.5781,
                    "Recall": 0.6631,
                    "F1": 0.6177,
                    "ROC_AUC": 0.8397
                },
                # Baseline from reports/baseline_model_comparison.csv + optimized DNN
                "model_comparison_table": [
                    {"Model": "Logistic Regression", "Accuracy": 0.8055, "Precision": 0.6582, "Recall": 0.5561, "F1": 0.6029, "ROC_AUC": 0.8420},
                    {"Model": "Decision Tree",       "Accuracy": 0.7942, "Precision": 0.6296, "Recall": 0.5455, "F1": 0.5845, "ROC_AUC": 0.8284},
                    {"Model": "Random Forest",       "Accuracy": 0.7892, "Precision": 0.6305, "Recall": 0.4973, "F1": 0.5561, "ROC_AUC": 0.8226},
                    {"Model": "XGBoost",             "Accuracy": 0.8020, "Precision": 0.6568, "Recall": 0.5321, "F1": 0.5879, "ROC_AUC": 0.8445},
                    {"Model": "Optimized DNN (O10-BatchNorm)", "Accuracy": 0.7821, "Precision": 0.5781, "Recall": 0.6631, "F1": 0.6177, "ROC_AUC": 0.8397}
                ],
                "global_shap_importance": global_shap,
                "dataset_summary": {
                    "total_customers": 7043,
                    "churn_yes": 1869,
                    "churn_no": 5174,
                    "churn_percentage": 26.54,
                    "train_size": 4225,
                    "validation_size": 1409,
                    "test_size": 1409
                },
                "model_limitations": [
                    "Threshold Sensitive: Classification uses a custom 0.45 probability threshold optimized for high recall on churned customers.",
                    "Missing Value Handling: TotalCharges whitespace values are median-imputed via scikit-learn SimpleImputer; extreme unseen missingness may shift distributions.",
                    "Out-of-Distribution Inputs: Categorical inputs not in the initial 7,043 training set will be handled via OneHotEncoder drop strategy.",
                    "Model Domain Boundary: Trained specifically on Telco B2C customer demographics and service subscriptions; not applicable to Enterprise or B2B contracts.",
                    "SHAP Interpretability: SHAP values describe model behavior and feature attribution — they do not imply causation.",
                    "Class Imbalance: Dataset has ~73.5% non-churn vs ~26.5% churn. The model may perform differently on highly imbalanced production datasets."
                ]
            }

            return jsonify(insights), 200

        except Exception as e:
            logger.error(f"Error in /api/model/insights: {e}", exc_info=True)
            return jsonify({"error": "Failed to load model insights", "details": str(e)}), 500

    # Global Error Handlers (JSON responses, no raw tracebacks)
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad Request", "details": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return jsonify({"error": "Request too large. Maximum file size exceeded."}), 413

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG)
