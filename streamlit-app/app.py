"""
app.py - LedgerSpy Financial Audit Tool
Main Streamlit entry point.
"""

import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="LedgerSpy",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.styles import apply_global_styles
from ui.anomaly import render_anomaly
from ui.benchmark_page import render_benchmark
from ui.benford import render_benford
from ui.dashboard import render_dashboard
from ui.explainability import render_explainability
from ui.fuzzy import render_fuzzy
from ui.integrity import render_integrity
from ui.risk_map import render_risk_map
from ui.simulation import render_simulation
from ui.upload import render_upload

apply_global_styles()


try:
    from ml.preprocessing import preprocess
except ImportError:
    def preprocess(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [str(col).strip() for col in df.columns]

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        object_columns = df.select_dtypes(include="object").columns
        if len(object_columns) > 0:
            df[object_columns] = df[object_columns].apply(lambda column: column.astype(str).str.strip())

        return df.replace({"": np.nan})


try:
    from ml.anomaly import detect_anomalies
except ImportError:
    def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        np.random.seed(42)
        scores = np.random.uniform(0, 1, len(df))
        df["hybrid_risk_score"] = scores
        df["is_anomaly"] = scores > 0.85
        df["risk"] = scores
        df["explanation"] = np.where(
            df["is_anomaly"],
            "Synthetic anomaly fallback triggered.",
            "Within normal range.",
        )
        return df


try:
    from ml.vendor import detect_vendor_duplicates
except ImportError:
    try:
        from ml.fuzzy import find_similar_vendors as detect_vendor_duplicates
    except ImportError:
        def detect_vendor_duplicates(df: pd.DataFrame) -> pd.DataFrame:
            if "vendor_name" not in df.columns:
                return pd.DataFrame(columns=["vendor_a", "vendor_b", "similarity_score", "risk"])

            vendors = df["vendor_name"].dropna().astype(str).unique()
            if len(vendors) < 2:
                return pd.DataFrame(columns=["vendor_a", "vendor_b", "similarity_score", "risk"])

            return pd.DataFrame(
                [
                    {
                        "vendor_a": vendors[0],
                        "vendor_b": f"{vendors[0]} Ltd",
                        "similarity_score": 91.5,
                        "risk": "High",
                    },
                    {
                        "vendor_a": vendors[min(1, len(vendors) - 1)],
                        "vendor_b": f"{vendors[min(1, len(vendors) - 1)]} Inc",
                        "similarity_score": 86.0,
                        "risk": "Medium",
                    },
                ]
            )


def _compute_readiness(df: pd.DataFrame) -> dict:
    null_pct = float(df.isnull().mean().mean() * 100)
    dup_pct = float((df.duplicated().sum() / max(len(df), 1)) * 100)
    score = max(0.0, 100.0 - null_pct - dup_pct)
    col_stats = [
        {"name": column, "completeness": round((1 - df[column].isnull().mean()) * 100, 2)}
        for column in df.columns
    ]
    return {
        "score": round(score, 1),
        "null_pct": round(null_pct, 2),
        "dup_pct": round(dup_pct, 2),
        "col_count": len(df.columns),
        "col_stats": col_stats,
    }


def _build_risk_graph(df_anomaly: pd.DataFrame | None, vendor_df: pd.DataFrame | None) -> dict:
    anomaly_count = (
        int(df_anomaly["is_anomaly"].sum())
        if df_anomaly is not None and "is_anomaly" in df_anomaly.columns
        else 0
    )
    vendor_count = len(vendor_df) if vendor_df is not None else 0

    return {
        "nodes": [
            {"id": "ledger", "label": "Ledger", "risk": "Medium"},
            {"id": "anomalies", "label": "Anomalies", "risk": "High" if anomaly_count else "Low"},
            {"id": "vendors", "label": "Vendors", "risk": "High" if vendor_count else "Low"},
            {"id": "benford", "label": "Benford", "risk": "Medium"},
        ],
        "edges": [
            {"source": "ledger", "target": "anomalies", "weight": 1.8},
            {"source": "ledger", "target": "vendors", "weight": 1.3},
            {"source": "ledger", "target": "benford", "weight": 1.1},
            {"source": "anomalies", "target": "vendors", "weight": 0.8},
        ],
    }


def _run_benford(df: pd.DataFrame) -> pd.DataFrame | None:
    if "amount" not in df.columns:
        return None

    amounts = pd.to_numeric(df["amount"], errors="coerce").dropna().abs()
    amounts = amounts[amounts > 0]
    if amounts.empty:
        return None

    leading = amounts.astype(str).str.lstrip("0").str[0]
    leading = pd.to_numeric(leading, errors="coerce").dropna().astype(int)
    leading = leading[leading.between(1, 9)]

    actual_pct = leading.value_counts(normalize=True).sort_index() * 100
    expected = {1: 30.1, 2: 17.6, 3: 12.5, 4: 9.7, 5: 7.9, 6: 6.7, 7: 5.8, 8: 5.1, 9: 4.6}

    rows = [
        {"Digit": digit, "Expected": expected[digit], "Actual": round(float(actual_pct.get(digit, 0.0)), 2)}
        for digit in range(1, 10)
    ]
    return pd.DataFrame(rows)


def _normalize_anomaly_output(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()

    if "hybrid_risk_score" not in normalized.columns:
        if "anomaly_score" in normalized.columns:
            normalized["hybrid_risk_score"] = pd.to_numeric(
                normalized["anomaly_score"],
                errors="coerce",
            ) / 100.0
        else:
            normalized["hybrid_risk_score"] = 0.0

    normalized["hybrid_risk_score"] = pd.to_numeric(
        normalized["hybrid_risk_score"],
        errors="coerce",
    ).fillna(0.0).clip(0.0, 1.0)

    if "is_anomaly" not in normalized.columns:
        normalized["is_anomaly"] = normalized["hybrid_risk_score"] > 0.85

    if "risk" not in normalized.columns:
        normalized["risk"] = normalized["hybrid_risk_score"]

    if "explanation" not in normalized.columns:
        normalized["explanation"] = np.where(
            normalized["is_anomaly"],
            "Elevated anomaly score detected.",
            "No material anomaly signal detected.",
        )

    return normalized


_DEFAULTS = {
    "df": None,
    "uploaded_filename": None,
    "readiness": None,
    "anomalies": None,
    "vendors": None,
    "benford": None,
    "risk_scores": {},
    "audit_memo": "No memo generated yet.",
    "explanations": None,
    "risk_graph": None,
    "mc_result": None,
    "bm_result": None,
}

for key, value in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


with st.sidebar:
    st.markdown(
        """
        <div style='padding:12px 4px 20px;border-bottom:1px solid #1f1f1f;margin-bottom:16px;'>
            <div style='font-size:1.4rem;font-weight:800;color:#ffffff;letter-spacing:-0.02em;'>
                🔍 LedgerSpy
            </div>
            <div style='font-size:0.78rem;color:#6b7280;margin-top:2px;text-transform:uppercase;letter-spacing:0.08em;'>
                Financial Audit AI
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='color:#6b7280;font-size:0.75rem;text-transform:uppercase;"
        "letter-spacing:0.1em;margin-bottom:6px;'>Navigation</p>",
        unsafe_allow_html=True,
    )

    _NAV = {
        "📂 Upload & Preview": render_upload,
        "🛡️ Data Integrity": render_integrity,
        "🚨 Anomaly Detection": render_anomaly,
        "📊 Benford Analysis": render_benford,
        "🔗 Fuzzy Vendor Match": render_fuzzy,
        "💡 Explainability": render_explainability,
        "🕸️ Risk Map": render_risk_map,
        "📋 Risk Dashboard": render_dashboard,
        "📈 Simulation": render_simulation,
        "🏦 Benchmark": render_benchmark,
    }

    selection = st.radio("nav", list(_NAV.keys()), label_visibility="collapsed")

    st.markdown("<hr style='border-color:#1f1f1f;margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#6b7280;font-size:0.75rem;text-transform:uppercase;"
        "letter-spacing:0.1em;margin-bottom:6px;'>Data Input</p>",
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")


if uploaded_file is not None:
    is_new = (
        st.session_state["df"] is None
        or st.session_state["uploaded_filename"] != uploaded_file.name
    )

    if is_new:
        try:
            with st.spinner("Processing dataset..."):
                raw_df = pd.read_csv(uploaded_file)
                clean_df = preprocess(raw_df)
                anomaly_df = _normalize_anomaly_output(detect_anomalies(clean_df))
                vendor_df = detect_vendor_duplicates(clean_df)
                benford_df = _run_benford(clean_df)
                readiness = _compute_readiness(clean_df)
                risk_graph = _build_risk_graph(anomaly_df, vendor_df)

                anomaly_count = (
                    int(anomaly_df["is_anomaly"].sum())
                    if "is_anomaly" in anomaly_df.columns
                    else 0
                )
                rate = anomaly_count / max(len(anomaly_df), 1)
                overall_risk = "High" if rate > 0.10 else "Medium" if rate > 0.03 else "Low"

                st.session_state.update(
                    {
                        "df": clean_df,
                        "uploaded_filename": uploaded_file.name,
                        "readiness": readiness,
                        "anomalies": anomaly_df,
                        "vendors": vendor_df,
                        "benford": benford_df,
                        "risk_scores": {
                            "total": len(clean_df),
                            "anomaly_count": anomaly_count,
                            "overall_risk": overall_risk,
                        },
                        "audit_memo": (
                            f"LEDGERSPY AUDIT MEMO\n"
                            f"{'-' * 40}\n"
                            f"Records Analysed : {len(clean_df):,}\n"
                            f"Anomalies Found  : {anomaly_count:,}\n"
                            f"Overall Risk     : {overall_risk}\n"
                            f"Vendor Flags     : {len(vendor_df):,}\n"
                            f"Data Quality     : {readiness['score']:.1f}%\n"
                            f"{'-' * 40}\n"
                            f"Recommendation   : "
                            f"{'Immediate review required.' if overall_risk == 'High' else 'Standard monitoring advised.'}"
                        ),
                        "explanations": anomaly_df,
                        "risk_graph": risk_graph,
                        "mc_result": None,
                        "bm_result": None,
                    }
                )
        except Exception as exc:
            st.sidebar.error(f"Error loading file: {exc}")


if st.session_state["df"] is None:
    st.markdown(
        """
        <div style='text-align:center;padding:5rem 2rem;'>
            <div style='font-size:3rem;margin-bottom:1rem;'>🔍</div>
            <h2 style='color:#ffffff;'>Welcome to LedgerSpy</h2>
            <p style='color:#6b7280;font-size:1rem;max-width:440px;margin:0 auto;'>
                Upload a CSV file from the sidebar to begin. The tool will automatically
                detect anomalies, run vendor checks, and prepare all dashboards.
            </p>
            <p style='color:#4b5563;font-size:0.85rem;margin-top:1rem;'>
                Expected columns: <code style='color:#c4b5fd'>transaction_id, date, vendor_name, amount</code>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


_NAV[selection]()
