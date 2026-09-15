# Telco Customer Churn Prediction

An end-to-end machine learning application that helps telecom teams identify customers at risk of churning, understand the factors behind each prediction, and prioritize retention activity.

The project combines an optimized TensorFlow neural network, a Flask prediction API, SHAP explainability, and a Streamlit dashboard for interactive scoring and reporting.

![Python](https://img.shields.io/badge/Python-3.9--3.13-3776AB?logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?logo=tensorflow&logoColor=white)
![Flask](https://img.shields.io/badge/API-Flask-000000?logo=flask&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![SHAP](https://img.shields.io/badge/Explainability-SHAP-4B8BBE)

## Project Snapshot

| Area | Implementation |
| --- | --- |
| Business problem | Predict telecom customer churn early enough to support retention outreach |
| Dataset | IBM Telco Customer Churn dataset, 7,043 customer records |
| Production model | Optimized DNN: Dense 64 -> 32 -> 16 -> 1 with Batch Normalization and Dropout |
| Model input | 19 customer and service attributes transformed into 30 features |
| Explainability | Local SHAP explanations with DeepExplainer and KernelExplainer fallback |
| Backend | Flask REST API with validation, CORS, JSON responses, and batch CSV scoring |
| Frontend | Streamlit dashboard with individual scoring, batch analysis, risk ranking, and reports |
| Decision threshold | 0.45, selected to improve churn detection and F1 performance |

## Why This Project Matters

Churn models are most useful when they fit the decisions a business needs to make. This application goes beyond returning a probability:

- It separates model inference from the user interface through a REST API.
- It validates individual and batch inputs before scoring.
- It classifies customers into Low, Medium, and High Risk groups.
- It explains individual predictions with positive and negative feature contributions.
- It supports both one-customer investigation and portfolio-level retention planning.
- It generates downloadable CSV and professional HTML reports for operational follow-up.

## Model Performance

The selected model is the O10-BatchNorm experiment, evaluated on the held-out test set at a classification threshold of 0.45.

| Metric | Score |
| --- | ---: |
| Accuracy | 78.21% |
| Precision | 57.81% |
| Recall | **66.31%** |
| F1 score | 61.77% |
| ROC-AUC | 83.97% |

Recall is emphasized because missing a likely churner can be more costly than contacting a customer who ultimately stays. For comparison, the Logistic Regression baseline achieved 55.61% recall and 84.20% ROC-AUC. The optimized DNN improves churn recall by approximately 10.7 percentage points while preserving strong ranking performance.

## Application Workflow

```text
Customer data
     |
     v
Input validation and feature mapping
     |
     v
Saved preprocessing pipeline
     |
     v
Optimized TensorFlow model
     |
     +--> Churn probability, prediction, and risk level
     |
     +--> SHAP feature contributions
     |
     v
Streamlit dashboard and downloadable reports
```

## Product Features

### Overview

- Dataset summary and churn distribution
- Key portfolio metrics
- Churn patterns across tenure, contract type, and monthly charges

### Predict Churn

- Form-based scoring for a single customer
- Churn probability, predicted class, and configurable risk level
- Local SHAP chart showing the strongest churn and retention drivers
- Downloadable individual prediction report

### Batch Customers

- CSV upload for multiple customers
- Ranked results sorted by churn probability
- Predicted churn count and High/Medium Risk summaries
- Downloadable scored CSV
- Downloadable HTML portfolio report with an individual summary for each customer

### SHAP Assistant

- Natural-language questions about the latest prediction
- Answers about probability, threshold, risk level, individual features, churn drivers, retention drivers, and SHAP methodology

## Technical Architecture

```text
                    HTTP / JSON
Streamlit UI --------------------------> Flask REST API
    |                                      |
    |                                      +--> Request validation
    |                                      +--> ChurnPredictor
    |                                      +--> ChurnExplainer
    |                                      |
    |                                      +--> TensorFlow model
    |                                      +--> scikit-learn preprocessor
    |                                      +--> SHAP background data
    |
    +--> Plotly visualizations
    +--> CSV and HTML report generation
```

The backend initializes the model, preprocessor, and SHAP explainer once per process. This avoids repeatedly loading large artifacts during requests and keeps the API boundary separate from the presentation layer.

## Machine Learning Pipeline

### Input data

The dataset contains 7,043 records and 21 columns:

- 19 model features
- `customerID`, used for customer identification but excluded from model inference
- `Churn`, the target label in the source dataset

Numeric features include `SeniorCitizen`, `tenure`, `MonthlyCharges`, and `TotalCharges`. Categorical features cover demographics, contract details, payment method, and subscribed services.

### Preprocessing

1. Convert whitespace-only `TotalCharges` values to missing values.
2. Impute numeric values with a median strategy.
3. Impute categorical values with the most frequent category.
4. Standardize numeric columns with `StandardScaler`.
5. One-hot encode categorical columns with a first-category drop strategy.
6. Pass the resulting 30 features to the neural network.

The fitted `ColumnTransformer` is saved and reused during API inference so training-time and production-time transformations remain consistent.

### Selected neural network

```text
Input: 30 transformed features
  -> Dense(64, ReLU) -> BatchNormalization -> Dropout(0.5)
  -> Dense(32, ReLU) -> BatchNormalization -> Dropout(0.5)
  -> Dense(16, ReLU) -> BatchNormalization -> Dropout(0.5)
  -> Dense(1, Sigmoid)
```

Training configuration includes Adam with a learning rate of `0.0003`, binary cross-entropy loss, batch size `32`, and early stopping patience of `10`.

## Explainability

SHAP makes each prediction inspectable rather than treating the model as a black box.

- `DeepExplainer` is used for the TensorFlow model when supported.
- `KernelExplainer` is available as a fallback.
- A saved background dataset anchors the explanation baseline.
- Positive SHAP values push the prediction toward churn.
- Negative SHAP values push the prediction toward retention.

The dashboard presents the strongest local drivers for a customer, while the API can also return global feature importance for model-level analysis.

## Risk Logic

The classification threshold and risk bands are configurable through environment variables or `backend/config.py`.

```text
Probability >= 0.45  -> Predicted churn
Probability <  0.45  -> Predicted stay

Probability >= 0.60  -> High Risk
Probability >= 0.30  -> Medium Risk
Probability <  0.30  -> Low Risk
```

## Repository Structure

```text
Customer-Churn-Prediction/
├── backend/
│   ├── app.py                         Flask API and routes
│   ├── config.py                      Runtime paths and thresholds
│   ├── models/
│   │   ├── churn_dnn_optimized.keras  Trained TensorFlow model
│   │   └── preprocessor_optimized.joblib
│   ├── explainability/
│   │   ├── shap_explainer.py          Local and global SHAP logic
│   │   └── shap_background.joblib     SHAP background data
│   └── utils/
│       ├── feature_mapping.py         Feature metadata for the UI
│       ├── prediction.py               Model inference and risk logic
│       └── validation.py               Single and batch validation
├── data/
│   └── WA_Fn-UseC_-Telco-Customer-Churn.csv
├── frontend/
│   ├── api_client.py                  Backend HTTP client
│   └── streamlit_app.py               Dashboard and report generation
├── requirements.txt
└── README.md
```

## API Reference

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Check API and model readiness |
| `GET` | `/api/features` | Return feature metadata for the prediction form |
| `POST` | `/api/predict` | Score one customer |
| `POST` | `/api/predict/explain` | Score one customer and return SHAP explanation |
| `POST` | `/api/predict/batch` | Score customers from an uploaded CSV |
| `POST` | `/api/explain/batch-row` | Explain one row from a batch result |
| `GET` | `/api/model/insights` | Return model metrics and global SHAP importance |

### Example prediction request

```json
{
  "gender": "Female",
  "SeniorCitizen": 0,
  "Partner": "Yes",
  "Dependents": "No",
  "tenure": 2,
  "PhoneService": "Yes",
  "MultipleLines": "No",
  "InternetService": "Fiber optic",
  "OnlineSecurity": "No",
  "OnlineBackup": "No",
  "DeviceProtection": "No",
  "TechSupport": "No",
  "StreamingTV": "No",
  "StreamingMovies": "No",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 70.7,
  "TotalCharges": 151.65
}
```

Example response:

```json
{
  "churn_label": "Yes",
  "churn_prediction": 1,
  "churn_probability": 0.6157,
  "risk_level": "High Risk",
  "threshold": 0.45
}
```

## Local Setup

### Requirements

- Python 3.9 to 3.13
- Git
- A machine capable of running TensorFlow on CPU

### Installation

```bash
git clone https://github.com/poorvi-code/telco-customer-churn-prediction.git
cd telco-customer-churn-prediction

python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Start the application

Open two terminals from the project root.

Terminal 1, start the Flask API:

```bash
python -m backend.app
```

Terminal 2, start the Streamlit dashboard:

```bash
python -m streamlit run frontend/streamlit_app.py
```

Open `http://localhost:8501` in a browser. The API runs at `http://localhost:5000`.

### Verify the API

```bash
curl http://localhost:5000/api/health
```

The health response should report `"status": "ok"` and `"model_loaded": true`.

## Batch CSV Format

For batch scoring, upload a CSV containing the following model columns. `customerID` is optional and is preserved for result identification.

```text
customerID,gender,SeniorCitizen,Partner,Dependents,tenure,PhoneService,
MultipleLines,InternetService,OnlineSecurity,OnlineBackup,DeviceProtection,
TechSupport,StreamingTV,StreamingMovies,Contract,PaperlessBilling,
PaymentMethod,MonthlyCharges,TotalCharges
```

## Engineering Highlights

- Modular backend with clear separation between routing, validation, preprocessing, inference, and explainability.
- Reusable serialized model artifacts for consistent inference.
- Configurable thresholds through environment variables.
- Process-level model and explainer initialization for lower request overhead.
- API-level validation and structured error responses.
- Batch processing for real operational workflows.
- Downloadable reports that turn predictions into an actionable deliverable.
- Streamlit and Plotly interface designed for scanning risk and investigating individual customers.

## Limitations and Responsible Use

- The model was trained on a specific IBM Telco customer dataset and may not generalize to other markets, products, or B2B populations without retraining and validation.
- SHAP values describe model behavior and feature contribution; they do not establish causation.
- Risk thresholds should be calibrated against the economics and capacity of a real retention program.
- Predictions should support human review and customer-service decisions, not replace them.

