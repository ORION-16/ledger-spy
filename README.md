# LedgerSpy

LedgerSpy is an AI-powered fraud detection tool built for a 4-person hackathon team.

## Setup Instructions

1. Clone the repository and navigate into the `ledger-spy` directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or .venv\Scripts\activate on Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run the App

1. Navigate to the frontend directory:
   ```bash
   cd streamlit-app
   ```
2. Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```

---

## Team Workflow & Guidelines

This project uses a simple, beginner-friendly GitHub flow without a `dev` branch. All work goes from feature branches directly into `main` via Pull Requests.

### Exact Commands for Teammates to Start
When starting work for the first time:

1. **Clone Repo:**
   ```bash
   git clone <your-github-repo-url>
   cd ledger-spy
   ```
2. **Create Branch (pick one of the assigned features):**
   ```bash
   git checkout -b feature/streamlit-core
   # OR: git checkout -b feature/ui-charts
   # OR: git checkout -b feature/ml-anomaly
   # OR: git checkout -b feature/ml-fuzzy
   ```
3. **Push Initial Branch:**
   ```bash
   git push -u origin <your-branch-name>
   ```

### Daily Workflow
Each time you sit down to code, follow these steps:

1. **Pull Latest Main:** Make sure you have everyone else's latest work.
   ```bash
   git checkout main
   git pull origin main
   ```
2. **Switch to Your Branch:**
   ```bash
   git checkout <your-branch-name>
   ```
3. **Merge Main to Your Branch (to keep it updated):**
   ```bash
   git merge main
   ```
4. **Code, Commit, and Push:**
   ```bash
   git add .
   git commit -m "Describe your changes clearly here"
   git push origin <your-branch-name>
   ```
5. **Create a Pull Request (PR):**
   - Go to GitHub and open a Pull Request from your branch into `main`.
   - Ask a teammate to review and merge it.

### 🚨 Strict Rules

1. **Never push directly to `main`.** All code must go through Pull Requests.
2. **Always use Pull Requests** to merge code into `main`.
3. **Stay in your lane.** Do not edit files or folders assigned to other team members.
4. **Streamlit core (`app.py`)** should only be edited by the assigned people (`feature/streamlit-core` and `feature/ui-charts`) to avoid massive merge conflicts.
