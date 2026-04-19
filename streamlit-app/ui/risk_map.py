import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import sys
import os

try:
    from ml.relationship_risk_mapping import run_risk_pipeline
except ImportError:
    # Add root folder if necessary
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from ml.relationship_risk_mapping import run_risk_pipeline

def render_risk_map():
    
    st.markdown("""
    <div class="card page-header">
        <h2>Relational Risk Map</h2>
        <p>Network-based insight on shared entities, high-risk vendors, and structural anomalies.</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = st.session_state.get("df")
    if df is None:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('''
            <div class="notice-box">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#facc15" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px; filter: drop-shadow(0 0 8px rgba(250, 204, 21, 0.4));"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                <div class="notice-box-title">No Dataset Loaded</div>
                <div class="notice-box-subtitle">Navigate to the Upload & Preview section to begin.</div>
            </div>
            ''', unsafe_allow_html=True)
        return

    # Check if we already have the pipeline results in session state
    if "risk_map_results" not in st.session_state:
        with st.spinner("Building interactive risk graph... (This may take a moment)"):
            try:
                # Prepare fuzzy matches if they exist
                vendors = st.session_state.get("vendors", [])
                fuzzy_df = pd.DataFrame(vendors)
                if not fuzzy_df.empty and "vendor_1" in fuzzy_df.columns and "vendor_2" in fuzzy_df.columns:
                    # Filter out the dummy row if it exists
                    fuzzy_df = fuzzy_df[fuzzy_df["vendor_1"] != "No matches found"]
                else:
                    fuzzy_df = pd.DataFrame(columns=["vendor_1", "vendor_2"])

                # Standardize column names since the script expects specific ones if they are missing
                df_map = df.copy()
                if "vendor_name" not in df_map.columns:
                    if "vendor" in df_map.columns:
                        df_map["vendor_name"] = df_map["vendor"]
                    else:
                        df_map["vendor_name"] = "Unknown Vendor"
                
                if "internal_account" not in df_map.columns:
                    if "account" in df_map.columns:
                        df_map["internal_account"] = df_map["account"]
                    else:
                        df_map["internal_account"] = "Default_Account"
                        
                if "approver" not in df_map.columns:
                    df_map["approver"] = "Unknown"
                if "department" not in df_map.columns:
                    df_map["department"] = "HQ"
                if "is_fraud" not in df_map.columns:
                    df_map["is_fraud"] = 0
                if "txn_id" not in df_map.columns:
                    df_map["txn_id"] = df_map.index
                if "amount" not in df_map.columns:
                    df_map["amount"] = 0

                top_vendors = st.sidebar.slider("Top Vendors Limit", min_value=10, max_value=200, value=80, step=10)

                metrics_df, G, net_html = run_risk_pipeline(df_map, fuzzy_df, top_vendors=top_vendors)
                st.session_state["risk_map_results"] = {
                    "metrics": metrics_df,
                    "graph_html": net_html,
                    "top_vendors_limit": top_vendors
                }
            except Exception as e:
                st.error(f"Error building graph: {e}")
                return
    else:
        # Check if the user changed the slider
        current_limit = st.sidebar.slider("Top Vendors Limit", min_value=10, max_value=200, value=st.session_state["risk_map_results"]["top_vendors_limit"], step=10)
        if current_limit != st.session_state["risk_map_results"]["top_vendors_limit"]:
            st.session_state.pop("risk_map_results")
            st.rerun()

    results = st.session_state["risk_map_results"]
    metrics_df = results["metrics"]
    net_html = results["graph_html"]

    # Graph Output
    st.markdown("### Interactive Network Graph")
    components.html(net_html, height=850)

    st.markdown("---")
    
    # Key Metrics Dashboard
    col1, col2, col3 = st.columns(3)
    vendor_count = len(metrics_df[metrics_df["node_type"] == "vendor"])
    approver_count = len(metrics_df[metrics_df["node_type"] == "approver"])
    top_risk = metrics_df.iloc[0]["node"] if not metrics_df.empty else "N/A"
    
    col1.metric("Mapped Vendors", vendor_count)
    col2.metric("Mapped Approvers", approver_count)
    col3.metric("Highest Risk Node", top_risk)

    st.markdown("---")
    st.markdown("### Risk Distribution Summary")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**Top 10 Risky Vendors**")
        top_v = metrics_df[metrics_df["node_type"] == "vendor"].sort_values("risk_score", ascending=False).head(10)
        if not top_v.empty:
            st.bar_chart(data=top_v.set_index("node")["risk_score"], color="#d62728")
        else:
            st.info("No Vendor data.")
            
    with chart_col2:
        st.markdown("**Top 10 Risky Approvers**")
        top_a = metrics_df[metrics_df["node_type"] == "approver"].sort_values("risk_score", ascending=False).head(10)
        if not top_a.empty:
            st.bar_chart(data=top_a.set_index("node")["risk_score"], color="#1f77b4")
        else:
            st.info("No Approver data.")

    st.markdown("---")
    st.markdown("### Entity Risk Score Details")
    
    tabs = st.tabs(["Vendors", "Approvers", "Accounts", "Departments", "All Nodes"])
    
    def format_risk_table(df_subset):
        if df_subset.empty:
            return df_subset
        return df_subset.drop(columns=["node_type"]).sort_values("risk_score", ascending=False)
    
    with tabs[0]:
        st.markdown("#### Top Risky Vendors")
        st.dataframe(format_risk_table(metrics_df[metrics_df["node_type"] == "vendor"]), use_container_width=True)
    with tabs[1]:
        st.markdown("#### Top Risky Approvers")
        st.dataframe(format_risk_table(metrics_df[metrics_df["node_type"] == "approver"]), use_container_width=True)
    with tabs[2]:
        st.markdown("#### Top Risky Accounts")
        st.dataframe(format_risk_table(metrics_df[metrics_df["node_type"] == "account"]), use_container_width=True)
    with tabs[3]:
        st.markdown("#### Top Risky Departments")
        st.dataframe(format_risk_table(metrics_df[metrics_df["node_type"] == "department"]), use_container_width=True)
    with tabs[4]:
        st.markdown("#### All Mapped Nodes")
        st.dataframe(metrics_df.sort_values("risk_score", ascending=False), use_container_width=True)
