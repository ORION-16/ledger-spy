import streamlit as st
import pandas as pd

def render_anomaly():
    st.markdown("""<style>
    .card { background-color: #161b22; border: 1px solid #2a2f36; border-radius: 12px; padding: 20px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-header { color: #00c2ff; font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem; border-bottom: 1px solid #2a2f36; padding-bottom: 0.5rem; }
    .metric-label { font-size: 0.85rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; font-weight: 600; }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #ff7b72; line-height: 1.2; }
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-header">Anomaly Detection</div><p style="color:#8b949e; font-size:0.9rem; margin:0;">Identify statistical deviations and unusual transaction patterns.</p></div>', unsafe_allow_html=True)
    
    df_anomaly = st.session_state.get("anomalies")
    
    if df_anomaly is None or "is_anomaly" not in df_anomaly.columns:
        st.info("No anomaly data available.")
        return
        
    total_transactions = len(df_anomaly)
    total_anomalies = int(df_anomaly["is_anomaly"].sum())
    pct_anomalies = (total_anomalies / total_transactions * 100) if total_transactions > 0 else 0
    
    metrics_html = f"""
    <div style="display: flex; gap: 20px; margin-bottom: 20px;">
        <div class="card" style="flex: 1; margin: 0; border-left: 4px solid #ff7b72;">
            <div class="metric-label">Flagged Anomalies</div>
            <div class="metric-value">{total_anomalies:,}</div>
        </div>
        <div class="card" style="flex: 1; margin: 0;">
            <div class="metric-label">Percentage Flagged</div>
            <div class="metric-value" style="color: #e6edf3;">{pct_anomalies:.2f}%</div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)
    
    st.markdown('<div class="card"><div class="card-header">Flagged Transactions</div></div>', unsafe_allow_html=True)
    
    def highlight_anomaly(row):
        if row.get("is_anomaly", False):
            return ['background-color: rgba(255, 123, 114, 0.15); color: #ff7b72;'] * len(row)
        return [''] * len(row)
        
    styled_df = df_anomaly.style.apply(highlight_anomaly, axis=1)
    st.dataframe(styled_df, use_container_width=True)
