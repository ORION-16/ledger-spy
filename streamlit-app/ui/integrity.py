import streamlit as st

def render_integrity():
    st.header("Data Integrity Dashboard")
    st.caption("Review the health and readiness of the uploaded data.")
    st.divider()
    
    readiness = st.session_state.get("readiness")
    if not readiness:
        st.warning("No readiness data generated.")
        return
        
    st.subheader(f"Overall Readiness Score: {readiness['score']:.1f}%")
    st.progress(readiness['score'] / 100.0)
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Missing Values", f"{readiness['null_pct']:.2f}%", delta_color="inverse")
    with col2:
        st.metric("Duplicate Rows", f"{readiness['dup_pct']:.2f}%", delta_color="inverse")
    with col3:
        st.metric("Total Columns", readiness['col_count'])
    
    if readiness['score'] < 80:
        st.error("Data Quality is low. Proceed with caution when analyzing.")
    else:
        st.success("Data Quality is acceptable for analysis.")
