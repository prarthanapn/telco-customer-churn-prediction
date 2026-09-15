
import os
import sys
import hashlib
from datetime import datetime
from html import escape

# Ensure api_client can be imported regardless of CWD
_FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _FRONTEND_DIR not in sys.path:
    sys.path.insert(0, _FRONTEND_DIR)

import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import api_client
from api_client import APIError

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Telco Customer Churn Intelligence System",
    page_icon="C",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global Styles ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-main:       #f8fafc;
    --bg-card:       #ffffff;
    --border-color:  #e2e8f0;
    --text-main:     #0f172a;
    --text-secondary:#334155;
    --text-muted:    #64748b;
    --primary:       #1d4ed8;
    --primary-hover: #1e40af;
    --radius-md:     12px;
    --radius-sm:     8px;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    background-color: var(--bg-main) !important;
    color: var(--text-main) !important;
}

.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-main) !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    max-width: 1400px;
    padding: 1.5rem 2rem 3rem !important;
}

.section-label {
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #64748b !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    margin: 1.5rem 0 0.75rem 0 !important;
}

[data-testid="stSidebar"] {
    background-color: #fbfcfd !important;
    border-right: 1px solid var(--border-color) !important;
}

.sidebar-card {
    background-color: #ffffff;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 14px 16px;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.hero-container {
    background-color: #ffffff;
    border: 1px solid var(--border-color);
    border-left: 5px solid var(--primary);
    border-radius: var(--radius-md);
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(15,23,42,0.04);
}

.hero-subtitle {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--primary);
    margin-bottom: 0.25rem;
}

.hero-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--text-main);
    margin-bottom: 0.35rem;
}

.hero-desc {
    font-size: 0.95rem;
    color: var(--text-secondary);
    max-width: 900px;
    margin: 0;
}

.kpi-card {
    background-color: #ffffff;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    height: 100%;
}

.kpi-label {
    font-size: 11px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.kpi-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--text-main);
    line-height: 1.2;
    margin: 4px 0 2px 0;
}

.kpi-footer {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-muted);
}

.badge-high-risk {
    background-color: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fca5a5;
    padding: 6px 16px;
    border-radius: 9999px;
    font-weight: 800;
    font-size: 0.95rem;
    display: inline-block;
}
.badge-medium-risk {
    background-color: #fef3c7;
    color: #b45309;
    border: 1px solid #fcd34d;
    padding: 6px 16px;
    border-radius: 9999px;
    font-weight: 800;
    font-size: 0.95rem;
    display: inline-block;
}
.badge-low-risk {
    background-color: #dcfce7;
    color: #15803d;
    border: 1px solid #86efac;
    padding: 6px 16px;
    border-radius: 9999px;
    font-weight: 800;
    font-size: 0.95rem;
    display: inline-block;
}

[data-testid="stForm"] {
    background: #ffffff !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    padding: 1.25rem 1.5rem !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
}

.stButton > button {
    background: var(--primary) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: var(--radius-sm) !important;
    border: none !important;
    padding: 0.6rem 1.25rem !important;
}

