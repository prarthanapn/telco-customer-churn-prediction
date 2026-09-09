import os
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from backend.config import MODEL_PATH, PREPROCESSOR_PATH, CLASSIFICATION_THRESHOLD
from backend.utils.feature_mapping import REQUIRED_FEATURES, NUMERIC_FEATURES


class ChurnPredictor:
    """
    Singleton predictor class that loads the Keras DNN model and Scikit-Learn
    preprocessor once at startup and provides single/batch inference.
    """

    def __init__(self, model_path=MODEL_PATH, preprocessor_path=PREPROCESSOR_PATH, threshold=CLASSIFICATION_THRESHOLD):
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.threshold = threshold
        self.model = None
        self.preprocessor = None
        self._load_artifacts()

    def _load_artifacts(self):
        """Load model and preprocessor artifacts into memory."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")
        if not os.path.exists(self.preprocessor_path):
            raise FileNotFoundError(f"Preprocessor file not found at: {self.preprocessor_path}")

        print(f"[ChurnPredictor] Loading model from {self.model_path}")
        self.model = tf.keras.models.load_model(self.model_path, compile=False)

        print(f"[ChurnPredictor] Loading preprocessor from {self.preprocessor_path}")
        self.preprocessor = joblib.load(self.preprocessor_path)

    def _prepare_dataframe(self, data):
        """
        Ensure data is a pandas DataFrame with exact 19 required columns in proper dtypes.
        """
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise ValueError("Input data must be a dict, list of dicts, or pandas DataFrame.")

        # Ensure all 19 columns exist
        for col in REQUIRED_FEATURES:
            if col not in df.columns:
                raise KeyError(f"Missing required feature column '{col}'")

        # Select exact 19 columns in order
        df = df[REQUIRED_FEATURES].copy()

        # Coerce numeric features
        for num_col in NUMERIC_FEATURES:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

        return df

    def transform_features(self, df):
        """
        Transform raw input DataFrame using fitted sklearn preprocessor.
        Returns float32 numpy array ready for Keras DNN model input.
        """
        df_prepared = self._prepare_dataframe(df)
        transformed = self.preprocessor.transform(df_prepared)
        
        if hasattr(transformed, "toarray"):
            transformed = transformed.toarray()
            
        return np.asarray(transformed, dtype=np.float32)

    def get_risk_level(self, probability):
        """Categorize churn probability into risk tiers."""
        if probability >= 0.70:
            return "High Risk"
        elif probability >= self.threshold:
            return "Medium Risk"
        else:
            return "Low Risk"

    def predict_single(self, customer_dict):
        """
        Perform single customer churn prediction.
        
        Returns dict:
            {
                "churn_probability": float,
                "churn_prediction": int (0 or 1),
                "churn_label": str ("Yes" or "No"),
                "threshold": float,
                "risk_level": str
            }
        """
        X_proc = self.transform_features(customer_dict)
        raw_pred = self.model.predict(X_proc, verbose=0)
        prob = float(raw_pred[0][0])
        pred_label = 1 if prob >= self.threshold else 0

        return {
            "churn_probability": round(prob, 4),
            "churn_prediction": pred_label,
            "churn_label": "Yes" if pred_label == 1 else "No",
            "threshold": self.threshold,
            "risk_level": self.get_risk_level(prob)
        }

    def predict_batch(self, df):
        """
        Perform batch churn prediction on a DataFrame.
        
        Returns:
            pd.DataFrame with added columns: churn_probability, churn_prediction, risk_level
        """
        X_proc = self.transform_features(df)
        raw_preds = self.model.predict(X_proc, verbose=0).flatten()
        
        result_df = df.copy()
        result_df["churn_probability"] = [round(float(p), 4) for p in raw_preds]
        result_df["churn_prediction"] = (result_df["churn_probability"] >= self.threshold).astype(int)
        result_df["churn_label"] = result_df["churn_prediction"].map({1: "Yes", 0: "No"})
        result_df["risk_level"] = [self.get_risk_level(p) for p in raw_preds]

        return result_df
