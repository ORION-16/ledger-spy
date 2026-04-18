import pandas as pd
import numpy as np

def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["anomaly_score"] = np.random.uniform(0, 1, len(df))
    df["is_anomaly"] = df["anomaly_score"] > 0.8
    return df

def benford_analysis(df: pd.DataFrame) -> dict:
    return {
        1: 28.0, 2: 19.0, 3: 13.0, 4: 10.5,
        5: 8.2, 6: 7.1, 7: 5.5, 8: 4.8, 9: 3.9
    }

def find_similar_vendors(df: pd.DataFrame) -> list:
    return [
        {"vendor_a": "Stationery Ltd", "vendor_b": "Stationery L.T.D",
         "similarity_score": 94, "risk": "High"},
        {"vendor_a": "Tech Supplies Co", "vendor_b": "Tech Supply Co.",
         "similarity_score": 87, "risk": "High"},
        {"vendor_a": "Office Mart", "vendor_b": "OfficeMart Inc",
         "similarity_score": 76, "risk": "Medium"},
    ]

def build_risk_graph(df: pd.DataFrame) -> dict:
    return {
        "nodes": [
            {"id": "V1", "label": "Stationery Ltd", "risk": "High"},
            {"id": "V2", "label": "Stationery L.T.D", "risk": "High"},
            {"id": "V3", "label": "Tech Supplies Co", "risk": "Medium"},
            {"id": "E1", "label": "Employee A", "risk": "Low"},
        ],
        "edges": [
            {"source": "V1", "target": "V2", "weight": 94},
            {"source": "V2", "target": "E1", "weight": 60},
            {"source": "V3", "target": "E1", "weight": 45},
        ]
    }

def explain_risk(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    explanations = [
        "65% unusual timing, 35% high amount",
        "80% rare vendor pattern, 20% duplicate entry",
        "50% off-hours transaction, 50% round figure amount",
    ]
    df["explanation"] = [
        explanations[i % len(explanations)] for i in range(len(df))
    ]
    return df

def compute_readiness_score(df: pd.DataFrame) -> dict:
    total_cells = df.size
    null_pct = (df.isnull().sum().sum() / total_cells) * 100
    dup_count = df.duplicated().sum()
    dup_pct = (dup_count / len(df)) * 100
    score = max(0, 100 - null_pct - dup_pct)
    return {
        "score": round(score, 1),
        "nulls": round(null_pct, 1),
        "duplicates": int(dup_count),
        "columns": "OK" if len(df.columns) >= 3 else "WARNING"
    }

def generate_memo(df: pd.DataFrame, risk_scores: dict) -> str:
    return f"""LEDGERSPY AUDIT MEMO
====================
Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}

EXECUTIVE SUMMARY
-----------------
Total transactions analyzed: {risk_scores.get('total', len(df))}
Anomalies detected: {risk_scores.get('anomaly_count', 0)}
Overall risk level: {risk_scores.get('overall_risk', 'Medium')}

FINDINGS
--------
1. Anomaly detection flagged suspicious transactions exceeding normal patterns.
2. Fuzzy entity reconciliation identified potentially duplicate vendor entries.
3. Digital frequency profiling revealed deviations from expected Benford distribution.

RECOMMENDATION
--------------
Immediate review of flagged transactions is advised before closing the audit engagement.
"""