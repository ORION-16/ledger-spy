import streamlit as st
import pandas as pd

def render_benford():
    
    st.markdown("""
    <div class="card">
        <h3>Benford's Law Analysis</h3>
        <p>Digital frequency profiling to detect fabricated numbers.</p>
    </div>
    """, unsafe_allow_html=True)
    
    benford_data = st.session_state.get("benford")
    if benford_data is None:
        st.markdown("""
        <div class="card" style="text-align:center; padding: 40px; border: 1px dashed #2a2f36;">
            <h3 style="color:#8b949e; border:none;">Data Missing</h3>
            <p>Benford analysis requires numerical data to process.</p>
        </div>
        """, unsafe_allow_html=True)
        return
        
    if isinstance(benford_data, dict):
        df_benford = pd.DataFrame(list(benford_data.items()), columns=["Digit", "Expected (%)"])
        df_benford.set_index("Digit", inplace=True)
        st.markdown("""
        <div class="card">
            <h3>Distribution Chart</h3>
        </div>
        """, unsafe_allow_html=True)
        st.bar_chart(df_benford)
    elif isinstance(benford_data, pd.DataFrame):
        if "Digit" in benford_data.columns:
            df_benford = benford_data.set_index("Digit")
            st.markdown("""
            <div class="card">
                <h3>Expected vs Actual Distribution</h3>
            </div>
            """, unsafe_allow_html=True)
            st.bar_chart(df_benford)
        else:
            st.dataframe(benford_data, use_container_width=True)
    else:
        st.write(benford_data)
