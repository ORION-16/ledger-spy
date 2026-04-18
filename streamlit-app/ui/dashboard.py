import streamlit as st

def render_dashboard():
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
        <h3>LedgerSpy Executive Dashboard</h3>
        <p>Intelligence overview for current audit engagement.</p>
    </div>
    """, unsafe_allow_html=True)
    
    risk_scores = st.session_state.get("risk_scores", {})
    
    total_tx = risk_scores.get("total", 0)
    anomalies_count = risk_scores.get("anomaly_count", 0)
    overall_risk = risk_scores.get("overall_risk", "N/A")
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Transactions", f"{total_tx:,}")
        with col2:
            st.metric("Anomalies Detected", f"{anomalies_count:,}")
        with col3:
            st.metric("Overall Risk Level", overall_risk)
    
    st.markdown("""
    <div class="card">
        <h3>Audit Memo</h3>
    </div>
    """, unsafe_allow_html=True)
    
    audit_memo = st.session_state.get("audit_memo", "No memo generated.")
    st.markdown(f'<div class="mono-block">{audit_memo}</div>', unsafe_allow_html=True)
