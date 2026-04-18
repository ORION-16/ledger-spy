import streamlit as st

def render_risk_map():
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
        <h3>Relational Risk Map</h3>
        <p>Network-based insight on shared entities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    risk_graph = st.session_state.get("risk_graph")
    if risk_graph and isinstance(risk_graph, dict) and "nodes" in risk_graph:
        n_nodes = len(risk_graph.get("nodes", []))
        n_edges = len(risk_graph.get("edges", []))
        
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Nodes", n_nodes)
            with col2:
                st.metric("Total Edges", n_edges)
        
        st.markdown("""
        <div class="card" style="text-align:center; padding: 40px;">
            <h3>Graph Visualization Data Loaded</h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center; padding: 40px; border: 1px dashed #2a2f36;">
            <h3 style="color:#8b949e; border:none;">Coming Soon</h3>
            <p>Network map features are currently in development.</p>
        </div>
        """, unsafe_allow_html=True)
