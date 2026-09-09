import pandas as pd
import numpy as np
from backend.utils.feature_mapping import (
    FEATURE_MAP,
    REQUIRED_FEATURES,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES
)


def validate_single_customer(payload):
    """
    Validate a single customer JSON dictionary payload.
    
    Returns:
        (is_valid: bool, errors: list of dicts)
        errors format: [{"row": 1, "field": "<field>", "error": "<msg>"}]
    """
    errors = []
    if not isinstance(payload, dict):
        return False, [{"row": 1, "field": "payload", "error": "Payload must be a JSON object"}]

    # 1. Check required fields
    for field in REQUIRED_FEATURES:
        if field not in payload or payload[field] is None:
            errors.append({"row": 1, "field": field, "error": f"Missing required field '{field}'"})
            continue

        meta = FEATURE_MAP[field]
        val = payload[field]

        # Handle whitespace strings in TotalCharges or numeric fields
        if isinstance(val, str):
            val_stripped = val.strip()
            if field == "TotalCharges" and val_stripped == "":
                # Allowed dirty data, preprocessor imputer will handle NaN
                continue
            elif meta["dtype"] == "numeric":
                try:
                    val = float(val_stripped)
                except ValueError:
                    errors.append({
                        "row": 1,
                        "field": field,
                        "error": f"Invalid numeric value '{payload[field]}' for field '{field}'"
                    })
                    continue

        # Categorical check
        if meta["dtype"] == "categorical":
            str_val = str(val).strip()
            allowed = meta.get("allowed_values", [])
            if str_val not in allowed:
                errors.append({
                    "row": 1,
                    "field": field,
                    "error": f"Invalid categorical value '{val}' for '{field}'. Allowed values: {allowed}"
                })

        # Numeric check
        elif meta["dtype"] == "numeric":
            try:
                num_val = float(val)
                if field == "tenure" and (num_val < 0 or num_val > 72):
                    errors.append({
                        "row": 1,
                        "field": field,
                        "error": f"Tenure must be between 0 and 72 months, got {num_val}"
                    })
                elif field == "MonthlyCharges" and num_val <= 0:
                    errors.append({
                        "row": 1,
                        "field": field,
                        "error": f"MonthlyCharges must be greater than 0, got {num_val}"
                    })
                elif field == "TotalCharges" and num_val < 0:
                    errors.append({
                        "row": 1,
                        "field": field,
                        "error": f"TotalCharges cannot be negative, got {num_val}"
                    })
            except (ValueError, TypeError):
                errors.append({
                    "row": 1,
                    "field": field,
                    "error": f"Value '{val}' for '{field}' could not be converted to float"
                })

    is_valid = (len(errors) == 0)
    return is_valid, errors


def validate_batch_dataframe(df):
    """
    Validate a pandas DataFrame uploaded via batch CSV.
    
    Returns:
        (is_valid: bool, errors: list of dicts, cleaned_df: pd.DataFrame)
        errors format: [{"row": row_num, "field": "<field>", "error": "<msg>"}]
    """
    errors = []
    if not isinstance(df, pd.DataFrame):
        return False, [{"row": 0, "field": "csv", "error": "Uploaded file is not a valid CSV/DataFrame"}], None

    # Check for missing required columns
    missing_cols = [col for col in REQUIRED_FEATURES if col not in df.columns]
    if missing_cols:
        return False, [
            {"row": 0, "field": col, "error": f"CSV missing required column '{col}'"}
            for col in missing_cols
        ], None

    cleaned_df = df.copy()

    # Coerce TotalCharges to numeric, converting whitespace to NaN
    if "TotalCharges" in cleaned_df.columns:
        cleaned_df["TotalCharges"] = pd.to_numeric(cleaned_df["TotalCharges"], errors="coerce")

    # Validate each row (up to max recommended limit of 1000 or full dataset)
    for idx, row in cleaned_df.iterrows():
        row_num = idx + 1  # 1-indexed for display
        for field in REQUIRED_FEATURES:
            meta = FEATURE_MAP[field]
            val = row[field]

            if pd.isna(val):
                if field == "TotalCharges":
                    # Imputer in preprocessor will handle NaN
                    continue
                else:
                    errors.append({
                        "row": row_num,
                        "field": field,
                        "error": f"Missing value (NaN/null) for required field '{field}'"
                    })
                    continue

            if meta["dtype"] == "categorical":
                str_val = str(val).strip()
                allowed = meta.get("allowed_values", [])
                if str_val not in allowed:
                    errors.append({
                        "row": row_num,
                        "field": field,
                        "error": f"Invalid value '{val}' for field '{field}'. Allowed: {allowed}"
                    })
            elif meta["dtype"] == "numeric":
                try:
                    num_val = float(val)
                    if field == "tenure" and (num_val < 0 or num_val > 72):
                        errors.append({
                            "row": row_num,
                            "field": field,
                            "error": f"Tenure must be between 0 and 72, got {num_val}"
                        })
                    elif field == "MonthlyCharges" and num_val <= 0:
                        errors.append({
                            "row": row_num,
                            "field": field,
                            "error": f"MonthlyCharges must be > 0, got {num_val}"
                        })
                except (ValueError, TypeError):
                    errors.append({
                        "row": row_num,
                        "field": field,
                        "error": f"Invalid numeric value '{val}' for field '{field}'"
                    })

        # Cap validation error collection at 50 errors to prevent payload explosion
        if len(errors) >= 50:
            errors.append({
                "row": row_num,
                "field": "batch",
                "error": "Validation stopped after reaching 50 errors."
            })
            break

    is_valid = (len(errors) == 0)
    return is_valid, errors, cleaned_df
