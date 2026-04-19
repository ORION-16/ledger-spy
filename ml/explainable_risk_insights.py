#!/usr/bin/env python3
"""
LedgerSpy – Explainable Risk Insights (Hybrid SHAP + Rule Engine)
=================================================================
Production-ready module that sits on top of:
  - Anomaly Detection Model outputs
  - Relationship Risk Mapping outputs
  - Fuzzy Duplicate Vendor Detection outputs

Usage:
  python explainable_risk_insights.py \
      --ledger LedgerSpy_Final_Realistic.csv \
      --anomaly hybrid_predictions.csv \
      --relationship node_risk_scores.csv \
      --fuzzy fuzzy_matches.csv \
      --model trained_hybrid.pkl \
      --top-n 100
"""

import argparse
import os
import sys
import warnings
import logging
import pickle
import json
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("LedgerSpy-Explainer")

def find_default_model():
    """
    Auto-detect model if --model not supplied.
    Looks inside ./models/
    """
    model_dir = Path("models")
    if not model_dir.exists():
        return None

    preferred = [
        "trained_hybrid.pkl",
        "hybrid_model.pkl",
        "model.pkl"
    ]

    for p in preferred:
        fp = model_dir / p
        if fp.exists():
            return str(fp)

    pkls = list(model_dir.glob("*.pkl"))
    if pkls:
        return str(pkls[0])

    return None


# ---------------------------------------------------------------------------
# Constants – output paths
# ---------------------------------------------------------------------------
from datetime import datetime

RUN_TS = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_DIR = Path("outputs") / f"run_{RUN_TS}"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHART_DIR = OUT_DIR / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Weights for final risk score composition (must sum to 1.0)
# ---------------------------------------------------------------------------
WEIGHTS = {
    "model_risk":        0.40,
    "relationship_risk": 0.25,
    "duplicate_vendor":  0.15,
    "amount_risk":       0.10,
    "timing_risk":       0.05,
    "velocity_risk":     0.05,
}

# Risk thresholds
RISK_HIGH   = 70
RISK_MEDIUM = 40

# SHAP sampling cap for large datasets
SHAP_SAMPLE_CAP = 5_000

# Suspicious narration keywords
NARRATION_KEYWORDS = [
    "urgent", "advance", "cash", "bearer", "gift", "personal",
    "loan", "credit", "penalty", "refund", "duplicate", "revision",
    "adjustment", "correction", "misc", "miscellaneous", "transfer",
]

# High-risk payment modes
HIGH_RISK_PAYMENT_MODES = {"RTGS", "Wire", "International Wire", "Cash"}

# Late-night / weekend hour ranges
LATE_NIGHT_HOURS = set(range(0, 6))   # midnight – 5 am
WEEKEND_DAYS     = {5, 6}             # Saturday, Sunday (weekday() numbering)


# ===========================================================================
# 1. LOAD INPUTS
# ===========================================================================
def load_inputs(args):
    """
    Memory-safe loader with sample mode.
    """
    data = {}

    sample_rows = getattr(args, "sample", None)

    def _load_csv(path, label, required=False):
        if not path:
            return None

        p = Path(path)
        if not p.exists():
            if required:
                raise FileNotFoundError(f"{label} not found: {path}")
            log.warning("%s missing.", label)
            return None

        try:
            log.info("[LOAD] %s -> %s", label, path)

            # sample mode
            if sample_rows:
                df = pd.read_csv(p, nrows=sample_rows, low_memory=False)
            else:
                size_mb = p.stat().st_size / (1024 * 1024)

                if size_mb > 300:
                    log.info("[SAFE MODE] Large file detected %.1f MB", size_mb)
                    chunks = []
                    for chunk in pd.read_csv(p, chunksize=100000, low_memory=False):
                        chunks.append(chunk)
                        if len(chunks) >= 5:
                            break
                    df = pd.concat(chunks, ignore_index=True)
                else:
                    df = pd.read_csv(p, low_memory=False)

            log.info("Loaded %s rows", len(df))
            return df

        except Exception as e:
            log.error("Failed reading %s: %s", label, e)
            return None

    data["ledger"] = _load_csv(args.ledger, "Ledger", required=True)
    data["anomaly"] = _load_csv(args.anomaly, "Anomaly")
    data["relationship"] = _load_csv(args.relationship, "Relationship")
    data["fuzzy"] = _load_csv(args.fuzzy, "Fuzzy")

    return data


# ===========================================================================
# 2. LOAD MODEL
# ===========================================================================
def load_model(model_path=None):
    """
    Load trained model safely.
    Supports:
        - joblib (.pkl / .joblib)
        - pickle
        - dict-wrapped objects:
            {"model": ..., "features": [...]}

    Returns:
        (model_object, feature_list)
    """
    if not model_path:
        model_path = find_default_model()

    if not model_path:
        log.warning("No model found.")
        return None, []

    p = Path(model_path)

    if not p.exists():
        log.warning("Model path invalid: %s", model_path)
        return None, []

    obj = None

    # ---------------------------------------------------
    # Try JOBLIB first (best for sklearn models)
    # ---------------------------------------------------
    try:
        import joblib
        obj = joblib.load(p)
        log.info("Model loaded using joblib: %s", model_path)

    except Exception as joblib_err:
        log.warning("Joblib load failed: %s", joblib_err)

        # ---------------------------------------------------
        # Fallback to PICKLE
        # ---------------------------------------------------
        try:
            with open(p, "rb") as f:
                obj = pickle.load(f)

            log.info("Model loaded using pickle: %s", model_path)

        except Exception as pickle_err:
            log.error("Could not load model: %s", pickle_err)
            return None, []

    # ---------------------------------------------------
    # Handle wrapped dict objects
    # ---------------------------------------------------
    try:
        if isinstance(obj, dict):
            model = (
                obj.get("model")
                or obj.get("classifier")
                or obj.get("clf")
                or obj.get("estimator")
            )

            feats = (
                obj.get("features")
                or obj.get("feature_names")
                or obj.get("columns")
                or []
            )

            log.info("Wrapped model detected: %s", type(model).__name__)
            return model, feats

        log.info("Loaded model type: %s", type(obj).__name__)
        return obj, []

    except Exception as e:
        log.error("Loaded object invalid: %s", e)
        return None, []



