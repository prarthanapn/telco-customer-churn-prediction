"""
Single source of truth for the 19 input features used by the Telco Churn prediction model.
Defines metadata for each feature including display name, dtype, allowed values, min/max ranges, and default values.
"""

FEATURE_METADATA = [
    {
        "name": "gender",
        "display_name": "Gender",
        "dtype": "categorical",
        "allowed_values": ["Female", "Male"],
        "default": "Female"
    },
    {
        "name": "SeniorCitizen",
        "display_name": "Senior Citizen",
        "dtype": "numeric",
        "allowed_values": [0, 1],
        "min_value": 0,
        "max_value": 1,
        "default": 0
    },
    {
        "name": "Partner",
        "display_name": "Partner",
        "dtype": "categorical",
        "allowed_values": ["Yes", "No"],
        "default": "No"
    },
    {
        "name": "Dependents",
        "display_name": "Dependents",
        "dtype": "categorical",
        "allowed_values": ["Yes", "No"],
        "default": "No"
    },
    {
        "name": "tenure",
        "display_name": "Tenure (Months)",
        "dtype": "numeric",
        "min_value": 0,
        "max_value": 72,
        "default": 12
    },
    {
        "name": "PhoneService",
        "display_name": "Phone Service",
        "dtype": "categorical",
        "allowed_values": ["Yes", "No"],
        "default": "Yes"
    },
    {
        "name": "MultipleLines",
        "display_name": "Multiple Lines",
        "dtype": "categorical",
        "allowed_values": ["No phone service", "No", "Yes"],
        "default": "No"
    },
    {
        "name": "InternetService",
        "display_name": "Internet Service",
        "dtype": "categorical",
        "allowed_values": ["DSL", "Fiber optic", "No"],
        "default": "Fiber optic"
    },
    {
        "name": "OnlineSecurity",
        "display_name": "Online Security",
        "dtype": "categorical",
        "allowed_values": ["No", "Yes", "No internet service"],
        "default": "No"
    },
    {
        "name": "OnlineBackup",
        "display_name": "Online Backup",
        "dtype": "categorical",
        "allowed_values": ["Yes", "No", "No internet service"],
        "default": "No"
    },
    {
        "name": "DeviceProtection",
        "display_name": "Device Protection",
        "dtype": "categorical",
        "allowed_values": ["No", "Yes", "No internet service"],
        "default": "No"
    },
    {
        "name": "TechSupport",
        "display_name": "Tech Support",
        "dtype": "categorical",
        "allowed_values": ["No", "Yes", "No internet service"],
        "default": "No"
    },
    {
        "name": "StreamingTV",
        "display_name": "Streaming TV",
        "dtype": "categorical",
        "allowed_values": ["No", "Yes", "No internet service"],
        "default": "No"
    },
    {
        "name": "StreamingMovies",
        "display_name": "Streaming Movies",
        "dtype": "categorical",
        "allowed_values": ["No", "Yes", "No internet service"],
        "default": "No"
    },
    {
        "name": "Contract",
        "display_name": "Contract Type",
        "dtype": "categorical",
        "allowed_values": ["Month-to-month", "One year", "Two year"],
        "default": "Month-to-month"
    },
    {
        "name": "PaperlessBilling",
        "display_name": "Paperless Billing",
        "dtype": "categorical",
        "allowed_values": ["Yes", "No"],
        "default": "Yes"
    },
    {
        "name": "PaymentMethod",
        "display_name": "Payment Method",
        "dtype": "categorical",
        "allowed_values": [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)"
        ],
        "default": "Electronic check"
    },
    {
        "name": "MonthlyCharges",
        "display_name": "Monthly Charges ($)",
        "dtype": "numeric",
        "min_value": 0.0,
        "max_value": 150.0,
        "default": 70.0
    },
    {
        "name": "TotalCharges",
        "display_name": "Total Charges ($)",
        "dtype": "numeric",
        "min_value": 0.0,
        "max_value": 10000.0,
        "default": 840.0
    }
]

FEATURE_MAP = {f["name"]: f for f in FEATURE_METADATA}
REQUIRED_FEATURES = [f["name"] for f in FEATURE_METADATA]

NUMERIC_FEATURES = [f["name"] for f in FEATURE_METADATA if f["dtype"] == "numeric"]
CATEGORICAL_FEATURES = [f["name"] for f in FEATURE_METADATA if f["dtype"] == "categorical"]


def get_feature_metadata():
    """Return complete list of feature metadata."""
    return FEATURE_METADATA


def get_required_feature_names():
    """Return list of required 19 feature names."""
    return REQUIRED_FEATURES
