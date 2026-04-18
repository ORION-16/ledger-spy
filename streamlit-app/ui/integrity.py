import streamlit as st

def render_integrity():
    st.markdown("""<style>
    .card { background-color: #161b22; border: 1px solid #2a2f36; border-radius: 12px; padding: 20px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-header { color: #00c2ff; font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem; border-bottom: 1px solid #2a2f36; padding-bottom: 0.5rem; }
    .metric-label { font-size: 0.85rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; font-weight: 600; }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #e6edf3; line-height: 1.2; }
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-header">Data Integrity Dashboard</div><p style="color:#8b949e; font-size:0.9rem; margin:0;">Data quality metrics and readiness</p></div>', unsafe_allow_html=True)
    
    readiness = st.session_state.get("readiness")
    if not readiness:
        st.info("No data available.")
        return
        
    score = readiness.get('score', 0.0)
    null_pct = readiness.get('null_pct', readiness.get('nulls', 0.0))
    dup_pct = readiness.get('dup_pct', readiness.get('duplicates', 0.0))
    cols = readiness.get('col_count', readiness.get('columns', 'N/A'))
    
    score_color = "#00c2ff" if score >= 80 else "#ff7b72"
    
    score_html = f"""
    <div class="card" style="text-align: center;">
        <div class="metric-label">Data Quality Score</div>
        <div class="metric-value" style="color: {score_color}; font-size: 3rem;">{score:.1f}%</div>
    </div>
    """
    st.markdown(score_html, unsafe_allow_html=True)
    
    metrics_html = f"""
    <div style="display: flex; gap: 20px; margin-bottom: 20px;">
        <div class="card" style="flex: 1; margin: 0; text-align: center;">
            <div class="metric-label">Missing Values</div>
            <div class="metric-value">{null_pct:.2f}%</div>
        </div>
        <div class="card" style="flex: 1; margin: 0; text-align: center;">
            <div class="metric-label">Duplicate Rows</div>
            <div class="metric-value">{dup_pct:.2f}%</div>
        </div>
        <div class="card" style="flex: 1; margin: 0; text-align: center;">
            <div class="metric-label">Column Count</div>
            <div class="metric-value">{cols}</div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)
