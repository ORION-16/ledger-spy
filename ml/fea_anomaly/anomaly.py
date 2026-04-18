# ============================================================
# LedgerSpy ULTIMATE HYBRID MODEL
# ------------------------------------------------------------
# Combines:
#   1. LightGBM Fraud Classifier
#   2. Isolation Forest Anomaly Detector
#   3. Final Hybrid Risk Score
#   4. Full Dataset Chunk Scoring
#   5. Charts + Vendor Risk Summary
#
# BEST FOR:
#   Known fraud + Unknown suspicious behavior
#
# RUN:
# python hybrid_model.py --input LedgerSpy_Final_Realistic.csv
# ============================================================

import pandas as pd
import numpy as np
import argparse
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import IsolationForest

# ------------------------------------------------------------
# LightGBM
# ------------------------------------------------------------
USE_LGBM = True
try:
    from lightgbm import LGBMClassifier
except:
    USE_LGBM = False
    from sklearn.ensemble import RandomForestClassifier

# ============================================================
# CONFIG
# ============================================================

COL = {
    "txn_id": "txn_id",
    "timestamp": "timestamp",
    "amount": "amount",
    "vendor_name": "vendor_name",
    "vendor_city": "vendor_city",
    "vendor_location_risk": "vendor_location_risk",
    "velocity_score": "velocity_score",
    "department": "department",
    "approver": "approver",
    "payment_mode": "payment_mode",
    "fraud": "is_fraud"
}

# ============================================================
# LOAD SAMPLE
# ============================================================

def load_sample(filepath, sample_size=300000):

    print(f"[INFO] Sampling {sample_size:,} rows...")

    chunks = []

    for chunk in pd.read_csv(filepath, chunksize=100000):
        chunks.append(chunk.sample(min(10000, len(chunk)), random_state=42))

    df = pd.concat(chunks, ignore_index=True)

    if len(df) > sample_size:
        df = df.sample(sample_size, random_state=42)

    print(f"[INFO] Training rows: {len(df):,}")

    return df

# ============================================================
# PREPROCESS
# ============================================================

encoders = {}

def preprocess(df, fit=True):

    ts = pd.to_datetime(df[COL["timestamp"]], errors="coerce")

    df["hour"] = ts.dt.hour.fillna(-1).astype("int8")
    df["day_of_week"] = ts.dt.dayofweek.fillna(-1).astype("int8")
    df["month"] = ts.dt.month.fillna(-1).astype("int8")

    cat_cols = [
        COL["vendor_name"],
        COL["vendor_city"],
        COL["department"],
        COL["approver"],
        COL["payment_mode"]
    ]

    for col in cat_cols:

        if fit:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        else:
            le = encoders[col]
            vals = df[col].astype(str)

            unseen = ~vals.isin(le.classes_)
            vals[unseen] = le.classes_[0]

            df[col] = le.transform(vals)

    y = None

    if COL["fraud"] in df.columns:
        y = df[COL["fraud"]].astype(str).str.lower().map({
            "true":1, "false":0, "1":1, "0":0
        }).fillna(0).astype(int)

    features = [
        COL["amount"],
        COL["vendor_location_risk"],
        COL["velocity_score"],
        COL["vendor_name"],
        COL["vendor_city"],
        COL["department"],
        COL["approver"],
        COL["payment_mode"],
        "hour",
        "day_of_week",
        "month"
    ]

    X = df[features].fillna(0).astype("float32")

    return X, y, features

# ============================================================
# LIGHTGBM MODEL
# ============================================================

def train_classifier(X_train, y_train):

    if USE_LGBM:

        model = LGBMClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=8,
            num_leaves=64,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        )

    else:

        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        )

    model.fit(X_train, y_train)

    return model

# ============================================================
# ISOLATION FOREST
# ============================================================

def train_anomaly_model(X):

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=100,
        max_samples=100000,
        contamination=0.03,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_scaled)

    return model, scaler

# ============================================================
# EVALUATION
# ============================================================

def evaluate(model, X_test, y_test):

    probs = model.predict_proba(X_test)[:,1]
    preds = (probs > 0.5).astype(int)

    print("\n========== CLASSIFIER METRICS ==========")
    print("ROC AUC :", round(roc_auc_score(y_test, probs),4))
    print("Precision:", round(precision_score(y_test,preds),4))
    print("Recall   :", round(recall_score(y_test,preds),4))
    print("F1 Score :", round(f1_score(y_test,preds),4))
    print("=======================================\n")

# ============================================================
# SCORE FULL FILE
# ============================================================