# ===========================================================================
# 3. MERGE SOURCES
# ===========================================================================
def merge_sources(data: dict) -> pd.DataFrame:
    """Merge ledger with anomaly scores and relationship / vendor risk data."""
    ledger = data["ledger"].copy()

    # ---- Normalise txn_id
    if "txn_id" in ledger.columns:
        ledger["txn_id"] = ledger["txn_id"].astype(str).str.strip()

    # ---- Merge anomaly scores
    anomaly = data.get("anomaly")
    if anomaly is not None:
        anomaly = anomaly.copy()
        if "txn_id" in anomaly.columns:
            anomaly["txn_id"] = anomaly["txn_id"].astype(str).str.strip()
            # Identify score columns robustly
            score_cols = [c for c in anomaly.columns if c not in ledger.columns or c == "txn_id"]
            ledger = ledger.merge(anomaly[score_cols], on="txn_id", how="left", suffixes=("", "_anm"))
            log.info("[MERGE] Anomaly scores merged.")
        else:
            # Try positional merge if txn_id missing
            log.warning("[WARN] Anomaly file has no 'txn_id'; attempting index-based merge.")
            for col in ["fraud_probability", "anomaly_score", "hybrid_risk_score", "predicted_fraud"]:
                if col in anomaly.columns and col not in ledger.columns:
                    ledger[col] = anomaly[col].values[: len(ledger)]

    # ---- Vendor-level relationship risk
    rel = data.get("relationship")
    if rel is not None and "node" in rel.columns:
        vendor_rel = rel[rel["node_type"].str.lower().str.contains("vendor", na=False)].copy()
        vendor_rel = vendor_rel.rename(columns={"node": "vendor_name", "risk_score": "vendor_graph_risk"})
        ledger = ledger.merge(
            vendor_rel[["vendor_name", "vendor_graph_risk"]].drop_duplicates("vendor_name"),
            on="vendor_name", how="left"
        )
        log.info("[MERGE] Vendor graph risk merged.")

    # ---- Approver-level relationship risk
    if rel is not None and "node" in rel.columns:
        approver_rel = rel[rel["node_type"].str.lower().str.contains("approver", na=False)].copy()
        approver_rel = approver_rel.rename(columns={"node": "approver", "risk_score": "approver_graph_risk"})
        ledger = ledger.merge(
            approver_rel[["approver", "approver_graph_risk"]].drop_duplicates("approver"),
            on="approver", how="left"
        )
        log.info("[MERGE] Approver graph risk merged.")

    # ---- Vendor risk summary
    vsumm = data.get("vendor_summary")
    if vsumm is not None and "vendor_name" in vsumm.columns:
        ledger = ledger.merge(
            vsumm[["vendor_name", "avg_risk", "fraud_flags"]].drop_duplicates("vendor_name"),
            on="vendor_name", how="left"
        )
        log.info("[MERGE] Vendor risk summary merged.")

    # ---- Duplicate vendor flag via fuzzy matches
    fuzzy = data.get("fuzzy")
    if fuzzy is not None:
        fuzzy = fuzzy.copy()
        # Build set of vendor names that appear in any HIGH/MEDIUM risk match
        flagged_vendors: set = set()
        for _, row in fuzzy.iterrows():
            risk_val = str(row.get("risk", "")).upper()
            if risk_val in {"HIGH", "MEDIUM"}:
                flagged_vendors.add(str(row.get("vendor_1", "")).strip())
                flagged_vendors.add(str(row.get("vendor_2", "")).strip())
        ledger["fuzzy_duplicate_flag"] = ledger["vendor_name"].isin(flagged_vendors).astype(int)

        # Attach similarity score for the best match
        sim_map: dict = {}
        for _, row in fuzzy.iterrows():
            v1, v2, sim = str(row.get("vendor_1", "")), str(row.get("vendor_2", "")), float(row.get("similarity", 0))
            sim_map[v1] = max(sim_map.get(v1, 0), sim)
            sim_map[v2] = max(sim_map.get(v2, 0), sim)
        ledger["fuzzy_similarity"] = ledger["vendor_name"].map(sim_map).fillna(0.0)
        log.info("[MERGE] Fuzzy duplicate flags merged (%d flagged vendors).", len(flagged_vendors))
    else:
        ledger["fuzzy_duplicate_flag"] = 0
        ledger["fuzzy_similarity"]     = 0.0

    # ---- Datetime engineering
    if "timestamp" in ledger.columns:
        ledger["timestamp"] = pd.to_datetime(ledger["timestamp"], errors="coerce")
        ledger["_hour"]       = ledger["timestamp"].dt.hour
        ledger["_day_of_week"] = ledger["timestamp"].dt.dayofweek
    else:
        # Use existing columns if pre-engineered
        ledger["_hour"]       = ledger.get("hour",       pd.Series(12, index=ledger.index))
        ledger["_day_of_week"] = ledger.get("day_of_week", pd.Series(1,  index=ledger.index))

    log.info("[MERGE] All sources merged → %d rows × %d cols", len(ledger), len(ledger.columns))
    return ledger


# ===========================================================================
# 4. SHAP EXPLANATIONS
# ===========================================================================
def _get_numeric_features(df: pd.DataFrame) -> list:
    """Return numeric columns suitable for SHAP (excluding metadata)."""
    exclude = {
        "txn_id", "invoice_id", "is_fraud", "predicted_fraud",
        "fraud_probability", "anomaly_score", "hybrid_risk_score",
        "fraud_type", "risk_reason", "narration", "vendor_name",
        "approver", "department", "company_name", "internal_account",
        "payment_mode", "device_used", "vendor_city", "timestamp",
        "invoice_date", "due_date", "hour", "day_of_week", "month",
    }
    return [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]


