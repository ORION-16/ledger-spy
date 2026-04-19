import subprocess
import sys
import threading
import time
import os
import webbrowser

def run_landing_page():
    print("🚀 Starting Landing Page on http://localhost:8000")
    # Serves the directory containing index.html
    subprocess.run([sys.executable, "-m", "http.server", "8000"], 
                   stdout=subprocess.DEVNULL, 
                   stderr=subprocess.DEVNULL)

def run_streamlit():
    print("📊 Starting LedgerSpy Dashboard on http://localhost:8506")
    # Use the specific venv python to ensure all installed packages are available
    venv_python = os.path.join(os.path.dirname(__file__), "..", ".venv", "bin", "python")
    python_cmd = venv_python if os.path.exists(venv_python) else sys.executable
    
    # Runs the main Streamlit application
    # Use --server.headless true to prevent Streamlit from opening its own browser tab
    subprocess.run([python_cmd, "-m", "streamlit", "run", "streamlit-app/app.py", "--server.port", "8506", "--server.headless", "true"])

if __name__ == "__main__":
    # Ensure we are running from the ledger-spy directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Start both servers in parallel threads
    t1 = threading.Thread(target=run_landing_page, daemon=True)
    t2 = threading.Thread(target=run_streamlit, daemon=True)

    t1.start()
    time.sleep(1) # Give the landing page a second to boot before starting Streamlit
    t2.start()
    
    # Automatically open the landing page in the user's default browser
    print("🌐 Opening Landing Page in browser...")
    webbrowser.open("http://localhost:8000")

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down LedgerSpy services...")
        sys.exit(0)