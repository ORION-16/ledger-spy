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
