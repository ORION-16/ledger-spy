import streamlit as st
import pandas as pd

def render_fuzzy():
    
    st.markdown("""
    <div class="card">
        <h3>Fuzzy Vendor Matching</h3>
        <p>Review potentially duplicate vendor names or spoofing attempts.</p>
    </div>
    """, unsafe_allow_html=True)
    
    vendors = st.session_state.get("vendors")
    if not vendors:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('''
            <div class="notice-box">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px; filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.4));"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
<div class="notice-box-title">No Dataset Loaded</div>
                <div class="notice-box-subtitle">Navigate to the Upload & Preview section to run fuzzy matching.</div>
            </div>
            ''', unsafe_allow_html=True)
        return
        
    if isinstance(vendors, list):
        df_vendors = pd.DataFrame(vendors)
    else:
        df_vendors = vendors
        
    def highlight_risk(row):
        risk = str(row.get("risk", "")).lower()
        if risk == "high":
            return ['color: #ff7b72; font-weight: bold; background-color: rgba(255, 123, 114, 0.1)'] * len(row)
        elif risk == "medium":
            return ['color: #d29922; background-color: rgba(210, 153, 34, 0.1)'] * len(row)
        return [''] * len(row)
        
    st.markdown("""
    <div class="card">
        <h3>Matched Entities</h3>
    </div>
    """, unsafe_allow_html=True)
    if not df_vendors.empty:
        st.dataframe(df_vendors.style.apply(highlight_risk, axis=1), use_container_width=True)
    else:
        st.warning("Empty vendor list.")
