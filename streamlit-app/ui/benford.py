import streamlit as st
import pandas as pd

def render_benford():
    st.markdown("""<style>
    .card { background-color: #161b22; border: 1px solid #2a2f36; border-radius: 12px; padding: 20px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-header { color: #00c2ff; font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem; border-bottom: 1px solid #2a2f36; padding-bottom: 0.5rem; }
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-header">Benford\'s Law Analysis</div><p style="color:#8b949e; font-size:0.9rem; margin:0;">Digital frequency profiling to detect fabricated numbers.</p></div>', unsafe_allow_html=True)
    
    benford_data = st.session_state.get("benford")
    if benford_data is None:
        st.markdown('<div class="card" style="text-align:center; padding: 40px; border: 1px dashed #2a2f36;"><h3 style="color:#8b949e; border:none;">Data Missing</h3><p style="color:#8b949e;">Benford analysis requires numerical data to process.</p></div>', unsafe_allow_html=True)
        return
        
    if isinstance(benford_data, dict):
        df_benford = pd.DataFrame(list(benford_data.items()), columns=["Digit", "Expected (%)"])
        df_benford.set_index("Digit", inplace=True)
        st.markdown('<div class="card"><div class="card-header">Distribution Chart</div></div>', unsafe_allow_html=True)
        st.bar_chart(df_benford)
    elif isinstance(benford_data, pd.DataFrame):
        if "Digit" in benford_data.columns:
            df_benford = benford_data.set_index("Digit")
            st.markdown('<div class="card"><div class="card-header">Expected vs Actual Distribution</div></div>', unsafe_allow_html=True)
            st.bar_chart(df_benford)
        else:
            st.dataframe(benford_data, use_container_width=True)
    else:
        st.write(benford_data)
