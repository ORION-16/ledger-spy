import streamlit as st

def render_dashboard():
    st.markdown("""<style>
    .card { background-color: #161b22; border: 1px solid #2a2f36; border-radius: 12px; padding: 20px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-header { color: #00c2ff; font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem; border-bottom: 1px solid #2a2f36; padding-bottom: 0.5rem; }
    .metric-label { font-size: 0.85rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; font-weight: 600; }
    .metric-value { font-size: 2.5rem; font-weight: 700; color: #e6edf3; line-height: 1.2; }
    .mono-block { font-family: 'Courier New', monospace; background-color: #0d1117; border: 1px solid #30363d; padding: 20px; border-radius: 8px; color: #79c0ff; white-space: pre-wrap; font-size: 0.95rem; line-height: 1.5; }
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-header">LedgerSpy Executive Dashboard</div><p style="color:#8b949e; font-size:0.9rem; margin:0;">Intelligence overview for current audit engagement.</p></div>', unsafe_allow_html=True)
    
    risk_scores = st.session_state.get("risk_scores", {})
    
    total_tx = risk_scores.get("total", 0)
    anomalies_count = risk_scores.get("anomaly_count", 0)
    overall_risk = risk_scores.get("overall_risk", "N/A")
    
    risk_color = "#00c2ff"
    if overall_risk == "High":
        risk_color = "#ff7b72"
    elif overall_risk == "Medium":
        risk_color = "#d29922"
    elif overall_risk == "Low":
        risk_color = "#3fb950"
        
    metrics_html = f"""
    <div style="display: flex; gap: 20px; margin-bottom: 20px;">
        <div class="card" style="flex: 1; margin: 0; text-align: center;">
            <div class="metric-label">Total Transactions</div>
            <div class="metric-value">{total_tx:,}</div>
        </div>
        <div class="card" style="flex: 1; margin: 0; text-align: center; border-bottom: 3px solid #ff7b72;">
            <div class="metric-label">Anomalies Detected</div>
            <div class="metric-value" style="color: #ff7b72;">{anomalies_count:,}</div>
        </div>
        <div class="card" style="flex: 1; margin: 0; text-align: center; border-bottom: 3px solid {risk_color};">
            <div class="metric-label">Overall Risk Level</div>
            <div class="metric-value" style="color: {risk_color};">{overall_risk}</div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)
    
    st.markdown('<div class="card"><div class="card-header">Audit Memo</div></div>', unsafe_allow_html=True)
    audit_memo = st.session_state.get("audit_memo", "No memo generated.")
    
    st.markdown(f'<div class="mono-block">{audit_memo}</div>', unsafe_allow_html=True)
