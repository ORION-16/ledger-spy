import streamlit as st
import pandas as pd

def render_fuzzy():
    st.header("Fuzzy Vendor Match")
    st.caption("Review potentially duplicate vendor names or spoofing attempts.")
    st.divider()
    
    matches_df = st.session_state.get("vendor_matches")
    explanations = st.session_state.get("risk_explanations")
    
    if matches_df is None or matches_df.empty:
        st.info("No fuzzy vendor matches could be computed. String columns required.")
        return
        
    st.subheader("Closest Vendor Matches")
    st.dataframe(matches_df, use_container_width=True)
    
    st.divider()
    st.subheader("Top Risky Pairs Context")
    if explanations:
        explanations = explanations[:5]
        for idx, row in matches_df.head(5).iterrows():
            exp = explanations[idx] if idx < len(explanations) else "No explanation available."
            with st.expander(f"Risk Pair: {row['vendor_a']} vs {row['vendor_b']} (Score: {row['similarity_score']}%)"):
                st.write(exp)
                st.write(f"**Risk Level:** {row['risk']}")
