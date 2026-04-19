import sys
import os
sys.path.append(os.path.abspath(os.path.join("streamlit-app", "..")))

try:
    from ui.upload import render_upload
    from ui.dashboard import render_dashboard
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