[data-testid="stTabs"] button {
    color: var(--text-secondary) !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--primary) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: var(--primary) !important;
}
</style>
""", unsafe_allow_html=True)


# ─── Chart Theme Utility ────────────────────────────────────────────────────
def apply_enterprise_chart_theme(fig, height=340):
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#0f172a"),
        margin=dict(l=25, r=25, t=35, b=30),
    )
    fig.update_xaxes(gridcolor="#f1f5f9", linecolor="#cbd5e1")
    fig.update_yaxes(gridcolor="#f1f5f9", linecolor="#cbd5e1")
    return fig


def render_kpi(label: str, value: str, footer: str = ""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-footer">{footer}</div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str):
    st.markdown(f'<div class="section-label">{title}</div>', unsafe_allow_html=True)


def show_api_error(err):
    detail = f" - {err.details}" if getattr(err, "details", None) else ""
    st.error(f"Backend API Error: {err.message}{detail}")


def build_individual_report(customer_name: str, prediction: dict, explanation: dict, threshold: float) -> str:
    """Create a self-contained HTML report for one customer prediction."""
    probability = float(prediction.get("churn_probability", 0.0))
    risk = str(prediction.get("risk_level", "Unknown"))
    label = str(prediction.get("churn_label", "Unknown"))
    cutoff = float(prediction.get("threshold", threshold))
    baseline = float(explanation.get("base_value", 0.0))
    explained_probability = float(explanation.get("prediction_probability", probability))
    churn_drivers = explanation.get("top_churn_drivers", [])[:5]
    retention_drivers = explanation.get("top_retention_drivers", [])[:5]
    risk_class = "high" if "high" in risk.lower() else "medium" if "medium" in risk.lower() else "low"
    recommendation = (
        "Prioritize immediate retention outreach and review the strongest churn drivers."
        if risk == "High Risk"
        else "Review the strongest churn drivers and consider proactive retention outreach."
        if risk == "Medium Risk"
        else "Continue regular monitoring and reinforce the factors supporting retention."
    )

    def driver_rows(drivers, direction):
        rows = []
        for driver in drivers:
            value = float(driver.get("shap_value", 0.0))
            rows.append(
                f"<tr><td><strong>{escape(str(driver.get('feature', 'Unknown')))}</strong></td>"
                f"<td class=\"{direction}\">{value:+.4f}</td>"
                f"<td>{'Increases' if value > 0 else 'Decreases'} churn probability</td></tr>"
            )
        return "".join(rows) or '<tr><td colspan="3">No driver data available.</td></tr>'

    generated_at = datetime.now().strftime("%d %b %Y, %H:%M")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Individual Churn Prediction Report</title>
<style>
    :root {{ --navy:#102a43; --blue:#1769aa; --ink:#243b53; --muted:#627d98; --line:#d9e2ec; --page:#f4f7fb; --white:#fff; --red:#b42318; --red-bg:#fee4e2; --green:#027a48; --green-bg:#d1fadf; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; background:var(--page); color:var(--ink); font-family:Arial,Helvetica,sans-serif; line-height:1.5; }}
    .page {{ max-width:980px; margin:0 auto; padding:42px 28px 56px; }} .hero {{ background:linear-gradient(120deg,#102a43,#1769aa); color:#fff; padding:34px 38px; border-radius:18px; }}
    .eyebrow {{ color:#b9e6ff; font-size:12px; font-weight:700; letter-spacing:1.6px; text-transform:uppercase; }} h1 {{ margin:8px 0 6px; font-size:34px; }} .hero p {{ margin:0; color:#d9f0ff; }} .meta {{ margin-top:22px; color:#d9f0ff; font-size:13px; }}
    .decision {{ display:grid; grid-template-columns:1.1fr 1fr 1fr; gap:14px; margin:24px 0; }} .metric,.section {{ background:var(--white); border:1px solid var(--line); border-radius:14px; padding:22px; }} .metric-label {{ color:var(--muted); font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.5px; }} .metric-value {{ color:var(--navy); font-size:28px; font-weight:800; margin-top:5px; }}
    .risk {{ display:inline-block; border-radius:999px; padding:5px 10px; font-size:13px; font-weight:700; margin-top:8px; }} .risk-high {{ color:var(--red); background:var(--red-bg); }} .risk-medium {{ color:#b54708; background:#fef0c7; }} .risk-low {{ color:var(--green); background:var(--green-bg); }}
    .section {{ margin-top:18px; }} h2 {{ margin:0 0 8px; color:var(--navy); font-size:20px; }} .note {{ margin:0 0 18px; color:var(--muted); font-size:13px; }} .recommendation {{ border-left:4px solid var(--blue); background:#edf5fb; padding:14px 16px; color:var(--navy); font-weight:600; }}
    .tables {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }} table {{ width:100%; border-collapse:collapse; font-size:13px; }} th {{ background:#edf5fb; color:var(--navy); padding:11px 9px; text-align:left; font-size:11px; text-transform:uppercase; }} td {{ border-top:1px solid var(--line); padding:11px 9px; }} .positive {{ color:var(--red); font-weight:700; }} .negative {{ color:var(--blue); font-weight:700; }} .footer {{ color:var(--muted); font-size:12px; text-align:center; margin-top:24px; }}
    @media (max-width:700px) {{ .page {{ padding:20px 12px; }} .hero {{ padding:25px 22px; }} h1 {{ font-size:27px; }} .decision,.tables {{ grid-template-columns:1fr; }} }}
</style></head><body><main class="page">
<header class="hero"><div class="eyebrow">Telco Customer Churn Intelligence</div><h1>Individual Churn Prediction Report</h1><p>Model decision and SHAP explanation for one customer.</p><div class="meta"><strong>Customer:</strong> {escape(customer_name)} &nbsp;|&nbsp; <strong>Generated:</strong> {generated_at}</div></header>
<section class="decision"><div class="metric"><div class="metric-label">Churn probability</div><div class="metric-value">{probability:.1%}</div><span class="risk risk-{risk_class}">{escape(risk)}</span></div><div class="metric"><div class="metric-label">Model prediction</div><div class="metric-value">{'At risk' if label == 'Yes' else 'Stable'}</div><div>{'Churn expected' if label == 'Yes' else 'Retention expected'}</div></div><div class="metric"><div class="metric-label">Decision threshold</div><div class="metric-value">{cutoff:.0%}</div><div>Baseline: {baseline:.1%}</div></div></section>
<section class="section"><h2>Decision Summary</h2><p class="note">The model estimates a {probability:.1%} likelihood of churn for this customer. The explained probability is {explained_probability:.1%}, starting from a baseline probability of {baseline:.1%}.</p><div class="recommendation">Recommended next step: {recommendation}</div></section>
<section class="section"><h2>SHAP Feature Explanation</h2><p class="note">Positive SHAP values push the prediction toward churn. Negative SHAP values push it toward retention. These values explain model behavior and do not prove causation.</p><div class="tables"><div><h3>Factors increasing churn</h3><table><thead><tr><th>Feature</th><th>SHAP value</th><th>Impact</th></tr></thead><tbody>{driver_rows(churn_drivers, 'positive')}</tbody></table></div><div><h3>Factors supporting retention</h3><table><thead><tr><th>Feature</th><th>SHAP value</th><th>Impact</th></tr></thead><tbody>{driver_rows(retention_drivers, 'negative')}</tbody></table></div></div></section>
<p class="footer">Generated by the Telco Customer Churn Intelligence System. This report supports prioritization and should be reviewed with customer and business context.</p>
</main></body></html>"""


