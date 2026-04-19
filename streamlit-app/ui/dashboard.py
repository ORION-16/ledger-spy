import streamlit as st

def render_dashboard():
    
    st.markdown("""
    <div class="card">
        <h3>
            <svg xmlns="http://www.w3.org/-2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-activity"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            LedgerSpy Executive Dashboard
        </h3>
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
        <h3>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-file-text"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            Audit Memo
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    audit_memo = st.session_state.get("audit_memo")
    
    if not audit_memo:
        st.warning("No audit memo available. Upload data first.")
    else:
        st.text_area("Generated Audit Memo", audit_memo, height=400)
    
        st.download_button(
            label="📥 Download Memo",
            data=audit_memo,
            file_name="audit_memo.txt",
            mime="text/plain"
        )
