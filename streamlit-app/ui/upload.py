import streamlit as st

def render_upload():
    st.header("Upload & Preview")
    st.caption("Inspect the raw data and understand the schema.")
    st.divider()
    
    df = st.session_state["df"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Rows", f"{df.shape[0]:,}")
    with col2:
        st.metric("Total Columns", f"{df.shape[1]:,}")
        
    st.subheader("Data Preview (Top 20 rows)")
    st.dataframe(df.head(20), use_container_width=True)
    
    st.subheader("Columns Available")
    st.write(", ".join(df.columns.tolist()))