def build_batch_report(customers: pd.DataFrame, source_name: str, threshold: float) -> str:
    """Create a self-contained HTML report for all scored batch customers."""
    report_df = customers.copy()
    total = len(report_df)
    churn_count = int(report_df["churn_prediction"].eq(1).sum()) if "churn_prediction" in report_df else 0
    high_count = int(report_df["risk_level"].eq("High Risk").sum()) if "risk_level" in report_df else 0
    medium_count = int(report_df["risk_level"].eq("Medium Risk").sum()) if "risk_level" in report_df else 0
    low_count = int(report_df["risk_level"].eq("Low Risk").sum()) if "risk_level" in report_df else 0
    average_probability = float(report_df["churn_probability"].mean()) if total else 0.0

    def customer_label(row):
        return str(row.get("customerID") or row.get("display_name") or "Customer")

    detail_rows = []
    for _, row in report_df.iterrows():
        probability = float(row.get("churn_probability", 0.0))
        risk = str(row.get("risk_level", "Unknown"))
        prediction = str(row.get("churn_label", "Unknown"))
        risk_class = "high" if risk == "High Risk" else "medium" if risk == "Medium Risk" else "low"
        action = (
            "Prioritize immediate retention outreach."
            if risk == "High Risk"
            else "Review for proactive retention outreach."
            if risk == "Medium Risk"
            else "Continue regular customer monitoring."
        )
        detail_rows.append(
            f"""<tr>
                <td><strong>{escape(customer_label(row))}</strong></td>
                <td><span class=\"risk risk-{risk_class}\">{escape(risk)}</span></td>
                <td><strong>{probability:.1%}</strong></td>
                <td>{escape(prediction)}</td>
                <td>{action}</td>
            </tr>"""
        )

    generated_at = datetime.now().strftime("%d %b %Y, %H:%M")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Customer Churn Risk Report</title>
