import sys
import os
sys.path.append(os.path.abspath(os.path.join("streamlit-app", "..")))

try:
    from ui.dashboard import render_dashboard
    print("Dashboard imported successfully")
except Exception as e:
    print(f"Error importing dashboard: {e}")

try:
    from ui.anomaly import render_anomaly
    print("Anomaly imported successfully")
except Exception as e:
    print(f"Error importing anomaly: {e}")
