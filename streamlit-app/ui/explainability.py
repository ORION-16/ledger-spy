from ui.styles import apply_global_styles
import streamlit as st
import pandas as pd

def render_explainability():
    apply_global_styles()
    
    st.markdown("""
    <div class="card">
        <h3>Explainable Risk Insights</h3>
        <p>Contextual breakdown of identified anomalies</p>
    </div>
    """, unsafe_allow_html=True)
    
    explanations = st.session_state.get("explanations")
    if explanations is None:
        st.info("No explainability data found.")
        return
        
    if isinstance(explanations, list):
        df = pd.DataFrame(explanations)
    else:
        df = explanations
        
    st.markdown("""
    <div class="card">
        <h3>Risk Explanations Table</h3>
    </div>
    """, unsafe_allow_html=True)
    
    def highlight_explanations(s):
        return ['color: #00c2ff; font-family: monospace;'] * len(s) if s.name == 'explanation' else [''] * len(s)
        
    st.dataframe(df.style.apply(highlight_explanations), use_container_width=True)
