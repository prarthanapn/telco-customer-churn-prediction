import streamlit as st
import pandas as pd
import plotly.express as px
# Custom Light Theme Styling
import api_client

# Configure Streamlit Page
st.set_page_config(
    page_title="Telco Churn Intelligence Platform",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    :root {
        --ink: #17212b;
        --muted: #687586;
        --line: #e6ebf0;
        --canvas: #f5f7f9;
        --panel: #ffffff;
        --teal: #087f73;
        --coral: #d95d4f;
        --blue: #2d6cdf;
    }

    page_title="Telco Churn Intelligence Platform",
    page_icon="📡",
    layout="wide",

    [data-testid="stAppViewContainer"] {
        background: var(--canvas);
    }


        background-color: var(--canvas);
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: #fbfcfd;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 2rem 1.25rem;
    }

    [data-testid="stSidebar"] h3 {
        color: var(--ink);
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    /* Light workspace header */
    .header-banner {
        background: var(--panel);
        color: var(--ink);
        padding: 2.35rem 2.6rem 2.2rem;
        border: 1px solid var(--line);
        border-radius: 18px;
        box-shadow: 0 12px 30px rgba(30, 45, 60, 0.06);
        margin: 0.4rem 0 1.8rem;
        position: relative;
        overflow: hidden;
    }

    .header-banner::after {
        content: "";
        position: absolute;
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: #e6f5f2;
        right: -55px;
        top: -70px;
    }

    .header-kicker {
        color: var(--teal);
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.7rem;
    }

        color: #1e293b;
        font-size: clamp(1.7rem, 3vw, 2.55rem);
    
    /* Header Container */
        letter-spacing: 0;
        color: var(--ink);
        position: relative;
        z-index: 1;
        color: #ffffff;

        padding: 32px 40px;
        max-width: 720px;
        font-size: 0.98rem;
        color: var(--muted);
        margin-top: 0.65rem;
    }
        line-height: 1.6;
        position: relative;
        z-index: 1;
    .header-title {

        font-size: 2.2rem;
        font-weight: 800;
        gap: 0.55rem;
        margin-top: 1.35rem;
        color: #ffffff;
        position: relative;
        z-index: 1;
    }

    .header-subtitle {
        background: #f2f6f8;
        border: 1px solid #e0e8eb;
        color: #4c5c67;
        padding: 0.4rem 0.75rem;
        border-radius: 8px;
        font-size: 0.76rem;
        gap: 12px;
        margin-top: 16px;
        flex-wrap: wrap;
    h1, h2, h3, h4 {
        color: var(--ink);
        letter-spacing: 0;
        font-size: 0.82rem;

    h3 {
        margin-top: 0.4rem;
    }

    .block-container {
        max-width: 1440px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    }

        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        text-align: left;
        box-shadow: 0 6px 18px rgba(30, 45, 60, 0.04);
        min-height: 92px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 24px;
        font-size: 1.85rem;
    
        color: var(--ink);
        margin-top: 0.25rem;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        font-size: 0.72rem;
        padding: 20px;
        letter-spacing: 0.08em;
        color: var(--muted);
    }
    .metric-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
        font-weight: 700;
    }

    /* Risk Badges */
    .badge-high-risk {
        background-color: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
        padding: 8px 18px;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
    }
    .badge-medium-risk {
        background-color: #fffbeb;
        color: #d97706;
        border: 1px solid #fde68a;
        padding: 8px 18px;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
    }
    .badge-low-risk {
        background-color: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
        padding: 8px 18px;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
    }

    /* Form Section Headers */
    .form-section-title {
        font-size: 0.86rem;
        font-weight: 800;
        color: var(--teal);
        margin: 1.5rem 0 0.8rem;
        border-bottom: 1px solid var(--line);
        padding-bottom: 0.65rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    [data-testid="stForm"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 0.6rem 1.35rem 1.25rem;
        box-shadow: 0 8px 24px rgba(30, 45, 60, 0.04);
    }

    [data-baseweb="select"] > div,
    [data-testid="stNumberInput"] input,
    [data-testid="stFileUploaderDropzone"] {
        border-color: #d9e1e7;
        border-radius: 8px;
        background: #fcfdfd;
    }

    [data-testid="stFileUploaderDropzone"] {
        border: 1px dashed #b8c9ce;
        padding: 1.4rem;
    }

    .stButton>button {
        background: var(--teal);
        color: #ffffff;
        font-weight: 700;
        border-radius: 8px;
        border: none;
        padding: 0.65rem 1.15rem;
        box-shadow: 0 5px 12px rgba(8, 127, 115, 0.18);
        transition: transform 0.2s ease, background 0.2s ease;
    }
    .stButton>button:hover {
        background: #066b62;
        box-shadow: 0 7px 16px rgba(8, 127, 115, 0.24);
        transform: translateY(-1px);
    }

    [data-testid="stTabs"] button {
        color: var(--muted);
        font-weight: 700;
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--teal);
    }

    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background-color: var(--teal);
    }

    [data-testid="stAlert"] {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# Final visual overrides keep the workspace consistent across Streamlit versions.
st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"] { background: #f5f7f9; color: #17212b; }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background: #fbfcfd; border-right: 1px solid #e6ebf0; }
    [data-testid="stSidebar"] > div:first-child { padding: 2rem 1.25rem; }
    [data-testid="stSidebar"] h3 { color: #17212b; font-size: .8rem; letter-spacing: .08em; text-transform: uppercase; }
    .block-container { max-width: 1440px; padding-top: 2rem; padding-bottom: 3rem; }
    .header-banner { background: #fff; color: #17212b; padding: 2.35rem 2.6rem 2.2rem; border: 1px solid #e6ebf0; border-radius: 18px; box-shadow: 0 12px 30px rgba(30,45,60,.06); margin: .4rem 0 1.8rem; position: relative; overflow: hidden; }
    .header-banner::after { content: ""; position: absolute; width: 180px; height: 180px; border-radius: 50%; background: #e6f5f2; right: -55px; top: -70px; }
    .header-kicker { color: #087f73; font-size: .74rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin-bottom: .7rem; }
    .header-title, .header-subtitle, .header-badges { position: relative; z-index: 1; }
    .header-title { color: #17212b; font-size: clamp(1.7rem, 3vw, 2.55rem); font-weight: 800; letter-spacing: 0; margin: 0; }
    .header-subtitle { max-width: 720px; color: #687586; font-size: .98rem; font-weight: 500; line-height: 1.6; margin-top: .65rem; }
    .header-badges { display: flex; gap: .55rem; margin-top: 1.35rem; flex-wrap: wrap; }
    .pill-badge { background: #f2f6f8; border: 1px solid #e0e8eb; border-radius: 8px; color: #4c5c67; font-size: .76rem; font-weight: 600; padding: .4rem .75rem; }
    h1, h2, h3, h4 { color: #17212b; letter-spacing: 0; }
    .metric-card { background: #fff; border: 1px solid #e6ebf0; border-radius: 12px; box-shadow: 0 6px 18px rgba(30,45,60,.04); min-height: 92px; padding: 1.1rem 1.2rem; text-align: left; }
    .metric-label { color: #687586; font-size: .72rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
    .metric-value { color: #17212b; font-size: 1.85rem; font-weight: 800; margin-top: .25rem; }
    .form-section-title { border-bottom: 1px solid #e6ebf0; color: #087f73; font-size: .86rem; font-weight: 800; letter-spacing: .06em; margin: 1.5rem 0 .8rem; padding-bottom: .65rem; text-transform: uppercase; }
    [data-testid="stForm"] { background: #fff; border: 1px solid #e6ebf0; border-radius: 14px; box-shadow: 0 8px 24px rgba(30,45,60,.04); padding: .6rem 1.35rem 1.25rem; }
    [data-baseweb="select"] > div, [data-testid="stNumberInput"] input { background: #fcfdfd; border-color: #d9e1e7; border-radius: 8px; }
    [data-testid="stFileUploaderDropzone"] { background: #fcfdfd; border: 1px dashed #b8c9ce; border-radius: 10px; padding: 1.4rem; }
    .stButton > button { background: #087f73; border: 0; border-radius: 8px; box-shadow: 0 5px 12px rgba(8,127,115,.18); color: #fff; font-weight: 700; padding: .65rem 1.15rem; }
    .stButton > button:hover { background: #066b62; box-shadow: 0 7px 16px rgba(8,127,115,.24); transform: translateY(-1px); }
    [data-testid="stTabs"] button { color: #687586; font-weight: 700; }
    [data-testid="stTabs"] button[aria-selected="true"] { color: #087f73; }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: #087f73; }
    [data-testid="stAlert"] { border-radius: 10px; }
    @media (max-width: 700px) { .header-banner { padding: 1.6rem 1.25rem; } .block-container { padding: 1rem .8rem 2rem; } }
</style>
""", unsafe_allow_html=True)


# Render App Banner
st.markdown("""
<div class="header-banner">
    <div class="header-kicker">Customer retention workspace</div>
    <div class="header-title">Telecom churn intelligence</div>
    <div class="header-subtitle">Score individual customers, review the factors behind each prediction, and prioritize retention work with confidence.</div>
    <div class="header-badges">
        <span class="pill-badge">Keras DNN model</span>
        <span class="pill-badge">Decision threshold 0.45</span>
        <span class="pill-badge">SHAP explainability</span>
        <span class="pill-badge">REST API connected</span>
    </div>
</div>
""", unsafe_allow_html=True)


# Sidebar Backend Status Check
with st.sidebar:
    st.markdown("### Workspace status")
    try:
        health_resp = api_client.check_health()
        st.success("🟢 Backend API Online")
        st.caption(f"**API Endpoint**: `{api_client.BACKEND_URL}`")
        st.caption(f"**Classification Threshold**: `{health_resp.get('classification_threshold', 0.45)}`")
    except api_client.APIError as err:
        st.error("🔴 Backend Service Offline")
        st.warning("Please launch Flask backend service:\n`python -m backend.app`")
        st.stop()


# Fetch Feature Metadata from Backend
try:
    feat_resp = api_client.get_features()
    feature_metadata = feat_resp.get("features", [])
    feat_dict = {f["name"]: f for f in feature_metadata}
except Exception as e:
    st.error(f"Failed to fetch feature metadata from backend API: {str(e)}")
    st.stop()


# ------------------ Navigation Tabs ------------------
tab1, tab2, tab3 = st.tabs([
    "Single customer",
    "Batch scoring",
    "Model insights"
])


# ==========================================
# TAB 1: Single Customer Evaluator
# ==========================================
with tab1:
    st.markdown("### 👤 Single Customer Churn Risk Evaluator")
    st.write("Configure customer attributes across Demographics, Services, and Billing to evaluate churn risk.")

    with st.form(key="single_customer_form_v2"):
        form_inputs = {}

        # Section 1: Customer Profile
        st.markdown('<div class="form-section-title">1. Customer Demographics</div>', unsafe_allow_html=True)
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)

        with col_d1:
            meta = feat_dict["gender"]
            form_inputs["gender"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=0)
        with col_d2:
            meta = feat_dict["SeniorCitizen"]
            form_inputs["SeniorCitizen"] = st.selectbox(meta["display_name"], options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No", index=0)
        with col_d3:
            meta = feat_dict["Partner"]
            form_inputs["Partner"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=1)
        with col_d4:
            meta = feat_dict["Dependents"]
            form_inputs["Dependents"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=1)

        st.markdown("<br>", unsafe_allow_html=True)

        # Section 2: Services Subscribed
        st.markdown('<div class="form-section-title">2. Telecommunication Services</div>', unsafe_allow_html=True)
        col_s1, col_s2, col_s3 = st.columns(3)

        with col_s1:
            meta = feat_dict["PhoneService"]
            form_inputs["PhoneService"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=0)
            meta = feat_dict["MultipleLines"]
            form_inputs["MultipleLines"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=1)
            meta = feat_dict["InternetService"]
            form_inputs["InternetService"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=1)

        with col_s2:
            meta = feat_dict["OnlineSecurity"]
            form_inputs["OnlineSecurity"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=0)
            meta = feat_dict["OnlineBackup"]
            form_inputs["OnlineBackup"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=0)
            meta = feat_dict["DeviceProtection"]
            form_inputs["DeviceProtection"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=0)

        with col_s3:
            meta = feat_dict["TechSupport"]
            form_inputs["TechSupport"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=0)
            meta = feat_dict["StreamingTV"]
            form_inputs["StreamingTV"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=0)
            meta = feat_dict["StreamingMovies"]
            form_inputs["StreamingMovies"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=0)

        st.markdown("<br>", unsafe_allow_html=True)

        # Section 3: Billing & Contract Details
        st.markdown('<div class="form-section-title">3. Account, Contract & Billing</div>', unsafe_allow_html=True)
        col_b1, col_b2, col_b3, col_b4, col_b5, col_b6 = st.columns(6)

        with col_b1:
            meta = feat_dict["tenure"]
            form_inputs["tenure"] = st.number_input(meta["display_name"], min_value=0, max_value=72, value=int(meta["default"]), step=1)
        with col_b2:
            meta = feat_dict["Contract"]
            form_inputs["Contract"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=0)
        with col_b3:
            meta = feat_dict["PaperlessBilling"]
            form_inputs["PaperlessBilling"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=0)
        with col_b4:
            meta = feat_dict["PaymentMethod"]
            form_inputs["PaymentMethod"] = st.selectbox(meta["display_name"], options=meta["allowed_values"], index=0)
        with col_b5:
            meta = feat_dict["MonthlyCharges"]
            form_inputs["MonthlyCharges"] = st.number_input(meta["display_name"], min_value=18.0, max_value=150.0, value=float(meta["default"]), step=1.0)
        with col_b6:
            meta = feat_dict["TotalCharges"]
            form_inputs["TotalCharges"] = st.number_input(meta["display_name"], min_value=0.0, max_value=10000.0, value=float(meta["default"]), step=10.0)

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚀 Compute Prediction & Local SHAP Attribution", use_container_width=True)

    if submit_btn:
        with st.spinner("Processing inference & SHAP explainability via REST API..."):
            try:
                response = api_client.predict_single_with_explain(form_inputs)
                pred_data = response.get("prediction", {})
                explain_data = response.get("explanation", {})

                st.markdown("---")
                col_res1, col_res2 = st.columns([1, 1.3])

                with col_res1:
                    prob = pred_data.get("churn_probability", 0.0)
                    risk = pred_data.get("risk_level", "Unknown")
                    label = pred_data.get("churn_label", "No")

                    st.markdown("#### Prediction Result & Churn Risk Score")

                    # Badge UI
                    badge_style = "badge-high-risk" if risk == "High Risk" else ("badge-medium-risk" if risk == "Medium Risk" else "badge-low-risk")
                    st.markdown(f'<div class="{badge_style}">Risk Status: {risk.upper()}</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Plotly Light Gauge Chart
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=prob * 100,
                        number={"suffix": "%", "font": {"size": 38, "color": "#0f172a", "family": "Plus Jakarta Sans"}},
                        title={
                            "text": f"Churn Probability (Threshold = 0.45)<br><b style='color:{'#dc2626' if label=='Yes' else '#059669'}'>PREDICTION: {'LIKELY TO CHURN' if label=='Yes' else 'LIKELY TO RETAIN'}</b>",
                            "font": {"size": 15, "color": "#475569"}
                        },
                        gauge={
                            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#cbd5e1"},
                            "bar": {"color": "#dc2626" if prob >= 0.45 else "#059669"},
                            "bgcolor": "#ffffff",
                            "borderwidth": 1,
                            "bordercolor": "#e2e8f0",
                            "steps": [
                                {"range": [0, 45], "color": "#f0fdf4"},
                                {"range": [45, 70], "color": "#fefce8"},
                                {"range": [70, 100], "color": "#fef2f2"}
                            ],
                            "threshold": {
                                "line": {"color": "#d97706", "width": 4},
                                "thickness": 0.8,
                                "value": 45
                            }
                        }
                    ))
                    fig_gauge.update_layout(
                        paper_bgcolor="#ffffff",
                        plot_bgcolor="#ffffff",
                        font={"color": "#1e293b"},
                        height=290,
                        margin=dict(l=25, r=25, t=60, b=20)
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with col_res2:
                    st.markdown("#### Local SHAP Feature Contribution")
                    st.write("Top feature influences pushing customer toward Churn (Red) or Retention (Green):")

                    all_shap = explain_data.get("all_shap_values", [])
                    if all_shap:
                        df_shap = pd.DataFrame(all_shap[:10])

                        fig_shap = px.bar(
                            df_shap,
                            x="shap_value",
                            y="feature",
                            orientation="h",
                            color="impact",
                            color_discrete_map={"churn": "#ef4444", "stay": "#10b981"},
                            labels={"shap_value": "SHAP Contribution Value", "feature": "Transformed Feature"},
                            title=f"Local Feature Attribution ({explain_data.get('explainer_type', 'SHAP Engine')})"
                        )
                        fig_shap.update_layout(
                            template="plotly_white",
                            paper_bgcolor="#ffffff",
                            plot_bgcolor="#ffffff",
                            font={"color": "#1e293b", "family": "Plus Jakarta Sans"},
                            yaxis={"autorange": "reversed"},
                            height=340,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig_shap, use_container_width=True)
                    else:
                        st.info("Local SHAP feature contributions unavailable.")

            except api_client.APIError as err:
                st.error(f"Prediction Error: {err.message}")
                if err.details:
                    st.json(err.details)


# ==========================================
# TAB 2: Batch CSV Risk Scoring
# ==========================================
with tab2:
    st.markdown("### 📁 Batch CSV Customer Risk Scoring")
    st.write("Upload customer batch CSV files to execute automated predictions, schema validation, and on-demand explanations.")

    uploaded_file = st.file_uploader("Upload Batch Customer CSV File", type=["csv"], key="batch_csv_uploader_v2")

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        filename = uploaded_file.name

        with st.spinner("Executing batch validation and model inference via API..."):
            try:
                batch_response = api_client.predict_batch(file_bytes, filename)
                total_records = batch_response.get("total_records", 0)
                predictions = batch_response.get("predictions", [])

                if predictions:
                    res_df = pd.DataFrame(predictions)
                    st.success(f"Successfully processed {total_records} customer records!")

                    # Summary Metrics Row
                    churn_count = int((res_df["churn_prediction"] == 1).sum())
                    churn_pct = round((churn_count / total_records) * 100, 1) if total_records > 0 else 0
                    high_risk_count = int((res_df["risk_level"] == "High Risk").sum())

                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Customers</div><div class="metric-value">{total_records}</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.markdown(f'<div class="metric-card"><div class="metric-label">Predicted Churns</div><div class="metric-value" style="color:#dc2626;">{churn_count}</div></div>', unsafe_allow_html=True)
                    with m3:
                        st.markdown(f'<div class="metric-card"><div class="metric-label">Churn Rate</div><div class="metric-value">{churn_pct}%</div></div>', unsafe_allow_html=True)
                    with m4:
                        st.markdown(f'<div class="metric-card"><div class="metric-label">High Risk Tier</div><div class="metric-value" style="color:#d97706;">{high_risk_count}</div></div>', unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Table Column Reordering
                    cols = list(res_df.columns)
                    priority = ["customerID", "churn_probability", "risk_level", "churn_label"]
                    exist_p = [c for c in priority if c in cols]
                    others = [c for c in cols if c not in exist_p]
                    final_cols = exist_p + others

                    st.markdown("#### Batch Results Data Table")
                    st.dataframe(res_df[final_cols], use_container_width=True, height=360)

                    # Download CSV Button
                    csv_bytes = res_df[final_cols].to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Download Batch Prediction Results (CSV)",
                        data=csv_bytes,
                        file_name="telco_churn_batch_results.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                    st.markdown("---")
                    st.markdown("#### 🔍 On-Demand Batch Row SHAP Inspector")
                    st.write("Select any customer row index from the batch dataset to fetch detailed SHAP feature attributions.")

                    row_idx = st.number_input(
                        "Select Batch Row Index (0 to total records - 1)",
                        min_value=0,
                        max_value=max(0, total_records - 1),
                        value=0,
                        step=1
                    )

                    if st.button("Generate Explanation for Selected Row"):
                        row_customer = res_df.iloc[row_idx].to_dict()
                        # Exclude generated prediction outputs before sending payload
                        clean_payload = {k: v for k, v in row_customer.items() if k in feat_dict}

                        with st.spinner(f"Computing SHAP explanation for row {row_idx}..."):
                            try:
                                row_exp = api_client.explain_batch_row(clean_payload, int(row_idx))
                                row_attributions = row_exp.get("all_shap_values", [])

                                if row_attributions:
                                    df_row_att = pd.DataFrame(row_attributions[:10])
                                    fig_row = px.bar(
                                        df_row_att,
                                        x="shap_value",
                                        y="feature",
                                        orientation="h",
                                        color="impact",
                                        color_discrete_map={"churn": "#ef4444", "stay": "#10b981"},
                                        title=f"SHAP Attribution for Row Index {row_idx} (Churn Prob: {row_exp.get('prediction_probability', 'N/A')})"
                                    )
                                    fig_row.update_layout(
                                        template="plotly_white",
                                        paper_bgcolor="#ffffff",
                                        plot_bgcolor="#ffffff",
                                        font={"color": "#1e293b"},
                                        yaxis={"autorange": "reversed"},
                                        height=340
                                    )
                                    st.plotly_chart(fig_row, use_container_width=True)
                            except api_client.APIError as err:
                                st.error(f"Row Explanation Error: {err.message}")

            except api_client.APIError as err:
                st.error(f"Batch Processing Error: {err.message}")
                if err.details:
                    st.warning("CSV Validation Failures Detected:")
                    st.json(err.details)


# ==========================================
# TAB 3: Model Insights & Benchmarks
# ==========================================
with tab3:
    st.markdown("### 📊 Model Architecture, Metrics & Industry Benchmarks")

    with st.spinner("Fetching model insights from backend API..."):
        try:
            insights = api_client.get_model_insights()

            # 1. Test Metrics Dashboard
            st.markdown("#### 🎯 Optimized DNN Performance Metrics (Threshold = 0.45)")
            metrics = insights.get("metrics_table", {})

            k1, k2, k3, k4, k5 = st.columns(5)
            with k1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Accuracy</div><div class="metric-value">{metrics.get("Accuracy", 0):.4f}</div></div>', unsafe_allow_html=True)
            with k2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Precision</div><div class="metric-value">{metrics.get("Precision", 0):.4f}</div></div>', unsafe_allow_html=True)
            with k3:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Recall</div><div class="metric-value" style="color:#2563eb;">{metrics.get("Recall", 0):.4f}</div></div>', unsafe_allow_html=True)
            with k4:
                st.markdown(f'<div class="metric-card"><div class="metric-label">F1-Score</div><div class="metric-value">{metrics.get("F1", 0):.4f}</div></div>', unsafe_allow_html=True)
            with k5:
                st.markdown(f'<div class="metric-card"><div class="metric-label">ROC-AUC</div><div class="metric-value" style="color:#059669;">{metrics.get("ROC_AUC", 0):.4f}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # 2. Benchmark Comparison Table & Architecture Summary
            c_left, c_right = st.columns([1.2, 1])

            with c_left:
                st.markdown("#### ⚔️ Model Benchmark Comparison")
                comp_list = insights.get("model_comparison_table", [])
                if comp_list:
                    df_comp = pd.DataFrame(comp_list)
                    st.dataframe(df_comp, use_container_width=True)
                    st.caption("*The Optimized DNN was selected for superior Recall (0.6631) and ROC-AUC (0.8397), ensuring maximum detection of at-risk customers.*")

            with c_right:
                st.markdown("#### 🧠 Neural Network Architecture")
                arch = insights.get("architecture_summary", {})
                st.info(f"""
                - **Model Architecture**: {arch.get('model_name', 'DNN')}
                - **Hidden Layers**: Dense(64) → Dense(32) → Dense(16) → Dense(1)
                - **Regularization**: Dropout (0.5 per layer) + Batch Normalization
                - **Optimizer**: Adam (learning_rate = 0.0003)
                - **Classification Threshold**: {arch.get('classification_threshold', 0.45)}
                """)

            st.markdown("---")

            # 3. Global SHAP Importance Chart
            st.markdown("#### 🌐 Global Feature Importance (SHAP)")
            st.write("Mean absolute SHAP value impact across training population features:")

            global_shap = insights.get("global_shap_importance", [])
            if global_shap:
                df_glob = pd.DataFrame(global_shap[:12])
                fig_glob = px.bar(
                    df_glob,
                    x="importance",
                    y="feature",
                    orientation="h",
                    color="importance",
                    color_continuous_scale="Blues",
                    title="Top Global Predictors of Churn Risk"
                )
                fig_glob.update_layout(
                    template="plotly_white",
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    font={"color": "#1e293b", "family": "Plus Jakarta Sans"},
                    yaxis={"autorange": "reversed"},
                    height=380
                )
                st.plotly_chart(fig_glob, use_container_width=True)

            st.markdown("---")

            # 4. Model Limitations
            st.markdown("#### ⚠️ Operational Boundaries & Limitations")
            limits = insights.get("model_limitations", [])
            for lim in limits:
                st.warning(f"• {lim}")

        except api_client.APIError as err:
            st.error(f"Failed to fetch model insights: {err.message}")
