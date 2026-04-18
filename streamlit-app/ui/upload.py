import streamlit as st

def render_upload():
    st.markdown("""<style>
    .card { background-color: #161b22; border: 1px solid #2a2f36; border-radius: 12px; padding: 20px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card h3 { color: #00c2ff; font-weight: 600; font-size: 1.2rem; margin-top: 0; margin-bottom: 0.5rem; border-bottom: 1px solid #2a2f36; padding-bottom: 0.5rem; }
    .card p { color: #8b949e; font-size: 0.9rem; margin: 0; }
    </style>""", unsafe_allow_html=True)
    
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