<style>
    :root {{ --navy:#102a43; --blue:#1769aa; --ink:#243b53; --muted:#627d98; --line:#d9e2ec; --page:#f4f7fb; --white:#ffffff; --red:#b42318; --red-bg:#fee4e2; --amber:#b54708; --amber-bg:#fef0c7; --green:#027a48; --green-bg:#d1fadf; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--page); color:var(--ink); font-family:Arial, Helvetica, sans-serif; line-height:1.5; }}
    .page {{ max-width:1180px; margin:0 auto; padding:42px 28px 56px; }}
    .hero {{ background:linear-gradient(120deg, #102a43, #1769aa); color:white; padding:34px 38px; border-radius:18px; }}
    .eyebrow {{ color:#b9e6ff; font-size:12px; font-weight:700; letter-spacing:1.6px; text-transform:uppercase; }}
    h1 {{ margin:8px 0 6px; font-size:34px; letter-spacing:-.5px; }}
    .hero p {{ margin:0; color:#d9f0ff; }}
    .meta {{ margin-top:22px; font-size:13px; color:#d9f0ff; }}
    .summary {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:24px 0; }}
    .metric {{ background:var(--white); border:1px solid var(--line); border-radius:12px; padding:18px; }}
    .metric-label {{ color:var(--muted); font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.5px; }}
    .metric-value {{ color:var(--navy); font-size:28px; font-weight:800; margin-top:5px; }}
    .section {{ background:var(--white); border:1px solid var(--line); border-radius:14px; padding:24px; margin-top:18px; }}
    h2 {{ color:var(--navy); font-size:20px; margin:0 0 8px; }}
    .note {{ color:var(--muted); font-size:13px; margin:0 0 18px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th {{ background:#edf5fb; color:var(--navy); text-align:left; padding:12px 10px; font-size:11px; text-transform:uppercase; letter-spacing:.4px; }}
    td {{ border-top:1px solid var(--line); padding:12px 10px; vertical-align:middle; }}
    tr:nth-child(even) td {{ background:#fbfdff; }}
    .risk {{ display:inline-block; border-radius:999px; padding:4px 9px; font-weight:700; font-size:12px; white-space:nowrap; }}
    .risk-high {{ color:var(--red); background:var(--red-bg); }} .risk-medium {{ color:var(--amber); background:var(--amber-bg); }} .risk-low {{ color:var(--green); background:var(--green-bg); }}
    .legend {{ color:var(--muted); font-size:13px; }}
    .footer {{ color:var(--muted); font-size:12px; margin-top:24px; text-align:center; }}
    @media (max-width:760px) {{ .page {{ padding:20px 12px; }} .hero {{ padding:25px 22px; }} h1 {{ font-size:27px; }} .summary {{ grid-template-columns:repeat(2,1fr); }} .section {{ padding:14px; overflow-x:auto; }} table {{ min-width:780px; }} }}
</style>
</head>
<body><main class="page">
    <header class="hero">
        <div class="eyebrow">Telco Customer Churn Intelligence</div>
        <h1>Customer Churn Risk Report</h1>
        <p>Batch prediction summary for customer retention planning.</p>
        <div class="meta"><strong>Source:</strong> {escape(source_name)} &nbsp;|&nbsp; <strong>Generated:</strong> {generated_at}</div>
    </header>
    <section class="summary">
        <div class="metric"><div class="metric-label">Customers scored</div><div class="metric-value">{total:,}</div></div>
        <div class="metric"><div class="metric-label">Predicted churn</div><div class="metric-value">{churn_count:,}</div></div>
        <div class="metric"><div class="metric-label">Average churn probability</div><div class="metric-value">{average_probability:.1%}</div></div>
        <div class="metric"><div class="metric-label">High-risk customers</div><div class="metric-value">{high_count:,}</div></div>
    </section>
    <section class="section">
        <h2>Risk Portfolio Overview</h2>
        <p class="note">The portfolio contains {high_count:,} high-risk, {medium_count:,} medium-risk, and {low_count:,} low-risk customers. The model classification threshold is {threshold:.0%}.</p>
        <p class="legend"><strong>Recommended prioritization:</strong> begin with high-risk customers, then review medium-risk customers for proactive retention actions.</p>
    </section>
    <section class="section">
        <h2>Individual Prediction Summary</h2>
        <p class="note">Each row summarizes the model output for one scored customer. Probabilities represent model-estimated churn likelihood, not certainty or causation.</p>
        <table><thead><tr><th>Customer</th><th>Risk level</th><th>Churn probability</th><th>Prediction</th><th>Suggested follow-up</th></tr></thead>
        <tbody>{''.join(detail_rows)}</tbody></table>
    </section>
    <p class="footer">Generated by the Telco Customer Churn Intelligence System. Use SHAP explanations in the dashboard to review the feature-level reasons behind an individual prediction.</p>
</main></body></html>"""


# ─── Data Loaders ────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_dataset():
    path = os.path.join(_FRONTEND_DIR, "..", "data", "WA_Fn-UseC_-Telco-Customer-Churn.csv")
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_features():
    try:
        return api_client.get_features().get("features", [])
    except APIError:
        return []

@st.cache_data(ttl=300)
def load_insights():
    try:
        return api_client.get_model_insights()
    except APIError:
        return {}


# ─── Session State ───────────────────────────────────────────────────────────
for key, default in [
    ("scored_customers", pd.DataFrame()),
    ("latest_prediction", None),
    ("latest_explanation", None),
    ("customer_name", ""),
    ("batch_results", None),
    ("batch_file_name", "uploaded_batch.csv"),
    ("batch_file_signature", None),
    ("chat_history", [
        {"role": "assistant", "content": "Hello! I am your **SHAP Decision Assistant**. Ask me any question about customer churn risk factors, SHAP feature drivers, threshold logic, or retention strategies."}
    ])
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─── Backend Health Check ────────────────────────────────────────────────────
try:
    health = api_client.check_health()
    backend_ok = health.get("status") == "ok"
except APIError:
    health = {}
    backend_ok = False

threshold = health.get("classification_threshold", 0.45)
risk_thresholds = health.get("risk_thresholds", {"high": 0.60, "medium": 0.30})


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:2px; font-weight:800; color:#0f172a; font-size:1.3rem;'>CHURN INTELLIGENCE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.82rem; color:#64748b; margin-bottom:1rem;'>Telco Decision Support Platform</p>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    if backend_ok:
        st.markdown('<div style="font-weight:700; color:#15803d; font-size:0.88rem;">Backend API Online</div>', unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.8rem; color:#334155; margin:6px 0 0 0;'><strong>Model:</strong> {health.get('model_name', 'DNN')}<br><strong>Threshold:</strong> {threshold:.0%}</p>", unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-weight:700; color:#b91c1c; font-size:0.88rem;">Backend API Offline</div>', unsafe_allow_html=True)
        st.caption("Start server via `python -m backend.app`")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight:700; font-size:0.78rem; text-transform:uppercase; color:#64748b; margin-bottom:4px;'>Risk Cutoffs</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.8rem; color:#334155; line-height:1.5;">
        <span style="color:#b91c1c; font-weight:700;">High Risk:</span> ≥ 60%<br>
        <span style="color:#b45309; font-weight:700;">Medium Risk:</span> 30% – 59%<br>
        <span style="color:#15803d; font-weight:700;">Low Risk:</span> &lt; 30%
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─── Hero Banner ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-subtitle">CUSTOMER RETENTION WORKSPACE</div>
    <div class="hero-title">Telecom Churn Intelligence</div>
    <p class="hero-desc">
        Score individual customers, review the factors behind each prediction, perform batch scoring, and prioritize retention work with confidence using explainable AI.
    </p>
</div>
""", unsafe_allow_html=True)


# ─── Main Tabs Navigation ───────────────────────────────────────────────────
overview_tab, predict_tab, batch_tab, assistant_tab = st.tabs([
    "Overview", "Predict Churn", "Batch Customers", "SHAP Assistant"
])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1: OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
with overview_tab:
    dataset = load_dataset()
    insights = load_insights()

    total_customers = len(dataset)
    churn_rate = dataset["Churn"].eq("Yes").mean() if "Churn" in dataset else 0.0
    churned_count = int(dataset["Churn"].eq("Yes").sum()) if "Churn" in dataset else 0
    metrics = insights.get("metrics_table", {})

    render_section_header("Executive Portfolio Summary")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: render_kpi("Total Customers", f"{total_customers:,}", "Dataset size")
    with c2: render_kpi("Historical Churn", f"{churn_rate:.1%}", "Observed baseline")
    with c3: render_kpi("Churn Events", f"{churned_count:,}", "Historical churners")
    with c4: render_kpi("DNN Accuracy", f"{float(metrics.get('Accuracy', 0.782)):.1%}", "Test set score")
    with c5: render_kpi("ROC-AUC Score", f"{float(metrics.get('ROC_AUC', 0.8397)):.4f}", "Model discrimination")

    render_section_header("Exploratory Data Analysis")
    col1, col2 = st.columns(2)
    with col1:
        if "tenure" in dataset.columns and "Churn" in dataset.columns:
            trend = dataset.assign(
                tenure_band=pd.cut(dataset["tenure"], bins=[-1, 6, 12, 24, 36, 54, 72],
                                   labels=["0-6 Mo", "7-12 Mo", "13-24 Mo", "25-36 Mo", "37-54 Mo", "55-72 Mo"])
            )
            trend = (trend.assign(churn_flag=trend["Churn"].eq("Yes"))
                         .groupby("tenure_band", observed=False)["churn_flag"]
                         .mean().reset_index(name="churn_rate"))
            fig_eda1 = px.bar(
                trend,
                x="tenure_band",
                y="churn_rate",
                labels={"tenure_band": "Tenure Cohort", "churn_rate": "Churn Rate"},
                color="tenure_band",
                color_discrete_sequence=["#2563eb", "#0d9488", "#f59e0b", "#ef4444", "#7c3aed", "#0891b2"],
                title="Churn Rate by Tenure Cohort",
            )
            fig_eda1.update_layout(yaxis_tickformat=".0%")
            apply_enterprise_chart_theme(fig_eda1, 300)
            st.plotly_chart(fig_eda1, width="stretch", config={"displayModeBar": False})

    with col2:
        if "Contract" in dataset.columns and "Churn" in dataset.columns:
            by_contract = (dataset.assign(churn_flag=dataset["Churn"].eq("Yes"))
                                  .groupby("Contract", as_index=False)["churn_flag"]
                                  .mean().rename(columns={"churn_flag": "churn_rate"}))
            fig_eda2 = px.bar(
                by_contract,
                x="churn_rate",
                y="Contract",
                orientation="h",
                color="churn_rate",
                color_continuous_scale=["#2563eb", "#0d9488", "#f59e0b", "#ef4444"],
                labels={"churn_rate": "Churn Rate", "Contract": "Contract Type"},
                title="Churn Rate by Contract Type",
            )
            fig_eda2.update_layout(xaxis_tickformat=".0%", coloraxis_showscale=False)
            apply_enterprise_chart_theme(fig_eda2, 300)
            st.plotly_chart(fig_eda2, width="stretch", config={"displayModeBar": False})

    if st.session_state.batch_results is not None and not st.session_state.batch_results.empty:
        render_section_header(f"Latest Batch Results ({len(st.session_state.batch_results)} Records)")
        st.info("Batch scoring completed. Open Batch Customers to filter or download the results.")
        st.dataframe(st.session_state.batch_results.head(10), width="stretch")


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2: PREDICT CHURN
# ═════════════════════════════════════════════════════════════════════════════
with predict_tab:
    render_section_header("Single Customer Risk Evaluator")

    if not backend_ok:
        st.warning("Backend API is currently offline. Please start the server using `python -m backend.app` to run predictions.")
    else:
        feature_metadata = load_features()
        if not feature_metadata:
            st.error("Unable to retrieve feature schema from backend API.")
        else:
            with st.form("predict_form", clear_on_submit=False):
                p_col1, p_col2, p_col3 = st.columns(3)
                with p_col1:
                    customer_name = st.text_input("Customer Name / Reference", value="Customer #8821-A")
                    contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
                    tenure = st.slider("Tenure (Months)", min_value=0, max_value=72, value=12)
                    monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, max_value=150.0, value=75.50, step=1.0)
                    total_charges = st.number_input("Total Charges ($)", min_value=0.0, max_value=12000.0, value=906.00, step=25.0)

                with p_col2:
                    internet = st.selectbox("Internet Service Type", ["Fiber optic", "DSL", "No"])
                    payment_method = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
                    paperless = st.selectbox("Paperless Billing", ["Yes", "No"])
                    senior = st.selectbox("Senior Citizen Status", [0, 1], format_func=lambda x: "Yes (1)" if x == 1 else "No (0)")
                    phone_svc = st.selectbox("Phone Service", ["Yes", "No"])

                with p_col3:
                    gender = st.selectbox("Gender", ["Female", "Male"])
                    partner = st.selectbox("Partner", ["No", "Yes"])
                    dependents = st.selectbox("Dependents", ["No", "Yes"])
                    multi_lines = st.selectbox("Multiple Lines", ["No", "Yes", "No phone service"])
                    online_sec = st.selectbox("Online Security", ["No", "Yes", "No internet service"])

                with st.expander("Additional Services", expanded=False):
                    d1, d2, d3 = st.columns(3)
                    with d1:
                        online_bkp = st.selectbox("Online Backup", ["No", "Yes", "No internet service"])
                        dev_prot = st.selectbox("Device Protection", ["No", "Yes", "No internet service"])
                    with d2:
                        tech_sup = st.selectbox("Tech Support", ["No", "Yes", "No internet service"])
                        stream_tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"])
                    with d3:
                        stream_mv = st.selectbox("Streaming Movies", ["No", "Yes", "No internet service"])

                submitted = st.form_submit_button("Calculate Risk Score", width="stretch")

            if submitted:
                payload = {
                    "gender":          gender,
                    "SeniorCitizen":   int(senior),
                    "Partner":         partner,
                    "Dependents":      dependents,
                    "tenure":          int(tenure),
                    "PhoneService":    phone_svc,
                    "MultipleLines":   multi_lines,
                    "InternetService": internet,
                    "OnlineSecurity":  online_sec,
                    "OnlineBackup":    online_bkp,
                    "DeviceProtection": dev_prot,
                    "TechSupport":     tech_sup,
                    "StreamingTV":     stream_tv,
                    "StreamingMovies": stream_mv,
                    "Contract":        contract,
                    "PaperlessBilling": paperless,
                    "PaymentMethod":   payment_method,
                    "MonthlyCharges":  float(monthly_charges),
                    "TotalCharges":    float(total_charges),
                }

                with st.spinner("Processing neural network scoring and SHAP attribution..."):
                    try:
                        result = api_client.predict_single_with_explain(payload)
                        pred = result.get("prediction", {})
                        expl = result.get("explanation", {})

                        st.session_state.latest_prediction = pred
                        st.session_state.latest_explanation = expl
                        st.session_state.customer_name = customer_name.strip() or "Customer"

                    except APIError as e:
                        show_api_error(e)
                        pred = None

                if pred:
                    prob = float(pred.get("churn_probability", 0))
                    risk = pred.get("risk_level", "Unknown")
                    label = pred.get("churn_label", "No")

                    risk_class = "badge-high-risk" if "high" in risk.lower() else ("badge-medium-risk" if "medium" in risk.lower() else "badge-low-risk")

                    res_col, shap_col = st.columns([1, 1.2])

                    with res_col:
                        render_section_header("Prediction Output")
                        st.markdown(f"**Subject Reference**  \n{st.session_state.customer_name}")
                        st.metric("Churn Probability", f"{prob:.1%}")
                        st.markdown(f"**{risk}**")
                        st.markdown(
                            f"Prediction: **{('At-Risk (Churn Expected)' if label == 'Yes' else 'Stable (Retention Expected)')}**  \n"
                            f"Cutoff threshold: **{float(pred.get('threshold', threshold)):.0%}**"
                        )

                    with shap_col:
                        render_section_header("Local SHAP Feature Drivers")
                        churn_drivers = expl.get("top_churn_drivers", [])[:5]
                        stay_drivers  = expl.get("top_retention_drivers", [])[:5]

                        base_value = float(expl.get("base_value", 0.0))
                        explanation_probability = float(expl.get("prediction_probability", prob))
                        st.caption(
                            f"Baseline probability: {base_value:.1%} | "
                            f"Explained probability: {explanation_probability:.1%}. "
                            "Red increases churn probability; blue decreases it."
                        )

                        all_drivers = (
                            [{"feature": d["feature"], "shap": d["shap_value"]} for d in churn_drivers] +
                            [{"feature": d["feature"], "shap": d["shap_value"]} for d in stay_drivers]
                        )

                        if all_drivers:
                            df_drv = pd.DataFrame(all_drivers)
                            df_drv["abs_shap"] = df_drv["shap"].abs()
                            df_drv = df_drv.sort_values("abs_shap", ascending=True)
                            colors = ["#1d4ed8" if s < 0 else "#b91c1c" for s in df_drv["shap"]]

                            fig_local = go.Figure(go.Bar(
                                x=df_drv["shap"],
                                y=df_drv["feature"],
                                orientation="h",
                                marker_color=colors,
                                text=[f"{v:+.4f}" for v in df_drv["shap"]],
                                textposition="outside",
                            ))
                            fig_local.update_layout(xaxis_title="SHAP Value Impact", showlegend=False)
                            apply_enterprise_chart_theme(fig_local, 300)
                            st.plotly_chart(fig_local, width="stretch", config={"displayModeBar": False})
                            top_churn = ", ".join(d["feature"] for d in churn_drivers[:3]) or "None"
                            top_stay = ", ".join(d["feature"] for d in stay_drivers[:3]) or "None"
                            st.markdown(
                                f"**Main churn drivers:** {top_churn}<br>"
                                f"**Main retention drivers:** {top_stay}",
                                unsafe_allow_html=True,
                            )

                    individual_report = build_individual_report(
                        st.session_state.customer_name,
                        pred,
                        expl,
                        float(threshold),
                    )
                    st.download_button(
                        label="Download Individual Report",
                        data=individual_report,
                        file_name="individual_churn_prediction_report.html",
                        mime="text/html",
                        help="Download the prediction, SHAP explanation, and recommended follow-up for this customer.",
                    )


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3: BATCH CUSTOMERS
# ═════════════════════════════════════════════════════════════════════════════
with batch_tab:
    render_section_header("Batch Customer Scoring & Segmentation")

    if not backend_ok:
        st.warning("Backend API is currently offline. Batch prediction requires an active API connection.")
    else:
        uploaded = st.file_uploader("Upload Customer CSV Dataset", type=["csv"])

        if uploaded:
            file_bytes = uploaded.getvalue()
            file_signature = hashlib.sha256(file_bytes).hexdigest()
        else:
            file_bytes = None
            file_signature = None

        if uploaded:
            st.info("CSV ready. Select Score Uploaded CSV to generate churn probability and risk results.")

        score_uploaded = uploaded and st.button(
            "Score Uploaded CSV",
            type="primary",
            width="stretch",
        )

        if uploaded and score_uploaded:
            with st.spinner("Processing batch predictions..."):
                try:
                    result = api_client.predict_batch(file_bytes, uploaded.name)
                    rows = result.get("predictions", [])
                    if rows:
                        customers = pd.DataFrame(rows)
                        customers["churn_probability"] = customers["churn_probability"].astype(float)
                        customers = customers.sort_values("churn_probability", ascending=False).reset_index(drop=True)
                        if "customerID" in customers.columns:
                            customers["display_name"] = customers["customerID"]
                        else:
                            customers["display_name"] = [f"Customer #{i+1:04d}" for i in range(len(customers))]
                        st.session_state.batch_results = customers
                        st.session_state.batch_file_signature = file_signature
                        st.session_state.batch_file_name = uploaded.name
                        st.session_state.batch_status = f"Batch completed: {len(customers)} customer records scored."
                        st.rerun()
                except APIError as err:
                    show_api_error(err)
                except Exception as err:
                    st.error(f"Batch scoring failed: {err}")

        display_df = st.session_state.batch_results
        if display_df is not None and not display_df.empty:
            render_section_header(f"Batch Scored Results ({len(display_df)} Records)")
            if st.session_state.get("batch_status"):
                st.success(st.session_state.batch_status)

            high_count = int(display_df["risk_level"].eq("High Risk").sum()) if "risk_level" in display_df else 0
            medium_count = int(display_df["risk_level"].eq("Medium Risk").sum()) if "risk_level" in display_df else 0
            churn_count = int(display_df["churn_prediction"].eq(1).sum()) if "churn_prediction" in display_df else 0
            s1, s2, s3 = st.columns(3)
            with s1:
                st.metric("Predicted Churn", f"{churn_count:,}")
            with s2:
                st.metric("High Risk", f"{high_count:,}")
            with s3:
                st.metric("Medium Risk", f"{medium_count:,}")

            visible_columns = [
                column for column in [
                    "customerID", "display_name", "churn_probability",
                    "churn_label", "risk_level", "churn_prediction"
                ] if column in display_df.columns
            ]
            visible_df = display_df[visible_columns].head(100).copy()
            if "churn_probability" in visible_df:
                visible_df["churn_probability"] = visible_df["churn_probability"].map(lambda value: f"{value:.1%}")
            visible_df = visible_df.rename(columns={
                "customerID": "Customer ID",
                "display_name": "Customer",
                "churn_probability": "Churn Probability",
                "churn_label": "Prediction",
                "risk_level": "Risk Level",
                "churn_prediction": "Prediction Code",
            })
            st.caption("Showing the top 100 customers ranked by churn probability. The download contains all scored customers.")
            st.dataframe(visible_df, width="stretch", hide_index=True)

            csv_buffer = io.StringIO()
            display_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download Results CSV",
                data=csv_buffer.getvalue(),
                file_name="batch_predictions.csv",
                mime="text/csv"
            )
            report_html = build_batch_report(
                display_df,
                st.session_state.get("batch_file_name", "uploaded_batch.csv"),
                float(threshold),
            )
            st.download_button(
                label="Download Professional Report",
                data=report_html,
                file_name="customer_churn_risk_report.html",
                mime="text/html",
                help="Download a formatted report with portfolio metrics and an individual summary for every scored customer.",
            )


# ═════════════════════════════════════════════════════════════════════════════
# TAB 4: SHAP ASSISTANT
# ═════════════════════════════════════════════════════════════════════════════
with assistant_tab:
    render_section_header("SHAP Decision Assistant")

    pred = st.session_state.latest_prediction
    expl = st.session_state.latest_explanation
    cname = st.session_state.customer_name or "Current Subject"

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_query := st.chat_input("Ask a question about churn risk drivers, SHAP values, or recommendations..."):
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        q_lower = user_query.lower()
        if not pred or not expl:
            response = "I am ready to explain predictions! Please calculate a risk score on the **Predict Churn** tab first."
        else:
            prob = float(pred.get("churn_probability", 0))
            risk = pred.get("risk_level", "Unknown")
            churn_drivers = expl.get("top_churn_drivers", [])
            retention_drivers = expl.get("top_retention_drivers", [])
            top_churn = ", ".join(
                f"**{driver['feature']}** ({driver['shap_value']:+.4f})"
                for driver in churn_drivers[:3]
            ) or "None"
            top_retention = ", ".join(
                f"**{driver['feature']}** ({driver['shap_value']:+.4f})"
                for driver in retention_drivers[:3]
            ) or "None"

            requested_feature = next(
                (driver for driver in expl.get("all_shap_values", [])
                 if driver["feature"].lower().replace("_", " ") in q_lower),
                None,
            )

            if requested_feature:
                direction = "increases" if requested_feature["shap_value"] > 0 else "decreases"
                response = (
                    f"For **{cname}**, **{requested_feature['feature']}** has a SHAP value of "
                    f"**{requested_feature['shap_value']:+.4f}**, which {direction} the churn probability."
                )
            elif any(w in q_lower for w in ["why", "reason", "risk", "driver", "factor"]):
                response = (
                    f"**{cname}** has a predicted churn probability of **{prob:.1%}** ({risk}).  \n"
                    f"Factors increasing churn: {top_churn}.  \n"
                    f"Factors reducing churn: {top_retention}."
                )
            elif any(w in q_lower for w in ["increase", "higher", "cause", "negative"]):
                response = f"The strongest factors increasing churn are: {top_churn}."
            elif any(w in q_lower for w in ["reduce", "decrease", "stay", "retention", "positive"]):
                response = f"The strongest factors reducing churn are: {top_retention}."
            elif any(w in q_lower for w in ["probability", "score", "risk level", "prediction"]):
                response = (
                    f"**{cname}** has a churn probability of **{prob:.1%}**, classified as **{risk}**. "
                    f"The decision threshold is **{float(pred.get('threshold', threshold)):.0%}**."
                )
            elif any(w in q_lower for w in ["threshold", "cutoff", "classif"]):
                response = (
                    f"A customer is classified as churn-risk when the probability is at least "
                    f"**{float(pred.get('threshold', threshold)):.0%}**. This customer is currently **{risk}**."
                )
            elif any(w in q_lower for w in ["shap", "method", "explain"]):
                response = (
                    f"SHAP starts from a baseline probability of **{float(expl.get('base_value', 0)):.1%}** "
                    f"and adds each feature's contribution to reach **{float(expl.get('prediction_probability', prob)):.1%}**. "
                    "Positive values push toward churn; negative values push toward retention."
                )
            elif any(w in q_lower for w in ["recommend", "action", "save", "retain"]):
                response = (
                    f"Prioritize **{cname}** for retention because the model assigns **{prob:.1%}** churn risk. "
                    f"Start by reviewing: {top_churn}."
                )
            else:
                response = (
                    f"**{cname}**: churn probability **{prob:.1%}**, risk **{risk}**. "
                    f"Ask about drivers, retention factors, the threshold, or a specific feature."
                )

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