def score_full_data(clf_model, anom_model, scaler, filepath):

    outputs = []

    for chunk in pd.read_csv(filepath, chunksize=100000):

        X, _, _ = preprocess(chunk, fit=False)

        # Fraud probability
        fraud_prob = clf_model.predict_proba(X)[:,1]

        # Anomaly score
        X_scaled = scaler.transform(X)

        raw = anom_model.decision_function(X_scaled)
        anomaly_score = -raw

        # Normalize anomaly score 0-1
        anomaly_norm = (
            anomaly_score - anomaly_score.min()
        ) / (
            anomaly_score.max() - anomaly_score.min() + 1e-9
        )

        # Final Hybrid Score
        hybrid_score = (
            0.7 * fraud_prob +
            0.3 * anomaly_norm
        )

        chunk["fraud_probability"] = fraud_prob
        chunk["anomaly_score"] = anomaly_norm
        chunk["hybrid_risk_score"] = hybrid_score
        chunk["predicted_fraud"] = (fraud_prob > 0.5).astype(int)

        outputs.append(chunk)

    final = pd.concat(outputs, ignore_index=True)

    final.to_csv("hybrid_predictions.csv", index=False)

    print("[SAVED] hybrid_predictions.csv")

    return final

# ============================================================
# CHARTS
# ============================================================

def make_charts(df):

    # Distribution
    plt.figure(figsize=(10,5))
    plt.hist(df["hybrid_risk_score"], bins=60)
    plt.title("Hybrid Risk Score Distribution")
    plt.savefig("risk_distribution.png", dpi=150)
    plt.close()

    # Top risky txns
    top = df.nlargest(20, "hybrid_risk_score")

    plt.figure(figsize=(12,6))
    plt.barh(
        top[COL["txn_id"]].astype(str),
        top["hybrid_risk_score"]
    )
    plt.title("Top Risky Transactions")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig("top_risky_transactions.png", dpi=150)
    plt.close()

    print("[SAVED] Charts")

# ============================================================
# VENDOR SUMMARY
# ============================================================

def vendor_summary(df):

    grp = df.groupby(COL["vendor_name"]).agg(
        total_txns=(COL["txn_id"],"count"),
        total_amount=(COL["amount"],"sum"),
        avg_risk=("hybrid_risk_score","mean"),
        fraud_flags=("predicted_fraud","sum")
    ).reset_index()

    grp = grp.sort_values("avg_risk", ascending=False)

    grp.to_csv("vendor_risk_summary.csv", index=False)

    print("[SAVED] vendor_risk_summary.csv")

# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--sample", type=int, default=300000)

    args = parser.parse_args()

    # Load training sample
    df = load_sample(args.input, args.sample)

    # Preprocess
    X, y, features = preprocess(df, fit=True)

    # Train test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    # Train classifier
    clf_model = train_classifier(X_train, y_train)

    # Evaluate
    evaluate(clf_model, X_test, y_test)

    # Train anomaly model
    anom_model, scaler = train_anomaly_model(X)

    # Score full dataset
    final = score_full_data(
        clf_model,
        anom_model,
        scaler,
        args.input
    )

    # Charts
    make_charts(final)

    # Vendor summary
    vendor_summary(final)

    print("[DONE] Ultimate Hybrid Risk Engine Complete.")

# ============================================================

def detect_anomalies(df):
    try:
        import numpy as np
        data = df.copy()
        
        for col in COL.values():
            if col not in data.columns:
                data[col] = "unknown"
                
        X, y, features = preprocess(data, fit=True)
        clf_model = train_classifier(X, y if y is not None else np.zeros(len(X)))
        anom_model, scaler = train_anomaly_model(X)
        
        fraud_prob = clf_model.predict_proba(X)[:,1]
        
        X_scaled = scaler.transform(X)
        raw = anom_model.decision_function(X_scaled)
        anomaly_score = -raw
        
        anomaly_norm = (
            anomaly_score - anomaly_score.min()
        ) / (
            anomaly_score.max() - anomaly_score.min() + 1e-9
        )
        
        hybrid_score = 0.7 * fraud_prob + 0.3 * anomaly_norm
        
        data["fraud_probability"] = fraud_prob
        data["anomaly_score"] = anomaly_norm
        data["hybrid_risk_score"] = hybrid_score
        data["is_anomaly"] = hybrid_score > 0.7
        
        return data
    except Exception as e:
        print(f"Error in detect_anomalies: {e}")
        df["is_anomaly"] = False
        return df

if __name__ == "__main__":
    main()
