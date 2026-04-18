import streamlit as st
import pandas as pd

def render_anomaly():
    st.markdown('''<style>
    /* Force Global Dark Mode to override Streamlit light theme */
    .stApp { background-color: #0e1117; color: #e6edf3; }
    
    /* Target Streamlit Metrics to look like React Cards */
    [data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #2a2f36;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Target Metric Labels */
    [data-testid="stMetricLabel"] > div > div > p {
        color: #8b949e !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Target Metric Values */
    [data-testid="stMetricValue"] > div {
        color: #00c2ff !important;
        font-weight: 700;
        font-size: 2.2rem;
    }

    /* Target Dataframes */
    [data-testid="stDataFrame"] {
        background-color: #161b22;
        border: 1px solid #2a2f36;
        border-radius: 12px;
        padding: 10px;
    }

    /* Shared Card Titles (Injected HTML) */
    .card { background-color: #161b22; border: 1px solid #2a2f36; border-radius: 12px; padding: 20px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card h3 { color: #00c2ff; font-weight: 600; font-size: 1.2rem; margin-top: 0; margin-bottom: 0.5rem; border-bottom: 1px solid #2a2f36; padding-bottom: 0.5rem; }
    .card p { color: #8b949e; font-size: 0.9rem; margin: 0; }
    
    /* Audit Memo Block */
    .mono-block { font-family: 'Courier New', monospace; background-color: #0d1117; border: 1px solid #30363d; padding: 20px; border-radius: 8px; color: #79c0ff; white-space: pre-wrap; font-size: 0.95rem; line-height: 1.5; }
    </style>''', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h3>Anomaly Detection</h3>
        <p>Identify statistical deviations and unusual transaction patterns.</p>
    </div>
    """, unsafe_allow_html=True)
    
    df_anomaly = st.session_state.get("anomalies")
    if df_anomaly is None or "is_anomaly" not in df_anomaly.columns:
        st.info("No anomaly data available.")
        return
        
    total_transactions = len(df_anomaly)
    total_anomalies = int(df_anomaly["is_anomaly"].sum())
    pct_anomalies = (total_anomalies / total_transactions * 100) if total_transactions > 0 else 0
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Flagged Anomalies", f"{total_anomalies:,}")
        with col2:
            st.metric("Percentage Flagged", f"{pct_anomalies:.2f}%")
            
    st.markdown("""
    <div class="card">
        <h3>Flagged Transactions</h3>
    </div>
    """, unsafe_allow_html=True)
    
    def highlight_anomaly(row):
        if row.get("is_anomaly", False):
            return ['background-color: rgba(255, 123, 114, 0.15); color: #ff7b72;'] * len(row)
        return [''] * len(row)
        
    styled_df = df_anomaly.style.apply(highlight_anomaly, axis=1)
    st.dataframe(styled_df, use_container_width=True)
