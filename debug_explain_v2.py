import pandas as pd
from ml.explainable_risk_insights import explain_dataset
from ml.fea_anomaly.anomaly import detect_anomalies

# simulate load_data
df = pd.read_csv('../test.csv')
df.rename(columns={'vendor': 'vendor_name'}, inplace=True)
df['txn_id'] = ['T1', 'T2', 'T3']
df['approver'] = ['A1', 'A2', 'A3']
df['department'] = ['D1', 'D2', 'D3']
df['payment_mode'] = ['P1', 'P2', 'P3']
df['narration'] = ['N1', 'N2', 'N3']
df['timestamp'] = ['2023-01-01', '2023-01-02', '2023-01-03']

from ml.fea_fuzzy.fuzzy import find_similar_vendors
from ml.stubs import build_risk_graph

anom = detect_anomalies(df)
vend = find_similar_vendors(df)
graph = build_risk_graph(df)

calc_df = df.copy()
for col in ['fraud_probability', 'anomaly_score', 'hybrid_risk_score']:
    if col in anom.columns:
        calc_df[col] = anom[col]

calc_df['fuzzy_duplicate_flag'] = 1
calc_df['fuzzy_similarity'] = 98.0
calc_df['vendor_graph_risk'] = 1.0

res = explain_dataset(calc_df)
print(res[['txn_id', 'final_risk_score', 'risk_tier']])
