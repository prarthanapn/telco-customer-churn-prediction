# Telco Customer Churn Prediction

A complete machine learning project for predicting customer churn using the IBM Telco Customer Churn dataset. The project includes data analysis, preprocessing, classical machine learning models, deep learning, model optimization, and explainable AI.

The final application uses a **Flask REST API backend** and a **Streamlit frontend** for customer churn prediction and model explanations.

---

## 📌 Project Overview

Customer churn prediction helps telecommunication companies identify customers who are likely to leave their services.

This project analyzes customer demographics, account information, subscribed services, contract details, and billing information to predict whether a customer is likely to churn.

### The project includes:

- Data understanding and quality checks
- Exploratory Data Analysis (EDA)
- Data preprocessing
- Feature encoding and transformation
- Classical machine learning models
- Deep Neural Network (DNN)
- DNN optimization
- Classification threshold tuning
- SHAP-based explainability
- Single customer prediction
- Batch CSV prediction
- REST API
- Streamlit web application

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │     Streamlit Frontend  │
                    │        Port 8501        │
                    └────────────┬────────────┘
                                 │
                                 │ REST API
                                 ▼
                    ┌─────────────────────────┐
                    │      Flask Backend      │
                    │        Port 5000        │
                    ├─────────────────────────┤
                    │ Prediction              │
                    │ Preprocessing           │
                    │ Validation              │
                    │ SHAP Explainability    │
                    │ Model Insights          │
                    └────────────┬────────────┘
                                 │
                ┌────────────────┼────────────────┐
                ▼                ▼                ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │ DNN Model    │ │ Preprocessor │ │ SHAP         │
        │ .keras       │ │ .joblib      │ │ Explainer    │
        └──────────────┘ └──────────────┘ └──────────────┘