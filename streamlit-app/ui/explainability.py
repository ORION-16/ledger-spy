from ui.styles import apply_global_styles
import streamlit as st
import pandas as pd

def render_explainability():
    apply_global_styles()
    
    st.markdown("""
    <div class="card">
        <h3>🧠 Explainable Risk Insights</h3>
        <p>Contextual breakdown of identified anomalies</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("🚧 The Explainable Risk UI is currently under construction and will be implemented in a future update.", icon="🚧")
