import re

file_path = '/Users/orionrodrigues16/Documents/antigravity/ps5/ledger-spy/ml/explainable_risk_insights.py'
with open(file_path, 'r') as f:
    content = f.read()

new_weights = """WEIGHTS = {
    "model_risk":        0.55,
    "amount_risk":       0.15,
    "relationship_risk": 0.10,
    "duplicate_vendor":  0.10,
    "timing_risk":       0.05,
    "velocity_risk":     0.05,
}

# Risk thresholds
RISK_HIGH   = 60
RISK_MEDIUM = 30"""

# Use regex to find and replace WEIGHTS block
import re
content = re.sub(r'WEIGHTS = \{.*?\}.*?RISK_MEDIUM = \d+', new_weights, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