def generate_shap_explanations(
    df: pd.DataFrame,
    model,
    feature_names: list,
    top_n: int = 100,
) -> pd.DataFrame:
    """
    Compute per-transaction SHAP values for the top_n riskiest rows.
    Returns a DataFrame of SHAP contributions indexed by txn_id.
    """
    if model is None:
        log.warning("[SKIP] No model loaded – skipping SHAP.")
        return pd.DataFrame()

    try:
        import shap
    except ImportError:
        log.error("[ERROR] 'shap' not installed.  Run: pip install shap")
        return pd.DataFrame()

    log.info("[SHAP] Preparing feature matrix …")

    # Feature selection
    if feature_names:
        feats = [f for f in feature_names if f in df.columns]
    else:
        feats = _get_numeric_features(df)

    if not feats:
        log.warning("[SHAP] No numeric features found.")
        return pd.DataFrame()

    X = df[feats].fillna(0).astype(float)

    # Determine subset to explain (top_n by hybrid_risk_score / anomaly_score)
    score_col = next(
        (c for c in ["hybrid_risk_score", "anomaly_score", "fraud_probability"] if c in df.columns),
        None
    )
    if score_col:
        idx = X.index[df[score_col].fillna(0).nlargest(min(top_n, SHAP_SAMPLE_CAP)).index]
    else:
        idx = X.index[:min(top_n, SHAP_SAMPLE_CAP)]

    X_sub = X.loc[idx]

    log.info("[SHAP] Computing SHAP values for %d transactions …", len(X_sub))
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sub)

        # For binary classifiers shap_values may be a list; take class-1
        if isinstance(shap_values, list):
            sv = shap_values[1] if len(shap_values) > 1 else shap_values[0]
        else:
            sv = shap_values

        shap_df = pd.DataFrame(sv, columns=[f"shap_{f}" for f in feats], index=X_sub.index)

        # ---- Global SHAP summary plot
        log.info("[SHAP] Generating global summary plot …")
        fig, ax = plt.subplots(figsize=(10, 6))
        shap.summary_plot(sv, X_sub, feature_names=feats, show=False, max_display=20)
        plt.tight_layout()
        fig.savefig(CHART_DIR / "shap_summary_plot.png", dpi=150, bbox_inches="tight")
        plt.close("all")
        log.info("[SAVED] charts/shap_summary_plot.png")

        # ---- Feature importance bar
        mean_abs_shap = np.abs(sv).mean(axis=0)
        fi_df = pd.DataFrame({"feature": feats, "importance": mean_abs_shap}).sort_values(
            "importance", ascending=False
        ).head(20)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(fi_df["feature"][::-1], fi_df["importance"][::-1], color="#E63946")
        ax.set_xlabel("Mean |SHAP value|")
        ax.set_title("SHAP Feature Importance – LedgerSpy Anomaly Model", fontweight="bold")
        plt.tight_layout()
        fig.savefig(CHART_DIR / "shap_feature_importance.png", dpi=150, bbox_inches="tight")
        plt.close("all")
        log.info("[SAVED] charts/shap_feature_importance.png")

        # ---- Waterfall for the single most risky transaction
        top_idx = X_sub.index[0]
        try:
            expl = shap.Explanation(
                values=sv[0],
                base_values=float(explainer.expected_value[1])
                    if isinstance(explainer.expected_value, (list, np.ndarray))
                    else float(explainer.expected_value),
                data=X_sub.iloc[0].values,
                feature_names=feats,
            )
            fig = plt.figure(figsize=(12, 6))
            shap.waterfall_plot(expl, max_display=15, show=False)
            plt.tight_layout()
            txn_label = str(df.loc[top_idx, "txn_id"]) if "txn_id" in df.columns else str(top_idx)
            fig.savefig(CHART_DIR / f"shap_waterfall_top_case_{txn_label}.png", dpi=150, bbox_inches="tight")
            plt.close("all")
            log.info("[SAVED] charts/shap_waterfall_top_case_%s.png", txn_label)
        except Exception as wfe:
            log.warning("[SHAP] Waterfall plot failed: %s", wfe)

        # Attach % contribution per transaction
        total_abs = shap_df.abs().sum(axis=1).replace(0, 1e-9)
        shap_pct_df = shap_df.abs().div(total_abs, axis=0).mul(100).round(2)
        shap_pct_df.columns = [c.replace("shap_", "shapPct_") for c in shap_pct_df.columns]
        combined = pd.concat([shap_df, shap_pct_df], axis=1)

        # Top-3 SHAP features per row
        abs_shap = shap_df.abs()
        abs_shap.columns = feats
        combined["shap_top1_feature"] = abs_shap.idxmax(axis=1)
        combined["shap_top1_pct"]     = abs_shap.max(axis=1).div(total_abs).mul(100).round(1)
        combined["shap_top2_feature"] = abs_shap.apply(lambda r: r.nlargest(2).index[-1] if len(r) >= 2 else "", axis=1)
        combined["shap_top3_feature"] = abs_shap.apply(lambda r: r.nlargest(3).index[-1] if len(r) >= 3 else "", axis=1)

        return combined

    except Exception as exc:
        log.error("[SHAP] Explanation failed: %s", exc)
        return pd.DataFrame()


# ===========================================================================
# 5. RULE ENGINE EXPLANATIONS
# ===========================================================================
def _norm(series: pd.Series, clip_max: float | None = None) -> pd.Series:
    """Min-max normalise a series to [0, 1]."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    out = (series - mn) / (mx - mn)
    if clip_max is not None:
        out = out.clip(upper=clip_max)
    return out


def generate_rule_explanations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute rule-based sub-scores (0–1) for each transaction.
    Returns a DataFrame with the same index as df.
    """
    log.info("[RULES] Computing rule-based risk factors …")
    res = pd.DataFrame(index=df.index)

    # ------------------------------------------------------------------ #
    # A) Model anomaly sub-score (0–1)
    # ------------------------------------------------------------------ #
    for col in ["hybrid_risk_score", "anomaly_score", "fraud_probability"]:
        if col in df.columns:
            res["model_sub"] = _norm(df[col].fillna(0))
            break
    if "model_sub" not in res.columns:
        res["model_sub"] = 0.0

    # ------------------------------------------------------------------ #
    # B) Relationship / graph risk
    # ------------------------------------------------------------------ #
    graph_signals = []
    if "vendor_graph_risk" in df.columns:
        graph_signals.append(_norm(df["vendor_graph_risk"].fillna(0)))
    if "approver_graph_risk" in df.columns:
        graph_signals.append(_norm(df["approver_graph_risk"].fillna(0)))

    res["relationship_sub"] = (
        pd.concat(graph_signals, axis=1).mean(axis=1) if graph_signals else pd.Series(0.0, index=df.index)
    )

    # ------------------------------------------------------------------ #
    # C) Duplicate / fuzzy vendor risk
    # ------------------------------------------------------------------ #
    dup_score = df["fuzzy_duplicate_flag"].fillna(0).astype(float) if "fuzzy_duplicate_flag" in df.columns else pd.Series(0.0, index=df.index)
    sim_score  = df["fuzzy_similarity"].fillna(0).astype(float) / 100.0 if "fuzzy_similarity" in df.columns else pd.Series(0.0, index=df.index)
    res["duplicate_vendor_sub"] = (dup_score * 0.6 + sim_score * 0.4).clip(0, 1)

    # ------------------------------------------------------------------ #
    # D) Amount risk – z-score vs vendor average
    # ------------------------------------------------------------------ #
    if "amount" in df.columns:
        vendor_stats = df.groupby("vendor_name")["amount"].agg(["mean", "std"]).rename(
            columns={"mean": "_vmean", "std": "_vstd"}
        )
        df2 = df.join(vendor_stats, on="vendor_name")
        df2["_vstd"] = df2["_vstd"].fillna(1).replace(0, 1)
        z = ((df2["amount"] - df2["_vmean"]) / df2["_vstd"]).clip(-3, 10).fillna(0)
        res["amount_sub"] = _norm(z.clip(lower=0))
    else:
        res["amount_sub"] = 0.0

    # ------------------------------------------------------------------ #
    # E) Timing risk
    # ------------------------------------------------------------------ #
    LATE_NIGHT_HOURS = {0, 1, 2, 3, 4}
    WEEKEND_DAYS = {5, 6}
    
    hour = df["_hour"].fillna(12).astype(int) if "_hour" in df.columns else pd.Series(12, index=df.index).astype(int)
    dow  = df["_day_of_week"].fillna(1).astype(int) if "_day_of_week" in df.columns else pd.Series(1, index=df.index).astype(int)
    timing = hour.isin(LATE_NIGHT_HOURS).astype(float) * 0.6 + dow.isin(WEEKEND_DAYS).astype(float) * 0.4
    res["timing_sub"] = timing.clip(0, 1)

    # ------------------------------------------------------------------ #
    # F) Velocity risk
    # ------------------------------------------------------------------ #
    if "velocity_score" in df.columns:
        res["velocity_sub"] = _norm(df["velocity_score"].fillna(0))
    else:
        res["velocity_sub"] = 0.0

    # ------------------------------------------------------------------ #
    # G) Location risk
    # ------------------------------------------------------------------ #
    if "vendor_location_risk" in df.columns:
        res["location_sub"] = _norm(df["vendor_location_risk"].fillna(0))
    else:
        res["location_sub"] = 0.0

    # ------------------------------------------------------------------ #
    # H) Payment mode risk
    # ------------------------------------------------------------------ #
    if "payment_mode" in df.columns:
        res["payment_mode_sub"] = df["payment_mode"].isin(HIGH_RISK_PAYMENT_MODES).astype(float)
    else:
        res["payment_mode_sub"] = 0.0

    # ------------------------------------------------------------------ #
    # I) Narration risk
    # ------------------------------------------------------------------ #
    if "narration" in df.columns:
        narr_lower = df["narration"].fillna("").str.lower()
        res["narration_sub"] = narr_lower.apply(
            lambda t: min(1.0, sum(kw in t for kw in NARRATION_KEYWORDS) / 3.0)
        )
    else:
        res["narration_sub"] = 0.0

    log.info("[RULES] Rule sub-scores computed.")
    return res


