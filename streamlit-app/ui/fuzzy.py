import streamlit as st
import pandas as pd

def render_fuzzy():
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
        <h3>Fuzzy Vendor Matching</h3>
        <p>Review potentially duplicate vendor names or spoofing attempts.</p>
    </div>
    """, unsafe_allow_html=True)
    
    vendors = st.session_state.get("vendors")
    if not vendors:
        st.info("No fuzzy matching data available.")
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
