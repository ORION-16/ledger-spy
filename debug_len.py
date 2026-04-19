import pandas as pd
from ml.fea_anomaly.anomaly import detect_anomalies
df = pd.read_csv('../test.csv')
df.rename(columns={'vendor': 'vendor_name'}, inplace=True)
anom = detect_anomalies(df)
print(f"Len df: {len(df)}")
print(f"Len anom: {len(anom)}")
print(f"txn_id in df: {'txn_id' in df.columns}")
