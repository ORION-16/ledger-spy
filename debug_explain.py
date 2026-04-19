import pandas as pd
from ml.explainable_risk_insights import explain_dataset
from ml.fea_anomaly.anomaly import detect_anomalies
from ml.fea_fuzzy.fuzzy import find_similar_vendors
from ml.stubs import build_risk_graph

df = pd.read_csv('../test.csv')
anom = detect_anomalies(df)
vend = find_similar_vendors(df)
graph = build_risk_graph(df)

calc_df = df.copy()
for col in ['fraud_probability', 'anomaly_score', 'hybrid_risk_score']:
    if col in anom.columns:
        calc_df[col] = anom[col]

res = explain_dataset(calc_df)
print(res)
