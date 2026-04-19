import sys
import os
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

# Task 1: Safe Import for Data Integrity
try:
    from ml.fea_dataintegrity.data_integrity import compute_data_integrity
except Exception:
    compute_data_integrity = None

import streamlit as st
import pandas as pd

# ML imports with stub fallback
from ml.fea_anomaly.anomaly import detect_anomalies
from ml.fea_benford.benford import benford_analysis
from ml.fea_fuzzy.fuzzy import find_similar_vendors
from ml.stubs import build_risk_graph, explain_risk, compute_readiness_score, generate_memo
from ml.audit_memo import generate_audit_memo

# UI imports
from ui.upload import render_upload
from ui.integrity import render_integrity
try:
    from ui.anomaly import render_anomaly
except ImportError:
    def render_anomaly(): st.warning("Anomaly UI unavailable. Install required UI dependencies (e.g., plotly).", icon="🚧")
from ui.fuzzy import render_fuzzy
try:
    from ui.benford import render_benford
except ImportError:
    def render_benford(): st.warning("Benford UI not implemented yet.", icon="🚧")
try:
    from ui.risk_map import render_risk_map
except ImportError:
    def render_risk_map(): st.warning("Risk Map UI not implemented yet.", icon="🚧")
try:
    from ui.explainability import render_explainability
except ImportError:
    def render_explainability(): st.warning("Explainability UI not implemented yet.", icon="🚧")
try:
    from ui.dashboard import render_dashboard
except ImportError:
    def render_dashboard(): st.warning("Dashboard UI unavailable. Install required UI dependencies (e.g., plotly).", icon="🚧")
try:
    from ui.reconciliation import render_reconciliation
except ImportError:
    def render_reconciliation(): st.warning("Reconciliation UI not implemented yet.", icon="🚧")
try:
    from ui.benchmark_page import render_benchmark
except ImportError:
    def render_benchmark(): st.warning("Benchmark UI not implemented yet.", icon="🚧")
try:
    from ui.simulation import render_simulation
except ImportError:
    def render_simulation(): st.warning("Simulation UI not implemented yet.", icon="🚧")

from ui.styles import apply_global_styles

st.set_page_config(page_title="LedgerSpy", layout="wide", page_icon="🔍")
apply_global_styles()

st.sidebar.image("https://via.placeholder.com/150x50?text=LedgerSpy", width=150)
st.sidebar.title("🔍 LedgerSpy")
st.sidebar.caption("Air-Gapped Forensic Auditing")
st.sidebar.divider()

section = st.sidebar.radio("Navigate", [
    "📤 Upload & Preview",
    "📋 Data Integrity",
    "📊 Benford's Law",
    "🚨 Anomaly Detection",
    "🔗 Fuzzy Vendor Match",
    "🏦 Reconciliation",
    "🕸️ Relational Risk Map",
    "🧠 Explainable Risk",
    "📝 Dashboard & Memo",
    "📈 Monte Carlo Stress Test",
    "🏦 Industry Benchmark",
])

uploaded_file = st.sidebar.file_uploader("Upload Ledger CSV", type=["csv"])

