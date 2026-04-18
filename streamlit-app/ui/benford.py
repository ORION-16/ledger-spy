import streamlit as st
import pandas as pd

def render_benford():
    st.markdown('''<style>
    /* Force Global Dark Mode to override Streamlit light theme */
    .stApp { background-color: #0e1117; color: #e6edf3; }
    
    /* Target Streamlit Metrics to look like React Cards */
    [data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #2a2f36;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Target Metric Labels */
    [data-testid="stMetricLabel"] > div > div > p {
        color: #8b949e !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Target Metric Values */
    [data-testid="stMetricValue"] > div {
        color: #00c2ff !important;
        font-weight: 700;
        font-size: 2.2rem;
    }

    /* Target Dataframes */
    [data-testid="stDataFrame"] {
        background-color: #161b22;
        border: 1px solid #2a2f36;
        border-radius: 12px;
        padding: 10px;
    }

    /* Shared Card Titles (Injected HTML) */
    .card { background-color: #161b22; border: 1px solid #2a2f36; border-radius: 12px; padding: 20px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card h3 { color: #00c2ff; font-weight: 600; font-size: 1.2rem; margin-top: 0; margin-bottom: 0.5rem; border-bottom: 1px solid #2a2f36; padding-bottom: 0.5rem; }
    .card p { color: #8b949e; font-size: 0.9rem; margin: 0; }
    
    /* Audit Memo Block */
    .mono-block { font-family: 'Courier New', monospace; background-color: #0d1117; border: 1px solid #30363d; padding: 20px; border-radius: 8px; color: #79c0ff; white-space: pre-wrap; font-size: 0.95rem; line-height: 1.5; }
    </style>''', unsafe_allow_html=True)
    
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
