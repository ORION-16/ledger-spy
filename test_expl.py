import pandas as pd
from ml.explainable_risk_insights import explain_dataset, generate_rule_explanations
import pickle

data = {
    'txn_id': ['T1', 'T2'],
    'hybrid_risk_score': [0.9, 0.1],
    'amount': [5000, 10],
    'vendor_name': ['A', 'B']
}
df = pd.DataFrame(data)
res = explain_dataset(df)
print(res[['txn_id', 'final_risk_score', 'risk_tier']])
