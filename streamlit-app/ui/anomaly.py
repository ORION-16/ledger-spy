import streamlit as st
import plotly.express as px

def render_anomaly():
    st.header("Anomaly Detection")
    st.caption("Identify statistical deviations and unusual transaction patterns.")
    st.divider()
    
    # Analyze Button trigger
    if st.button("Run Anomaly Analysis", type="primary", use_container_width=True):
        st.session_state["run_anomaly"] = True
        st.rerun()

    df_anomaly = st.session_state.get("df_anomaly")
    benford_df = st.session_state.get("benford_df")
    
    if df_anomaly is None or benford_df is None:
        st.info("Click 'Run Anomaly Analysis' to begin detection.")
        return
        
    st.subheader("Suspicious Transactions")
    anomalies = df_anomaly[df_anomaly["is_anomaly"]]
    st.dataframe(anomalies, use_container_width=True)
    
    st.divider()
    st.subheader("Anomaly Distribution")
    if "amount" in df_anomaly.columns:
        fig_scatter = px.scatter(
            df_anomaly, 
            y="amount", 
            x="anomaly_score", 
            color="is_anomaly",
            color_discrete_map={True: "red", False: "lightblue"},
            title="Transaction Amount vs Anomaly Score",
            labels={"amount": "Amount", "anomaly_score": "Risk Score", "is_anomaly": "Is Anomaly"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("No 'amount' column found in data to plot scatter chart.")
        
    st.divider()
    st.subheader("Benford's Law Analysis")
    fig_bar = px.bar(
        benford_df, 
        x="Digit", 
        y=["Expected", "Actual"], 
        barmode="group",
        title="Leading Digit Distribution vs Expected",
        labels={"value": "Frequency (%)", "variable": "Distribution"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)
