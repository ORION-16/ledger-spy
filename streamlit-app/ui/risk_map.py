import streamlit as st

def render_risk_map():
    st.markdown("""<style>
    .card { background-color: #161b22; border: 1px solid #2a2f36; border-radius: 12px; padding: 20px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-header { color: #00c2ff; font-weight: 600; font-size: 1.2rem; margin-bottom: 0.5rem; border-bottom: 1px solid #2a2f36; padding-bottom: 0.5rem; }
    .metric-label { font-size: 0.85rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #00c2ff; line-height: 1.2; margin-top: 5px; }
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-header">Relational Risk Map</div><p style="color:#8b949e; font-size:0.9rem; margin:0;">Network-based insight on shared entities.</p></div>', unsafe_allow_html=True)
    
    risk_graph = st.session_state.get("risk_graph")
    if risk_graph and isinstance(risk_graph, dict) and "nodes" in risk_graph:
        n_nodes = len(risk_graph.get("nodes", []))
        n_edges = len(risk_graph.get("edges", []))
        
        html_metrics = f"""
        <div style="display: flex; gap: 20px; margin-bottom: 20px;">
            <div class="card" style="flex: 1; margin: 0; text-align: center;">
                <div class="metric-label">Total Nodes</div>
                <div class="metric-value">{n_nodes}</div>
            </div>
            <div class="card" style="flex: 1; margin: 0; text-align: center;">
                <div class="metric-label">Total Edges</div>
                <div class="metric-value">{n_edges}</div>
            </div>
        </div>
        """
        st.markdown(html_metrics, unsafe_allow_html=True)
        st.markdown('<div class="card" style="text-align:center; padding: 40px;"><div class="metric-label">Graph Visualization Data Loaded</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card" style="text-align:center; padding: 40px; border: 1px dashed #2a2f36;"><h3 style="color:#8b949e; border:none;">Coming Soon</h3><p style="color:#8b949e;">Network map features are currently in development.</p></div>', unsafe_allow_html=True)
