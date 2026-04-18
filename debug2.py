import sys
import os
sys.path.append(os.path.abspath("streamlit-app"))
try:
    from ui.dashboard import render_dashboard
    print("Dashboard imported")
except ImportError as e:
    print("Dashboard ImportError:", e)

try:
    from ui.anomaly import render_anomaly
    print("Anomaly imported")
except ImportError as e:
    print("Anomaly ImportError:", e)
