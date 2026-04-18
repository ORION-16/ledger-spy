import streamlit as st
import pandas as pd
import plotly.express as px

def render_dashboard():
    st.header("Risk Dashboard")
    st.caption("Executive summary of all data risks and final decision memo.")
    st.divider()
    
    df = st.session_state.get("df")
    df_anomaly = st.session_state.get("df_anomaly")
    matches_df = st.session_state.get("vendor_matches")
    risk_summary = st.session_state.get("risk_summary")
    
    total_tx = len(df) if df is not None else 0
    anomalies_count = len(df_anomaly[df_anomaly["is_anomaly"]]) if df_anomaly is not None and "is_anomaly" in df_anomaly.columns else 0
    
    overall_risk = "N/A"
    if risk_summary:
        overall_risk = risk_summary.get("overall_risk", "N/A")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Transactions", f"{total_tx:,}")
    with col2:
        st.metric("Anomalies Found", f"{anomalies_count:,}")
    with col3:
        st.metric("Overall Risk Score", overall_risk)
        
    st.divider()
    st.subheader("Transaction Risk Distribution")
    
    # Base it on our mock data
    high = anomalies_count
    medium = len(matches_df) if matches_df is not None else 0
    low = max(total_tx - (high + medium), 0)
    
    pie_data = pd.DataFrame({
        "Risk Bucket": ["High", "Medium", "Low"],
        "Count": [high, medium, low]
    })
    
    fig = px.pie(
        pie_data, 
        values="Count", 
        names="Risk Bucket", 
        color="Risk Bucket",
        color_discrete_map={"High": "red", "Medium": "orange", "Low": "green"},
        title="Distribution of Identified Risks"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("Audit Memo Generation")
    
    if st.button("Generate Audit Memo", type="primary", use_container_width=True):
        st.session_state["generate_memo"] = True
        st.rerun()
        
    if risk_summary and risk_summary.get("memo"):
        st.text_area("Final Output Memo", value=risk_summary["memo"], height=150)
