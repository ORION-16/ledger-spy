import streamlit as st

def render_upload():
    
    st.markdown("""
    <div class="card">
        <h3>Upload & Preview</h3>
        <p>Dataset schema and snapshot preview</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = st.session_state.get("df")
    if df is None:
        return
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Rows", f"{df.shape[0]:,}")
        with col2:
            st.metric("Total Columns", f"{df.shape[1]:,}")
            
    st.markdown("""
    <div class="card">
        <h3>Data Snapshot</h3>
    </div>
    """, unsafe_allow_html=True)
    st.dataframe(df.head(100), use_container_width=True)
