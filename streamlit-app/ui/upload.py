import streamlit as st

def render_upload():
    st.markdown("""<style>
    .card { background-color: #161b22; border: 1px solid #2a2f36; border-radius: 12px; padding: 20px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-header { color: #00c2ff; font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem; border-bottom: 1px solid #2a2f36; padding-bottom: 0.5rem; }
    .metric-label { font-size: 0.85rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; font-weight: 600; }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #e6edf3; line-height: 1.2; }
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-header">Upload & Preview</div><p style="color:#8b949e; font-size:0.9rem; margin:0;">Dataset schema and snapshot preview</p></div>', unsafe_allow_html=True)
    
    df = st.session_state.get("df")
    if df is None:
        return
        
    html_metrics = f"""
    <div style="display: flex; gap: 20px; margin-bottom: 20px;">
        <div class="card" style="flex: 1; margin: 0;">
            <div class="metric-label">Total Rows</div>
            <div class="metric-value">{df.shape[0]:,}</div>
        </div>
        <div class="card" style="flex: 1; margin: 0;">
            <div class="metric-label">Total Columns</div>
            <div class="metric-value">{df.shape[1]:,}</div>
        </div>
    </div>
    """
    st.markdown(html_metrics, unsafe_allow_html=True)
    
    st.markdown('<div class="card"><div class="card-header">Data Snapshot</div></div>', unsafe_allow_html=True)
    st.dataframe(df.head(100), use_container_width=True)
