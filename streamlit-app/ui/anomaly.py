import streamlit as st
import pandas as pd

def render_anomaly():
    
    st.markdown("""
    <div class="card" style="padding: 16px 24px; margin-bottom: 24px;">
        <h2 style="margin: 0; display: flex; align-items: center; gap: 10px;">
            Anomaly Detection
        </h2>
        <p style="margin-top: 4px; color: #9ca3af;">Identify statistical deviations and unusual transaction patterns across the ledger.</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = st.session_state.get("anomalies")
    if df is None or not isinstance(df, pd.DataFrame) or "is_anomaly" not in df.columns:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('''
            <div class="notice-box">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px; filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.4));"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
<div class="notice-box-title">No Dataset Loaded</div>
                <div class="notice-box-subtitle">Navigate to the Upload & Preview section to process anomalies.</div>
            </div>
            ''', unsafe_allow_html=True)
        return
        
    total = len(df)
    anomalies = int(df["is_anomaly"].sum()) if "is_anomaly" in df.columns else 0
    percent = (anomalies / total * 100) if total else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", f"{total:,}")
    col2.metric("Anomalies Detected", f"{anomalies:,}")
    col3.metric("Anomaly Rate", f"{percent:.2f}%")
    
    st.info(f"{anomalies:,} suspicious transactions detected out of {total:,} total records.")
    
    # Hide encoded/unnecessary columns to keep the UI clean
    cols_to_hide = ["approver", "department", "vendor_city", "merchant_category_code"]
    clean_df = df.drop(columns=cols_to_hide, errors="ignore")

    if "hybrid_risk_score" in clean_df.columns:
        st.markdown("""
            <h3 style='margin-top: 2rem; margin-bottom: 1rem; color: #ffffff; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem;'>
                Risk Score Distribution
            </h3>
        """, unsafe_allow_html=True)
        # Plot distribution
        st.bar_chart(clean_df["hybrid_risk_score"].dropna().head(1000), color="#8b5cf6", use_container_width=True)

        st.markdown("""
            <h3 style='margin-top: 2rem; margin-bottom: 1rem; color: #ffffff; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem;'>
                Top Risky Transactions
            </h3>
        """, unsafe_allow_html=True)
        
        top_risky = clean_df.sort_values("hybrid_risk_score", ascending=False).head(20)
        st.dataframe(
            top_risky, 
            use_container_width=True,
            hide_index=True,
            column_config={
                "hybrid_risk_score": st.column_config.ProgressColumn(
                    "Risk Score",
                    help="Anomaly risk probability",
                    format="%.3f",
                    min_value=0,
                    max_value=1,
                ),
                "is_anomaly": st.column_config.CheckboxColumn("Anomaly Flag"),
                "amount": st.column_config.NumberColumn("Amount", format="$ %.2f")
            }
        )
            
    st.markdown("""
        <h3 style='margin-top: 3rem; margin-bottom: 1rem; color: #ffffff; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem;'>
            <svg style="width:20px; height:20px; vertical-align:middle; margin-right:8px;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            Transaction Explorer
        </h3>
    """, unsafe_allow_html=True)
    
    col_filter, col_caption = st.columns([1, 2])
    with col_filter:
        show_only_anomalies = st.checkbox("Show only anomalies (High Risk)", value=True)
    
    display_df = clean_df[clean_df["is_anomaly"] == True] if show_only_anomalies else clean_df

    MAX_ROWS = 500
    display_df_head = display_df.head(MAX_ROWS)
    
    with col_caption:
        if len(display_df) > MAX_ROWS:
            st.markdown(f"<p style='color: #9ca3af; font-size: 0.9rem; text-align: right; margin-top: 5px;'>Showing {len(display_df_head):,} of {len(display_df):,} rows (Limited for Performance)</p>", unsafe_allow_html=True)
        elif show_only_anomalies:
            st.markdown(f"<p style='color: #ff7b72; font-size: 0.9rem; text-align: right; margin-top: 5px; font-weight: 600;'>Displaying all {len(display_df_head):,} Anomaly Hits</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color: #9ca3af; font-size: 0.9rem; text-align: right; margin-top: 5px;'>Showing {len(display_df_head):,} rows</p>", unsafe_allow_html=True)
            
    # Display optimized dataframe natively
    st.dataframe(
        display_df_head, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "hybrid_risk_score": st.column_config.ProgressColumn(
                "Risk Score",
                help="Anomaly risk probability",
                format="%.3f",
                min_value=0,
                max_value=1,
            ),
            "is_anomaly": st.column_config.CheckboxColumn("Anomaly Flag"),
            "amount": st.column_config.NumberColumn("Amount", format="$ %.2f")
        }
    )
