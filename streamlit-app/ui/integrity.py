import streamlit as st

def render_integrity():
    st.markdown("""<style>
    .card { background-color: #161b22; border: 1px solid #2a2f36; border-radius: 12px; padding: 20px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card h3 { color: #00c2ff; font-weight: 600; font-size: 1.2rem; margin-top: 0; margin-bottom: 0.5rem; border-bottom: 1px solid #2a2f36; padding-bottom: 0.5rem; }
    .card p { color: #8b949e; font-size: 0.9rem; margin: 0; }
    </style>""", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h3>Data Integrity Dashboard</h3>
        <p>Data quality metrics and readiness</p>
    </div>
    """, unsafe_allow_html=True)
    
    readiness = st.session_state.get("readiness")
    if not readiness:
        st.info("No data available.")
        return
        
    score = readiness.get('score', 0.0)
    null_pct = readiness.get('null_pct', readiness.get('nulls', 0.0))
    dup_pct = readiness.get('dup_pct', readiness.get('duplicates', 0.0))
    cols = readiness.get('col_count', readiness.get('columns', 'N/A'))
    
    with st.container():
        st.metric("Data Quality Score", f"{score:.1f}%")
        
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Missing Values", f"{null_pct:.2f}%")
        with col2:
            st.metric("Duplicate Rows", f"{dup_pct:.2f}%")
        with col3:
            st.metric("Column Count", cols)
