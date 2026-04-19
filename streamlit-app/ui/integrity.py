import streamlit as st

def render_integrity():
    
    st.markdown("""
    <div class="card">
        <h3>Data Integrity Dashboard</h3>
        <p>Data quality metrics and readiness</p>
    </div>
    """, unsafe_allow_html=True)
    
    readiness = st.session_state.get("readiness")
    if not readiness:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('''
            <div class="notice-box">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px; filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.4));"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
<div class="notice-box-title">No Dataset Loaded</div>
                <div class="notice-box-subtitle">Navigate to the Upload & Preview section to begin.</div>
            </div>
            ''', unsafe_allow_html=True)
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