if uploaded_file:
    with st.spinner("Processing Dataset & Executing Machine Learning Models..."):
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.lower()
        st.session_state["df"] = df

        # Task 3: Replace assignment logic
        if compute_data_integrity:
            integrity = compute_data_integrity(df)
            st.session_state["readiness"] = integrity
        else:
            # fallback to existing logic (DO NOT REMOVE)
            readiness_raw = compute_readiness_score(df)
            st.session_state["readiness"] = {
                "score": readiness_raw.get("score", 0.0),
                "null_pct": readiness_raw.get("null_pct", readiness_raw.get("nulls", 0.0)),
                "dup_pct": readiness_raw.get(
                    "dup_pct",
                    (readiness_raw.get("duplicates", 0) / len(df) * 100.0) if len(df) else 0.0,
                ),
                "col_count": readiness_raw.get("col_count", len(df.columns)),
            }

        anomaly_df = detect_anomalies(df)
        if not hasattr(anomaly_df, "columns"):
            anomaly_df = pd.DataFrame(anomaly_df)

        if "is_anomaly" not in anomaly_df.columns:
            anomaly_df["is_anomaly"] = False
        st.session_state["anomalies"] = anomaly_df
        st.session_state["benford"] = benford_analysis(df)
        st.session_state["vendors"] = find_similar_vendors(df)
        st.session_state["risk_graph"] = build_risk_graph(df)
        st.session_state["explanations"] = explain_risk(df)
        anomaly_count = int(st.session_state["anomalies"]["is_anomaly"].sum()) if "is_anomaly" in st.session_state["anomalies"].columns else 0
        st.session_state["risk_scores"] = {
            "total": len(df),
            "anomaly_count": anomaly_count,
            "overall_risk": "High" if anomaly_count > len(df) * 0.1 else "Medium"
        }

        try:
            st.session_state["audit_memo"] = generate_audit_memo(
                df,
                st.session_state.get("risk_scores", {}),
                st.session_state.get("readiness", {})
            )
        except Exception:
            st.session_state["audit_memo"] = None

        # --- Simulated Bank Reconciliation (Demo Mode) ---
        import numpy as np
        try:
            from ml.fea_reconcilation.recon import reconcile
            
            df_recon = df.copy()
            # Sandbox the schema so we don't pollute global df!
            df_recon.columns = df_recon.columns.str.strip().str.lower().str.replace(' ', '_')
            
            # Guarantee invoice_id for the merge
            if "invoice_id" not in df_recon.columns:
                df_recon["invoice_id"] = df_recon.index.astype(str)
                
            bank_df = df_recon.copy()
            bank_df["bank_txn_id"] = "BTX-" + bank_df.index.astype(str)
            
            if "amount" in bank_df.columns:
                bank_df["amount"] = pd.to_numeric(bank_df["amount"], errors="coerce").fillna(0)
                
                # Form realistic variations (PARTIAL)
                random_idx = bank_df.sample(frac=0.3, random_state=42).index
                bank_df.loc[random_idx, "amount"] *= np.random.uniform(0.8, 1.2, size=len(random_idx))
                
                # Form missing cases (MISSING)
                missing_idx = bank_df.sample(frac=0.2, random_state=1).index
                bank_df = bank_df.drop(missing_idx)
                
            rec_output = reconcile(df_recon, bank_df)
            
            if not hasattr(rec_output, "columns"):
                rec_output = pd.DataFrame(rec_output)
                
            if "status" not in rec_output.columns:
                # Safe fallback if status wasn't generated
                rec_output["status"] = rec_output.apply(
                    lambda row:
                        "MATCHED" if abs(row.get("amount_ledger", 0) - row.get("amount_bank", 0)) < 1
                        else "PARTIAL" if pd.notna(row.get("amount_bank"))
                        else "MISSING",
                    axis=1
                )
                
            st.session_state["reconciliation"] = rec_output
            st.session_state["reconciliation_simulated"] = True
        except Exception as e:
            print("RECONCILIATION ERROR:", e)
            st.session_state["reconciliation"] = None

# (Removed st.stop() so that UI layouts and empty states render even without a dataset)
if "df" not in st.session_state:
    st.info("👈 Upload a CSV from the sidebar to begin.")

if st.sidebar.checkbox("Debug"):
    st.write(st.session_state)
    
# Route to sections
section_name = section.split(" ", 1)[-1] if " " in section else section

# Show loader explicitly when navigating between pages
if "current_section" not in st.session_state or st.session_state["current_section"] != section:
    with st.spinner(f"Loading {section_name}..."):
        import time
        time.sleep(0.6)  # Add a slight delay to make the loader visible during fast page transitions
    st.session_state["current_section"] = section

with st.spinner(f"Rendering {section_name}..."):
    if section == "📤 Upload & Preview":
        render_upload()
    elif section == "📋 Data Integrity":
        render_integrity()
    elif section == "📊 Benford's Law":
        render_benford()
    elif section == "🚨 Anomaly Detection":
        render_anomaly()
    elif section == "🔗 Fuzzy Vendor Match":
        render_fuzzy()
    elif section == "🏦 Reconciliation":
        render_reconciliation()
    elif section == "🕸️ Relational Risk Map":
        render_risk_map()
    elif section == "🧠 Explainable Risk":
        render_explainability()
    elif section == "📝 Dashboard & Memo":
        render_dashboard()
    elif section == "📈 Monte Carlo Stress Test":
        render_simulation()
    elif section == "🏦 Industry Benchmark":
        render_benchmark()
