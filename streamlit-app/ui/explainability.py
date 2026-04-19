import streamlit as st
import pandas as pd
from ml.explainable_risk_insights import explain_dataset

def render_explainability():
    
    st.markdown("""
    <div class="card">
        <h3>Explainable Risk Insights</h3>
        <p>Contextual breakdown of identified anomalies</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = st.session_state.get("df")
    
    if df is None:
        st.warning("No data available. Please upload a dataset.")
        return
        
    calc_df = df.copy()
    
    # 1. Merge ML anomaly scores to drive the risk values above 0
    anomalies_df = st.session_state.get("anomalies")
    if anomalies_df is not None and not anomalies_df.empty:
        for col in ["fraud_probability", "anomaly_score", "hybrid_risk_score", "velocity_score", "vendor_location_risk"]:
            if col in anomalies_df.columns:
                if len(calc_df) == len(anomalies_df):
                    calc_df[col] = anomalies_df[col].values
                elif "txn_id" in calc_df.columns and "txn_id" in anomalies_df.columns:
                    calc_df = calc_df.merge(anomalies_df[["txn_id", col]], on="txn_id", how="left")

    # 2. Merge Fuzzy vendor metrics
    vendors_res = st.session_state.get("vendors")
    if vendors_res is not None:
        if not hasattr(vendors_res, "columns"):
            vendors_res = pd.DataFrame(vendors_res)
        
        if "risk" in vendors_res.columns:
            # Extract flagged vendor names to construct the fuzzy duplicate flags
            flagged = set(vendors_res[vendors_res["risk"].isin(["HIGH", "MEDIUM", "High", "Medium"])].get("vendor_1", vendors_res.get("vendor_a", pd.Series()))).union(
                set(vendors_res[vendors_res["risk"].isin(["HIGH", "MEDIUM", "High", "Medium"])].get("vendor_2", vendors_res.get("vendor_b", pd.Series())))
            )
            
            if "vendor_name" in calc_df.columns:
                calc_df["fuzzy_duplicate_flag"] = calc_df["vendor_name"].isin(flagged).astype(int)
                sim_map = {}
                for _, r in vendors_res.iterrows():
                    v1 = str(r.get("vendor_1", r.get("vendor_a", "")))
                    v2 = str(r.get("vendor_2", r.get("vendor_b", "")))
                    sim = float(r.get("similarity", r.get("similarity_score", 0)))
                    sim_map[v1] = max(sim_map.get(v1, 0), sim)
                    sim_map[v2] = max(sim_map.get(v2, 0), sim)
                calc_df["fuzzy_similarity"] = calc_df["vendor_name"].map(sim_map).fillna(0.0)

    # 3. Merge Graph/Relationship risk
    graph_res = st.session_state.get("risk_graph")
    if graph_res is not None and isinstance(graph_res, dict) and "nodes" in graph_res:
        graph_risk_map = {}
        for node in graph_res["nodes"]:
            label = str(node.get("label", ""))
            r_val = str(node.get("risk", "")).upper()
            score = 1.0 if r_val == "HIGH" else (0.5 if r_val == "MEDIUM" else 0.0)
            graph_risk_map[label] = max(graph_risk_map.get(label, 0), score)
        if "vendor_name" in calc_df.columns:
            calc_df["vendor_graph_risk"] = calc_df["vendor_name"].map(graph_risk_map).fillna(0.0)

    try:
        result = explain_dataset(calc_df)
    except Exception as e:
        st.error(f"Explainability failed: {str(e)}")
        return

    if hasattr(result, "columns"):
        display_df = result.copy()
    else:
        display_df = pd.DataFrame(result)
        
    if "risk_tier" in display_df.columns:
        # Reorder columns to put important ones first
        front_cols = ["risk_tier", "final_risk_score", "txn_id", "vendor_name", "amount", "top_reason_1"]
        existing_front = [c for c in front_cols if c in display_df.columns]
        other_cols = [c for c in display_df.columns if c not in existing_front]
        display_df = display_df[existing_front + other_cols]

        high = (display_df["risk_tier"] == "HIGH").sum()
        medium = (display_df["risk_tier"] == "MEDIUM").sum()
        low = (display_df["risk_tier"] == "LOW").sum()
        st.write(f"High: {high}, Medium: {medium}, Low: {low}")

        st.write("Top Risky Entries:")
        # Sort so highest risk scores appear at the top, and take the top 100 rows
        top_risky_df = display_df.sort_values(by="final_risk_score", ascending=False).head(100)
        st.dataframe(top_risky_df, use_container_width=True)
    elif "risk" in display_df.columns:
        high = (display_df["risk"] == "HIGH").sum()
        medium = (display_df["risk"] == "MEDIUM").sum()
        low = (display_df["risk"] == "LOW").sum()
        st.write(f"High: {high}, Medium: {medium}, Low: {low}")

        st.write("Top Risky Entries:")
        # Define a sorting hierarchy if only a categorical string exists
        risk_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        display_df["_sort_helper"] = display_df["risk"].map(risk_map).fillna(0)
        top_risky_df = display_df.sort_values(by="_sort_helper", ascending=False).drop(columns=["_sort_helper"]).head(100)
        st.dataframe(top_risky_df, use_container_width=True)

    st.write("All entries (Sampled):")
    st.dataframe(display_df.head(500), use_container_width=True)
    
    # Empty space to force Streamlit to reload the module and purge the cache
    st.write("")
