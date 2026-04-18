import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="LedgerSpy 🔍",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODULE IMPORTS & STUBS ---
# Try importing ML modules, fallback to inline stubs if they don't exist yet
try:
    from ml.utils import compute_readiness_score
except ImportError:
    def compute_readiness_score(df):
        null_avg = df.isnull().mean().mean() * 100
        dup_pct = (df.duplicated().sum() / len(df)) * 100
        score = max(0, 100 - (null_avg + dup_pct))
        return {
            "score": score,
            "null_pct": null_avg,
            "dup_pct": dup_pct,
            "col_count": len(df.columns)
        }

try:
    from ml.anomaly import detect_anomalies, benford_analysis
except ImportError:
    def detect_anomalies(df):
        df_out = df.copy()
        # Ensure we have an amount column for plotting
        if "amount" not in df_out.columns:
            num_cols = df_out.select_dtypes(include=[np.number]).columns
            if len(num_cols) > 0:
                df_out["amount"] = df_out[num_cols[0]]
            else:
                df_out["amount"] = np.random.uniform(10, 5000, size=len(df))
        
        np.random.seed(42)
        df_out["anomaly_score"] = np.random.uniform(0, 100, size=len(df))
        df_out["is_anomaly"] = df_out["anomaly_score"] > 85
        return df_out

    def benford_analysis(df):
        # Fake expected vs actual benford distribution
        digits = list(range(1, 10))
        expected = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]
        # Generate some fake actuals slightly off from expected
        actual = [max(0, e + np.random.uniform(-2, 2)) for e in expected]
        return pd.DataFrame({"Digit": digits, "Expected": expected, "Actual": actual})

try:
    from ml.fuzzy import find_similar_vendors, explain_risk, get_risk_scores
except ImportError:
    def find_similar_vendors(df):
        # Find string columns that might be vendors
        str_cols = df.select_dtypes(include=['object']).columns
        if len(str_cols) > 0:
            vendor_col = str_cols[0]
            vendors = df[vendor_col].dropna().unique()
            if len(vendors) >= 2:
                return pd.DataFrame([
                    {"vendor_a": str(vendors[0]), "vendor_b": str(vendors[1]) + " Inc", "similarity_score": 92.5, "risk": "High"},
                    {"vendor_a": str(vendors[0]) + " LLC", "vendor_b": str(vendors[0]) + " LTD", "similarity_score": 88.0, "risk": "Medium"},
                    {"vendor_a": "Vendor X", "vendor_b": "Vender X", "similarity_score": 95.0, "risk": "High"}
                ])
                
        return pd.DataFrame([
            {"vendor_a": "Acme Corp", "vendor_b": "Ackme Corp", "similarity_score": 92.5, "risk": "High"},
            {"vendor_a": "Global Tech", "vendor_b": "Global Technologies", "similarity_score": 88.0, "risk": "Medium"}
        ])
        
    def explain_risk(df):
        return [f"Transaction {i} flagged due to unusual matching patterns." for i in range(min(5, len(df)))]

    def get_risk_scores(df):
        return {
            "overall_risk": "Medium",
            "memo": f"LedgerSpy analyzed {len(df)} transactions. We identified potential risks primarily in vendor matching and slight deviations in Benford's law. Manual review recommended for {int(len(df) * 0.05)} transactions."
        }

# --- IMPORT UI COMPONENT RENDERERS ---
from ui.upload import render_upload
from ui.integrity import render_integrity
from ui.anomaly import render_anomaly
from ui.fuzzy import render_fuzzy
from ui.dashboard import render_dashboard

# --- SESSION STATE INITIALIZATION ---
if "df" not in st.session_state:
    st.session_state["df"] = None
if "uploaded_filename" not in st.session_state:
    st.session_state["uploaded_filename"] = None
if "readiness" not in st.session_state:
    st.session_state["readiness"] = None
if "df_anomaly" not in st.session_state:
    st.session_state["df_anomaly"] = None
if "benford_df" not in st.session_state:
    st.session_state["benford_df"] = None
if "vendor_matches" not in st.session_state:
    st.session_state["vendor_matches"] = None
if "risk_explanations" not in st.session_state:
    st.session_state["risk_explanations"] = None
if "risk_summary" not in st.session_state:
    st.session_state["risk_summary"] = None

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("LedgerSpy Navigation")
sections = {
    "Upload & Preview": render_upload,
    "Data Integrity Dashboard": render_integrity,
    "Anomaly Detection": render_anomaly,
    "Fuzzy Vendor Match": render_fuzzy,
    "Risk Dashboard": render_dashboard
}
selection = st.sidebar.radio("Go to", list(sections.keys()))

# --- GLOBAL FILE UPLOAD ---
st.sidebar.divider()
st.sidebar.header("Data Input")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    # Only load if changed
    if st.session_state["df"] is None or st.session_state["uploaded_filename"] != uploaded_file.name:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state["df"] = df
            st.session_state["uploaded_filename"] = uploaded_file.name
            
            # Pre-compute data that doesn't need a button press
            st.session_state["readiness"] = compute_readiness_score(df)
            st.session_state["vendor_matches"] = find_similar_vendors(df)
            st.session_state["risk_explanations"] = explain_risk(df)
            st.session_state["risk_summary"] = None
            
            # Reset explicit triggers
            st.session_state["df_anomaly"] = None
            st.session_state["benford_df"] = None
            
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")

# --- MAIN APP ROUTING ---
if st.session_state["df"] is None:
    st.info("👋 Welcome to LedgerSpy! Please upload a CSV file in the sidebar to begin.")
    st.stop()

# Trigger ML logic from UI interactions
if "run_anomaly" in st.session_state and st.session_state["run_anomaly"]:
    st.session_state["df_anomaly"] = detect_anomalies(st.session_state["df"])
    st.session_state["benford_df"] = benford_analysis(st.session_state["df"])
    st.session_state["run_anomaly"] = False # Reset trigger

# Trigger Risk Memo Generation
if "generate_memo" in st.session_state and st.session_state["generate_memo"]:
    st.session_state["risk_summary"] = get_risk_scores(st.session_state["df"])
    st.session_state["generate_memo"] = False

# Render selected section
sections[selection]()