# ===========================================================================
# 6. CALCULATE FINAL SCORES
# ===========================================================================
def calculate_final_scores(df: pd.DataFrame, rule_df: pd.DataFrame, shap_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine sub-scores into a final 0–100 risk score and per-factor % breakdown.
    """
    log.info("[SCORE] Calculating final composite risk scores …")

    cols = ["txn_id", "vendor_name", "amount", "approver", "department",
            "payment_mode", "narration", "_hour", "_day_of_week",
            "vendor_location_risk", "velocity_score",
            "fuzzy_duplicate_flag", "fuzzy_similarity"]
    existing_cols = [c for c in cols if c in df.columns]
    
    base = df[existing_cols].copy() if "txn_id" in df.columns else df.copy()

    # Weighted composite (0–1)
    w = WEIGHTS
    composite = (
        rule_df["model_sub"]           * w["model_risk"]        +
        rule_df["relationship_sub"]    * w["relationship_risk"]  +
        rule_df["duplicate_vendor_sub"]* w["duplicate_vendor"]   +
        rule_df["amount_sub"]          * w["amount_risk"]        +
        rule_df["timing_sub"]          * w["timing_risk"]        +
        rule_df["velocity_sub"]        * w["velocity_risk"]
    )
    base["final_risk_score"] = (composite * 100).clip(0, 100).round(2)

    # Weighted absolute contributions → percentages
    contribs = pd.DataFrame({
        "model_risk_raw":       rule_df["model_sub"]            * w["model_risk"],
        "relationship_risk_raw":rule_df["relationship_sub"]     * w["relationship_risk"],
        "duplicate_vendor_raw": rule_df["duplicate_vendor_sub"] * w["duplicate_vendor"],
        "amount_risk_raw":      rule_df["amount_sub"]           * w["amount_risk"],
        "timing_risk_raw":      rule_df["timing_sub"]           * w["timing_risk"],
        "velocity_risk_raw":    rule_df["velocity_sub"]         * w["velocity_risk"],
    })
    row_totals = contribs.sum(axis=1).replace(0, 1e-9)

    for col in contribs.columns:
        pct_col = col.replace("_raw", "_pct")
        base[pct_col] = (contribs[col] / row_totals * 100).round(1)

    # Append supplementary sub-scores
    for col in ["location_sub", "payment_mode_sub", "narration_sub"]:
        base[col.replace("_sub", "_risk_raw")] = rule_df[col]

    # Attach SHAP top features if available
    if not shap_df.empty:
        for col in ["shap_top1_feature", "shap_top1_pct", "shap_top2_feature", "shap_top3_feature"]:
            if col in shap_df.columns:
                base[col] = shap_df[col]

    # Anomaly scores pass-through
    for col in ["fraud_probability", "anomaly_score", "hybrid_risk_score", "predicted_fraud"]:
        if col in df.columns:
            base[col] = df[col].values

    # Risk tier
    base["risk_tier"] = pd.cut(
        base["final_risk_score"],
        bins=[-1, RISK_MEDIUM, RISK_HIGH, 101],
        labels=["LOW", "MEDIUM", "HIGH"],
    )

    # Ordered factor columns for top-reason logic
    factor_pct_cols = [
        "model_risk_pct", "relationship_risk_pct",
        "duplicate_vendor_pct", "amount_risk_pct",
        "timing_risk_pct", "velocity_risk_pct",
    ]
    factor_labels = {
        "model_risk_pct":        "ML anomaly score",
        "relationship_risk_pct": "graph/network risk",
        "duplicate_vendor_pct":  "duplicate vendor cluster",
        "amount_risk_pct":       "unusual transaction amount",
        "timing_risk_pct":       "suspicious payment timing",
        "velocity_risk_pct":     "high transaction velocity",
    }

    def _top_reasons(row: pd.Series) -> tuple:
        vals = {k: row.get(k, 0) for k in factor_pct_cols}
        ranked = sorted(vals.items(), key=lambda x: x[1], reverse=True)
        reasons = [(factor_labels[k], v) for k, v in ranked if v > 0]
        pad = ("—", 0.0)
        r1 = reasons[0] if len(reasons) > 0 else pad
        r2 = reasons[1] if len(reasons) > 1 else pad
        r3 = reasons[2] if len(reasons) > 2 else pad
        return r1[0], f"{r1[1]:.1f}%", r2[0], f"{r2[1]:.1f}%", r3[0], f"{r3[1]:.1f}%"

    (
        base["top_reason_1"],
        base["top_reason_1_pct"],
        base["top_reason_2"],
        base["top_reason_2_pct"],
        base["top_reason_3"],
        base["top_reason_3_pct"],
    ) = zip(*base.apply(_top_reasons, axis=1))

    log.info("[SCORE] Final scores computed.  High-risk transactions: %d",
             (base["risk_tier"] == "HIGH").sum())
    return base


# ===========================================================================
# 7. BUILD NARRATIVES
# ===========================================================================
def build_narratives(scored: pd.DataFrame) -> pd.DataFrame:
    """Generate human-readable audit narrative for each flagged transaction."""
    log.info("[NARR] Building audit narratives …")

    def _narrative(row: pd.Series) -> str:
        txn  = row.get("txn_id", "Unknown")
        vend = row.get("vendor_name", "Unknown Vendor")
        amt  = f"₹{row.get('amount', 0):,.0f}"
        score = row.get("final_risk_score", 0)
        tier  = row.get("risk_tier", "MEDIUM")

        reasons = []
        for i in [1, 2, 3]:
            r = row.get(f"top_reason_{i}", "")
            p = row.get(f"top_reason_{i}_pct", "")
            if r and r != "—":
                reasons.append(f"{p} {r}")

        reason_str = "; ".join(reasons) if reasons else "multiple factors"

        # Additional context flags
        extras = []
        if row.get("fuzzy_duplicate_flag", 0):
            sim = row.get("fuzzy_similarity", 0)
            extras.append(f"vendor name similarity {sim:.0f}% to a known duplicate")
        if str(row.get("payment_mode", "")).upper() in HIGH_RISK_PAYMENT_MODES:
            extras.append(f"high-risk payment mode ({row['payment_mode']})")
        hour = int(row.get("_hour", 12))
        if hour in LATE_NIGHT_HOURS:
            extras.append(f"processed at {hour:02d}:00 (late-night window)")
        day = int(row.get("_day_of_week", 1))
        if day in WEEKEND_DAYS:
            extras.append("initiated on a weekend")

        extra_str = ("; additionally: " + ", ".join(extras)) if extras else ""

        return (
            f"Transaction {txn} involving vendor '{vend}' for {amt} is flagged as "
            f"{tier} risk (score: {score:.1f}/100). "
            f"Primary risk drivers: {reason_str}{extra_str}. "
            f"This transaction warrants immediate auditor review."
        )

    scored["narrative_explanation"] = scored.apply(_narrative, axis=1)
    log.info("[NARR] Narratives built.")
    return scored


# ===========================================================================
# 8. SAVE REPORTS
# ===========================================================================
def save_reports(scored: pd.DataFrame, df_full: pd.DataFrame, top_n: int) -> None:
    """Write all output CSVs."""

    # 1) All explained transactions
    out1 = OUT_DIR / "explained_risky_transactions.csv"
    scored.to_csv(out1, index=False)
    log.info("[SAVED] %s (%d rows)", out1, len(scored))

    # 2) Top N highest risk
    top_cols = [
        "txn_id", "vendor_name", "amount", "final_risk_score", "risk_tier",
        "model_risk_pct", "relationship_risk_pct", "duplicate_vendor_pct",
        "amount_risk_pct", "timing_risk_pct", "velocity_risk_pct",
        "top_reason_1", "top_reason_1_pct",
        "top_reason_2", "top_reason_2_pct",
        "top_reason_3", "top_reason_3_pct",
        "narrative_explanation",
    ]
    top_cols_avail = [c for c in top_cols if c in scored.columns]
    top_cases = scored.nlargest(top_n, "final_risk_score")[top_cols_avail]
    out2 = OUT_DIR / "top_explained_cases.csv"
    top_cases.to_csv(out2, index=False)
    log.info("[SAVED] %s (%d rows)", out2, top_n)

    # 3) Risk factor summary
    factor_pct_cols = [c for c in scored.columns if c.endswith("_pct")]
    if factor_pct_cols:
        summary = scored[factor_pct_cols].describe().T
        summary.columns = ["count", "mean_%", "std", "min", "25%", "50%", "75%", "max"]
        out3 = OUT_DIR / "risk_factor_summary.csv"
        summary.to_csv(out3)
        log.info("[SAVED] %s", out3)

    # 4) SHAP transaction explanations placeholder / real
    shap_cols = [c for c in scored.columns if c.startswith("shap_") or c.startswith("shapPct_")]
    if shap_cols:
        shap_out = scored[["txn_id"] + shap_cols] if "txn_id" in scored.columns else scored[shap_cols]
        out4 = OUT_DIR / "shap_transaction_explanations.csv"
        shap_out.to_csv(out4, index=False)
        log.info("[SAVED] %s", out4)

    # 5) Tier breakdown summary
    tier_summary = (
        scored.groupby("risk_tier")
        .agg(
            txn_count=("final_risk_score", "count"),
            avg_risk_score=("final_risk_score", "mean"),
            total_amount=("amount", "sum") if "amount" in scored.columns else ("final_risk_score", "count"),
        )
        .round(2)
    )
    out5 = OUT_DIR / "risk_tier_summary.csv"
    tier_summary.to_csv(out5)
    log.info("[SAVED] %s", out5)


# ===========================================================================
# 9. CREATE CHARTS
# ===========================================================================
def _style_ax(ax, title: str, xlabel: str = "", ylabel: str = "") -> None:
    ax.set_title(title, fontweight="bold", fontsize=12, pad=10)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linestyle="--")


def create_charts(scored: pd.DataFrame, top_n: int = 20) -> None:
    """Generate all PNG charts."""
    log.info("[CHARTS] Generating visualisations …")
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.dpi": 120})

    # Palette
    PALETTE = ["#E63946", "#F4A261", "#2A9D8F", "#264653", "#E9C46A", "#A8DADC"]

    # ------------------------------------------------------------------ #
    # 1. Top Risky Transactions – horizontal bar
    # ------------------------------------------------------------------ #
    top = scored.nlargest(min(top_n, 25), "final_risk_score")
    if not top.empty and "txn_id" in top.columns:
        fig, ax = plt.subplots(figsize=(12, 7))
        colours = [PALETTE[0] if s >= RISK_HIGH else PALETTE[1] if s >= RISK_MEDIUM else PALETTE[2]
                   for s in top["final_risk_score"]]
        ax.barh(top["txn_id"].astype(str)[::-1], top["final_risk_score"][::-1], color=colours[::-1])
        ax.axvline(RISK_HIGH,   color=PALETTE[0], linestyle="--", linewidth=1.2, label=f"High >{RISK_HIGH}")
        ax.axvline(RISK_MEDIUM, color=PALETTE[1], linestyle="--", linewidth=1.2, label=f"Medium >{RISK_MEDIUM}")
        ax.legend(fontsize=9)
        _style_ax(ax, "Top Risky Transactions – Final Risk Score", "Risk Score (0–100)", "Transaction ID")
        plt.tight_layout()
        fig.savefig(CHART_DIR / "top_risky_transactions.png", bbox_inches="tight")
        plt.close("all")
        log.info("[SAVED] charts/top_risky_transactions.png")

    # ------------------------------------------------------------------ #
    # 2. Risk Factor Contribution Pie (mean across high-risk txns)
    # ------------------------------------------------------------------ #
    factor_pct_cols = {
        "model_risk_pct":        "ML Anomaly",
        "relationship_risk_pct": "Graph/Network",
        "duplicate_vendor_pct":  "Duplicate Vendor",
        "amount_risk_pct":       "Amount Anomaly",
        "timing_risk_pct":       "Timing Risk",
        "velocity_risk_pct":     "Velocity Risk",
    }
    avail = {k: v for k, v in factor_pct_cols.items() if k in scored.columns}
    if avail:
        high_risk = scored[scored["risk_tier"] == "HIGH"]
        means = [high_risk[k].mean() for k in avail]
        labels = list(avail.values())
        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(
            means, labels=labels, autopct="%1.1f%%",
            colors=PALETTE[:len(means)], startangle=140,
            wedgeprops=dict(edgecolor="white", linewidth=1.5)
        )
        for at in autotexts:
            at.set_fontsize(9)
        ax.set_title("Risk Factor Contributions\n(Average across HIGH-risk transactions)",
                     fontweight="bold", fontsize=12)
        plt.tight_layout()
        fig.savefig(CHART_DIR / "risk_factor_pie.png", bbox_inches="tight")
        plt.close("all")
        log.info("[SAVED] charts/risk_factor_pie.png")

    # ------------------------------------------------------------------ #
    # 3. Risk Score Distribution
    # ------------------------------------------------------------------ #
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(scored["final_risk_score"].dropna(), bins=50, color=PALETTE[2], edgecolor="white", alpha=0.85)
    ax.axvline(RISK_HIGH,   color=PALETTE[0], linestyle="--", linewidth=1.5, label=f"High Threshold ({RISK_HIGH})")
    ax.axvline(RISK_MEDIUM, color=PALETTE[1], linestyle="--", linewidth=1.5, label=f"Medium Threshold ({RISK_MEDIUM})")
    ax.legend()
    _style_ax(ax, "Risk Score Distribution", "Final Risk Score (0–100)", "Number of Transactions")
    plt.tight_layout()
    fig.savefig(CHART_DIR / "risk_score_distribution.png", bbox_inches="tight")
    plt.close("all")
    log.info("[SAVED] charts/risk_score_distribution.png")

    # ------------------------------------------------------------------ #
    # 4. Top Risky Vendors
    # ------------------------------------------------------------------ #
    if "vendor_name" in scored.columns:
        vendor_risk = (
            scored.groupby("vendor_name")["final_risk_score"]
            .mean().nlargest(15).sort_values()
        )
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(vendor_risk.index, vendor_risk.values, color=PALETTE[0])
        _style_ax(ax, "Top 15 Risky Vendors (avg risk score)", "Avg Risk Score", "Vendor")
        plt.tight_layout()
        fig.savefig(CHART_DIR / "top_risky_vendors.png", bbox_inches="tight")
        plt.close("all")
        log.info("[SAVED] charts/top_risky_vendors.png")

    # ------------------------------------------------------------------ #
    # 5. Top Risky Approvers
    # ------------------------------------------------------------------ #
    if "approver" in scored.columns:
        app_risk = (
            scored.groupby("approver")["final_risk_score"]
            .mean().nlargest(15).sort_values()
        )
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(app_risk.index, app_risk.values, color=PALETTE[1])
        _style_ax(ax, "Top 15 Risky Approvers (avg risk score)", "Avg Risk Score", "Approver")
        plt.tight_layout()
        fig.savefig(CHART_DIR / "top_risky_approvers.png", bbox_inches="tight")
        plt.close("all")
        log.info("[SAVED] charts/top_risky_approvers.png")

    # ------------------------------------------------------------------ #
    # 6. Risk Tier Breakdown
    # ------------------------------------------------------------------ #
    if "risk_tier" in scored.columns:
        tier_counts = scored["risk_tier"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 5))
        colours = {"HIGH": PALETTE[0], "MEDIUM": PALETTE[1], "LOW": PALETTE[2]}
        bars = ax.bar(
            tier_counts.index, tier_counts.values,
            color=[colours.get(t, PALETTE[3]) for t in tier_counts.index]
        )
        for bar, val in zip(bars, tier_counts.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2, str(val),
                    ha="center", va="bottom", fontweight="bold")
        _style_ax(ax, "Risk Tier Breakdown", "Risk Tier", "Transaction Count")
        plt.tight_layout()
        fig.savefig(CHART_DIR / "risk_tier_breakdown.png", bbox_inches="tight")
        plt.close("all")
        log.info("[SAVED] charts/risk_tier_breakdown.png")

    # ------------------------------------------------------------------ #
    # 7. Risk Factor Stacked Bar – Top 20 Transactions
    # ------------------------------------------------------------------ #
    fpc = [c for c in ["model_risk_pct", "relationship_risk_pct", "duplicate_vendor_pct",
                        "amount_risk_pct", "timing_risk_pct", "velocity_risk_pct"]
           if c in scored.columns]
    if fpc and "txn_id" in scored.columns:
        top20 = scored.nlargest(20, "final_risk_score")[["txn_id"] + fpc].set_index("txn_id")
        fig, ax = plt.subplots(figsize=(14, 7))
        bottom = pd.Series(0.0, index=top20.index)
        for col, colour in zip(fpc, PALETTE):
            ax.bar(top20.index.astype(str), top20[col], bottom=bottom,
                   label=col.replace("_pct", "").replace("_", " ").title(), color=colour)
            bottom += top20[col]
        ax.legend(loc="upper right", fontsize=8)
        ax.set_xticklabels(top20.index.astype(str), rotation=45, ha="right", fontsize=8)
        _style_ax(ax, "Risk Factor Breakdown – Top 20 Transactions", "Transaction", "% Contribution")
        plt.tight_layout()
        fig.savefig(CHART_DIR / "risk_factor_stacked_bar.png", bbox_inches="tight")
        plt.close("all")
        log.info("[SAVED] charts/risk_factor_stacked_bar.png")

    # ------------------------------------------------------------------ #
    # 8. Amount vs Risk Score scatter
    # ------------------------------------------------------------------ #
    if "amount" in scored.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        tier_map = {"HIGH": PALETTE[0], "MEDIUM": PALETTE[1], "LOW": PALETTE[2]}
        for tier, grp in scored.groupby("risk_tier"):
            ax.scatter(grp["amount"], grp["final_risk_score"],
                       c=tier_map.get(tier, PALETTE[3]), alpha=0.5, s=15, label=tier)
        ax.legend()
        _style_ax(ax, "Transaction Amount vs Risk Score", "Amount (₹)", "Risk Score")
        ax.grid(True, alpha=0.2)
        plt.tight_layout()
        fig.savefig(CHART_DIR / "amount_vs_risk_scatter.png", bbox_inches="tight")
        plt.close("all")
        log.info("[SAVED] charts/amount_vs_risk_scatter.png")

    log.info("[CHARTS] All charts saved to %s/", CHART_DIR)


# ===========================================================================
# 10. CREATE HTML DASHBOARD
# ===========================================================================
def create_dashboard(scored: pd.DataFrame, top_n: int = 50) -> None:
    """Generate a self-contained HTML audit dashboard."""
    log.info("[DASH] Building HTML dashboard …")

    total     = len(scored)
    high      = int((scored["risk_tier"] == "HIGH").sum())
    medium    = int((scored["risk_tier"] == "MEDIUM").sum())
    low       = int((scored["risk_tier"] == "LOW").sum())
    avg_score = float(scored["final_risk_score"].mean())
    total_amt = float(scored["amount"].sum()) if "amount" in scored.columns else 0

    top_cases = scored.nlargest(top_n, "final_risk_score")

    # Build table rows
    rows_html = ""
    for _, row in top_cases.iterrows():
        tier = row.get("risk_tier", "MEDIUM")
        badge_colour = {"HIGH": "#E63946", "MEDIUM": "#F4A261", "LOW": "#2A9D8F"}.get(tier, "#888")
        score = row.get("final_risk_score", 0)
        bar_w = int(score)
        rows_html += f"""
        <tr>
          <td>{row.get('txn_id','')}</td>
          <td>{row.get('vendor_name','')}</td>
          <td>₹{row.get('amount',0):,.0f}</td>
          <td>
            <div class="score-bar-wrap">
              <div class="score-bar" style="width:{bar_w}%;background:{badge_colour}"></div>
              <span>{score:.1f}</span>
            </div>
          </td>
          <td><span class="badge" style="background:{badge_colour}">{tier}</span></td>
          <td>{row.get('top_reason_1','—')} ({row.get('top_reason_1_pct','—')})</td>
          <td>{row.get('top_reason_2','—')} ({row.get('top_reason_2_pct','—')})</td>
          <td style="max-width:350px;font-size:11px">{row.get('narrative_explanation','—')}</td>
        </tr>"""

    # Chart img tags (only include if files exist)
    def _img(fname: str, caption: str) -> str:
        p = CHART_DIR / fname
        if p.exists():
            return f"""
            <div class="chart-card">
              <img src="charts/{fname}" alt="{caption}" />
              <p>{caption}</p>
            </div>"""
        return ""

    charts_html = "".join([
        _img("top_risky_transactions.png",    "Top Risky Transactions"),
        _img("risk_factor_pie.png",           "Risk Factor Contributions"),
        _img("risk_score_distribution.png",   "Risk Score Distribution"),
        _img("top_risky_vendors.png",         "Top Risky Vendors"),
        _img("top_risky_approvers.png",       "Top Risky Approvers"),
        _img("risk_tier_breakdown.png",       "Risk Tier Breakdown"),
        _img("risk_factor_stacked_bar.png",   "Risk Factor Stack – Top 20"),
        _img("amount_vs_risk_scatter.png",    "Amount vs Risk Score"),
        _img("shap_summary_plot.png",         "SHAP Summary Plot"),
        _img("shap_feature_importance.png",   "SHAP Feature Importance"),
    ])

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>LedgerSpy – Explainable Risk Insights</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{font-family:'Segoe UI',Arial,sans-serif;background:#0f1117;color:#e0e0e0;}}
  header{{background:linear-gradient(135deg,#1a1f2e,#16213e);padding:24px 32px;border-bottom:2px solid #E63946;}}
  header h1{{font-size:26px;color:#fff;letter-spacing:1px;}}
  header p{{color:#aaa;font-size:13px;margin-top:4px;}}
  .kpi-row{{display:flex;flex-wrap:wrap;gap:16px;padding:24px 32px;background:#13161f;}}
  .kpi{{flex:1;min-width:160px;background:#1c2030;border-radius:10px;padding:18px 22px;
        border-left:4px solid #E63946;}}
  .kpi .val{{font-size:28px;font-weight:700;color:#fff;}}
  .kpi .lbl{{font-size:12px;color:#aaa;margin-top:4px;}}
  .section{{padding:24px 32px;}}
  .section h2{{font-size:16px;color:#E63946;margin-bottom:14px;letter-spacing:0.5px;text-transform:uppercase;}}
  table{{width:100%;border-collapse:collapse;font-size:12px;}}
  th{{background:#1c2030;padding:10px 8px;text-align:left;color:#aaa;font-weight:600;border-bottom:1px solid #2a2f3e;}}
  td{{padding:9px 8px;border-bottom:1px solid #1c2030;vertical-align:top;}}
  tr:hover td{{background:#1c2030;}}
  .badge{{display:inline-block;padding:2px 10px;border-radius:20px;font-size:11px;
          font-weight:700;color:#fff;}}
  .score-bar-wrap{{display:flex;align-items:center;gap:8px;}}
  .score-bar{{height:8px;border-radius:4px;transition:width .3s;}}
  .score-bar-wrap span{{font-weight:700;font-size:12px;color:#fff;min-width:36px;}}
  .charts-grid{{display:flex;flex-wrap:wrap;gap:20px;}}
  .chart-card{{background:#1c2030;border-radius:10px;padding:16px;flex:1;min-width:380px;text-align:center;}}
  .chart-card img{{width:100%;border-radius:6px;}}
  .chart-card p{{font-size:11px;color:#aaa;margin-top:8px;}}
  footer{{text-align:center;padding:24px;font-size:11px;color:#555;border-top:1px solid #1c2030;}}
  a.dl-link{{display:inline-block;margin:4px 6px;padding:7px 18px;border:1px solid #E63946;
             color:#E63946;text-decoration:none;border-radius:6px;font-size:12px;}}
  a.dl-link:hover{{background:#E63946;color:#fff;}}
</style>
</head>
<body>
<header>
  <h1>🔍 LedgerSpy — Explainable Risk Insights</h1>
  <p>Audit-grade fraud explainability dashboard &nbsp;|&nbsp; Generated: {now}</p>
</header>

<div class="kpi-row">
  <div class="kpi"><div class="val">{total:,}</div><div class="lbl">Transactions Analysed</div></div>
  <div class="kpi" style="border-color:#E63946"><div class="val" style="color:#E63946">{high:,}</div><div class="lbl">HIGH Risk</div></div>
  <div class="kpi" style="border-color:#F4A261"><div class="val" style="color:#F4A261">{medium:,}</div><div class="lbl">MEDIUM Risk</div></div>
  <div class="kpi" style="border-color:#2A9D8F"><div class="val" style="color:#2A9D8F">{low:,}</div><div class="lbl">LOW Risk</div></div>
  <div class="kpi" style="border-color:#E9C46A"><div class="val" style="color:#E9C46A">{avg_score:.1f}</div><div class="lbl">Avg Risk Score</div></div>
  <div class="kpi" style="border-color:#A8DADC"><div class="val" style="color:#A8DADC">₹{total_amt/1e6:.1f}M</div><div class="lbl">Total Flagged Amount</div></div>
</div>

<div class="section">
  <h2>📋 Top {top_n} Explained High-Risk Transactions</h2>
  <div style="overflow-x:auto">
  <table>
    <thead>
      <tr>
        <th>TXN ID</th><th>Vendor</th><th>Amount</th><th>Risk Score</th><th>Tier</th>
        <th>Top Reason 1</th><th>Top Reason 2</th><th>Audit Narrative</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
  </div>
</div>

<div class="section">
  <h2>📊 Risk Charts</h2>
  <div class="charts-grid">{charts_html}</div>
</div>

<div class="section">
  <h2>⬇ Download Reports</h2>
  <a class="dl-link" href="explained_risky_transactions.csv">Explained Risky Transactions</a>
  <a class="dl-link" href="top_explained_cases.csv">Top Explained Cases</a>
  <a class="dl-link" href="risk_factor_summary.csv">Risk Factor Summary</a>
  <a class="dl-link" href="shap_transaction_explanations.csv">SHAP Explanations</a>
  <a class="dl-link" href="risk_tier_summary.csv">Risk Tier Summary</a>
</div>

<footer>
  LedgerSpy Explainable Risk Insights &copy; {datetime.now().year} &nbsp;|&nbsp;
  For internal audit use only. Not for redistribution.
</footer>
</body>
</html>"""

    out = OUT_DIR / "explainable_dashboard.html"
    out.write_text(html, encoding="utf-8")
    log.info("[SAVED] %s", out)


def run_analysis(
    ledger_path,
    anomaly_path=None,
    relationship_path=None,
    fuzzy_path=None,
    model_path=None,
    top_n=100,
    sample_rows=None,
    generate_charts_flag=True,
    generate_dashboard_flag=True
):
    """
    Backend/API callable function.
    """

    class Args:
        pass

    args = Args()
    args.ledger = ledger_path
    args.anomaly = anomaly_path
    args.relationship = relationship_path
    args.fuzzy = fuzzy_path
    args.model = model_path
    args.top_n = top_n
    args.sample = sample_rows

    log.info("Starting LedgerSpy analysis...")

    data = load_inputs(args)

    if data["ledger"] is None:
        return {"status": "failed", "reason": "ledger file not loaded"}

    model, feature_names = load_model(args.model)

    df = merge_sources(data)

    shap_df = generate_shap_explanations(df, model, feature_names, top_n=top_n)

    rule_df = generate_rule_explanations(df)

    scored = calculate_final_scores(df, rule_df, shap_df)

    scored = build_narratives(scored)

    save_reports(scored, df, top_n=top_n)

    if generate_charts_flag:
        create_charts(scored, top_n=top_n)

    if generate_dashboard_flag:
        create_dashboard(scored, top_n=top_n)

    total = len(scored)
    high = int((scored["risk_tier"] == "HIGH").sum())
    med = int((scored["risk_tier"] == "MEDIUM").sum())
    low = int((scored["risk_tier"] == "LOW").sum())

    return {
        "status": "success",
        "rows_processed": total,
        "high_risk_count": high,
        "medium_risk_count": med,
        "low_risk_count": low,
        "output_folder": str(OUT_DIR),
        "dashboard": str(OUT_DIR / "explainable_dashboard.html"),
        "csv_outputs": [
            "explained_risky_transactions.csv",
            "top_explained_cases.csv",
            "risk_factor_summary.csv"
        ]
    }


# ===========================================================================
# MAIN
# ===========================================================================
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--ledger", required=True)
    parser.add_argument("--anomaly")
    parser.add_argument("--relationship")
    parser.add_argument("--fuzzy")
    parser.add_argument("--model")
    parser.add_argument("--top-n", type=int, default=100)

    parser.add_argument("--sample", type=int, default=None)

    parser.add_argument("--no-charts", action="store_true")
    parser.add_argument("--no-dashboard", action="store_true")

    args = parser.parse_args()

    result = run_analysis(
        ledger_path=args.ledger,
        anomaly_path=args.anomaly,
        relationship_path=args.relationship,
        fuzzy_path=args.fuzzy,
        model_path=args.model,
        top_n=args.top_n,
        sample_rows=args.sample,
        generate_charts_flag=not args.no_charts,
        generate_dashboard_flag=not args.no_dashboard
    )

    print(json.dumps(result, indent=2))


def explain_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Wrapper function for Streamlit App safely extracting explaining scores."""
    if df is None or df.empty:
        return df
    
    # 1. Rule Engine Explanations
    rule_df = generate_rule_explanations(df)
    
    # 2. Final Risk Score (Mock empty SHAP DF for UI fast performance)
    shap_df = pd.DataFrame(index=df.index)
    scored = calculate_final_scores(df, rule_df, shap_df)
    
    # 3. Add narratives
    scored = build_narratives(scored)
    
    return scored


if __name__ == "__main__":
    main()
