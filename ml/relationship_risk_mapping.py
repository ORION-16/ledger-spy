# =============================================================
# LedgerSpy FINAL Relationship Risk Mapping + Fuzzy Integration
# -------------------------------------------------------------
# Uses:
#   1. transactions.csv
#   2. fuzzy_matches.csv   (required for duplicate vendors)
#
# Outputs:
#   risk_graph.html
#   node_risk_scores.csv
#   top_risky_vendors.csv
#   top_risky_approvers.csv
#
# Run:
# python relationship_risk_mapping.py ^
#   --input LedgerSpy_Final_Realistic.csv ^
#   --fuzzy fuzzy_matches.csv ^
#   --top-vendors 80
#
# Requirements:
# pip install pandas numpy networkx pyvis
# =============================================================

import pandas as pd
import numpy as np
import argparse
from pathlib import Path
import networkx as nx
from pyvis.network import Network

# -------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------

COL = {
    "txn_id": "txn_id",
    "amount": "amount",
    "vendor_name": "vendor_name",
    "internal_account": "internal_account",
    "approver": "approver",
    "department": "department",
    "is_fraud": "is_fraud"
}

COLOR = {
    "vendor": "#d62728",
    "approver": "#1f77b4",
    "account": "#2ca02c",
    "department": "#ff7f0e"
}


# =============================================================
# LOAD DATA
# =============================================================

def load_transactions(path):
    print("[INFO] Loading transactions...")

    usecols = [
        "txn_id",
        "amount",
        "vendor_name",
        "internal_account",
        "approver",
        "department",
        "is_fraud"
    ]

    df = pd.read_csv(path, usecols=usecols, low_memory=False)

    print(f"[INFO] Rows loaded: {len(df):,}")
    return df


def load_fuzzy(path):
    print("[INFO] Loading fuzzy duplicate matches...")

    fuzzy = pd.read_csv(path)

    print(f"[INFO] Duplicate vendor pairs: {len(fuzzy)}")
    return fuzzy


# =============================================================
# APPLY FUZZY CANONICALIZATION
# =============================================================

def canonicalize_vendors(df, fuzzy):

    mapping = {}

    for _, row in fuzzy.iterrows():

        v1 = str(row["vendor_1"]).strip()
        v2 = str(row["vendor_2"]).strip()

        # choose shorter cleaner name
        canonical = min([v1, v2], key=len)

        mapping[v1] = canonical
        mapping[v2] = canonical

    df["vendor_name_original"] = df["vendor_name"]

    df["vendor_name"] = (
        df["vendor_name"]
        .astype(str)
        .map(mapping)
        .fillna(df["vendor_name"].astype(str))
    )

    print("[INFO] Vendor canonicalization applied.")

    return df, mapping


# =============================================================
# AGGREGATE GRAPH EDGES
# =============================================================

def aggregate_edges(df, top_vendors=80):

    print("[INFO] Aggregating graph edges...")

    top_vendor_list = (
        df.groupby("vendor_name")["amount"]
        .sum()
        .nlargest(top_vendors)
        .index
    )

    sub = df[df["vendor_name"].isin(top_vendor_list)].copy()

    # account -> vendor
    e1 = (
        sub.groupby(["internal_account", "vendor_name"])
        .agg(
            txn_count=("txn_id", "count"),
            total_amount=("amount", "sum"),
            fraud_count=("is_fraud", lambda x: x.astype(str).str.lower().isin(["true","1"]).sum())
        )
        .reset_index()
    )

    e1["source_type"] = "account"
    e1["target_type"] = "vendor"
    e1.rename(columns={
        "internal_account":"source",
        "vendor_name":"target"
    }, inplace=True)

    # approver -> vendor
    e2 = (
        sub.groupby(["approver", "vendor_name"])
        .agg(
            txn_count=("txn_id", "count"),
            total_amount=("amount", "sum"),
            fraud_count=("is_fraud", lambda x: x.astype(str).str.lower().isin(["true","1"]).sum())
        )
        .reset_index()
    )

    e2["source_type"] = "approver"
    e2["target_type"] = "vendor"
    e2.rename(columns={
        "approver":"source",
        "vendor_name":"target"
    }, inplace=True)

    # dept -> vendor
    e3 = (
        sub.groupby(["department", "vendor_name"])
        .agg(
            txn_count=("txn_id", "count"),
            total_amount=("amount", "sum"),
            fraud_count=("is_fraud", lambda x: x.astype(str).str.lower().isin(["true","1"]).sum())
        )
        .reset_index()
    )

    e3["source_type"] = "department"
    e3["target_type"] = "vendor"
    e3.rename(columns={
        "department":"source",
        "vendor_name":"target"
    }, inplace=True)

    edges = pd.concat([e1, e2, e3], ignore_index=True)

    print(f"[INFO] Total edges: {len(edges):,}")

    return edges


# =============================================================
# BUILD GRAPH
# =============================================================

def build_graph(edges):

    G = nx.DiGraph()

    for row in edges.itertuples(index=False):

        src = str(row.source)
        dst = str(row.target)

        if src not in G:
            G.add_node(src, node_type=row.source_type)

        if dst not in G:
            G.add_node(dst, node_type=row.target_type)

        G.add_edge(
            src,
            dst,
            txn_count=int(row.txn_count),
            total_amount=float(row.total_amount),
            fraud_count=int(row.fraud_count),
            weight=float(row.total_amount)
        )

    print(
        f"[INFO] Graph built: "
        f"{G.number_of_nodes()} nodes / {G.number_of_edges()} edges"
    )

    return G


# =============================================================
# RISK METRICS
# =============================================================


def compute_scores(G, fuzzy):

    print("[INFO] Computing intelligent risk scores...")

    deg = nx.degree_centrality(G)

    bet = nx.betweenness_centrality(
        G,
        k=min(100, G.number_of_nodes()),
        weight="weight",
        seed=42
    )

    duplicate_nodes = set()

    for _, row in fuzzy.iterrows():
        duplicate_nodes.add(str(row["vendor_1"]))
        duplicate_nodes.add(str(row["vendor_2"]))

    rows = []

    for node in G.nodes():

        node = str(node)

        ntype = G.nodes[node].get("node_type", "unknown")

        in_edges = list(G.in_edges(node, data=True))
        out_edges = list(G.out_edges(node, data=True))
        all_edges = in_edges + out_edges

        total_amt = sum(
            d.get("total_amount", 0)
            for _, _, d in all_edges
        )

        txn_count = sum(
            d.get("txn_count", 0)
            for _, _, d in all_edges
        )

        fraud_links = sum(
            d.get("fraud_count", 0)
            for _, _, d in all_edges
        )

        unique_connections = len(
            set(
                [u for u, _, _ in in_edges] +
                [v for _, v, _ in out_edges]
            )
        )

        duplicate_flag = 1 if node in duplicate_nodes else 0

        degree_score = deg.get(node, 0)
        between = bet.get(node, 0)

        # --------------------------------------------------
        # Risk Logic by Type
        # --------------------------------------------------

        if ntype == "vendor":

            avg_txn = total_amt / max(txn_count, 1)

            risk = (
                40 * fraud_links +
                25 * duplicate_flag +
                15 * np.log1p(total_amt) +
                10 * np.log1p(avg_txn) +
                5 * unique_connections +
                5 * degree_score
            )

        elif ntype == "approver":

            risk = (
                30 * fraud_links +
                20 * unique_connections +
                20 * np.log1p(total_amt) +
                10 * txn_count +
                5 * degree_score
            )

        elif ntype == "account":

            risk = (
                20 * np.log1p(total_amt) +
                15 * txn_count +
                10 * unique_connections +
                10 * fraud_links
            )

        elif ntype == "department":

            risk = (
                15 * np.log1p(total_amt) +
                10 * txn_count +
                8 * unique_connections +
                5 * fraud_links
            )

        else:
            risk = 0

        # --------------------------------------------------
        # Reason Builder
        # --------------------------------------------------

        reasons = []

        if duplicate_flag:
            reasons.append("Duplicate vendor cluster")

        if fraud_links > 0:
            reasons.append(f"{fraud_links} fraud-linked connections")

        if total_amt > 1_00_00_000:
            reasons.append("Very high money flow")

        if txn_count > 20:
            reasons.append("High transaction frequency")

        if unique_connections > 8:
            reasons.append("Highly connected entity")

        if not reasons:
            reasons.append("Moderate structural risk")

        rows.append({
            "node": node,
            "node_type": ntype,
            "degree_centrality": round(degree_score, 4),
            "betweenness": round(between, 4),
            "total_amount": round(total_amt, 2),
            "txn_count": txn_count,
            "unique_connections": unique_connections,
            "fraud_links": fraud_links,
            "duplicate_vendor_flag": duplicate_flag,
            "risk_raw": risk,
            "reason": " | ".join(reasons)
        })

    df = pd.DataFrame(rows)

    # normalize separately by node type
    final_parts = []

    for t in df["node_type"].unique():

        temp = df[df["node_type"] == t].copy()

        mn = temp["risk_raw"].min()
        mx = temp["risk_raw"].max()

        if mx - mn == 0:
            temp["risk_score"] = 0
        else:
            temp["risk_score"] = (
                100 *
                (temp["risk_raw"] - mn) /
                (mx - mn)
            )

        final_parts.append(temp)

    final = pd.concat(final_parts)

    final.drop(columns=["risk_raw"], inplace=True)

    final = final.sort_values(
        "risk_score",
        ascending=False
    )

    return final


# =============================================================
# VISUAL GRAPH
# =============================================================

def render_graph(G, metrics):

    net = Network(
        height="850px",
        width="100%",
        bgcolor="#111111",
        font_color="white",
        directed=True
    )

    risk_lookup = dict(
        zip(metrics["node"], metrics["risk_score"])
    )

    max_amt = max(
        [d["total_amount"] for _, _, d in G.edges(data=True)]
    )

    for node in G.nodes():

        ntype = G.nodes[node]["node_type"]

        risk = risk_lookup.get(node, 0)

        size = max(10, min(55, 10 + risk / 2))

        color = COLOR.get(ntype, "#999999")

        net.add_node(
            node,
            label=str(node)[:25],
            color=color,
            size=size,
            title=f"{node}<br>{ntype}<br>Risk: {risk:.1f}"
        )

    for src, dst, d in G.edges(data=True):

        width = max(
            1,
            10 * np.log1p(d["total_amount"]) /
            np.log1p(max_amt)
        )

        edge_color = "#ff4444" if d["fraud_count"] > 0 else "#888888"

        net.add_edge(
            src,
            dst,
            value=width,
            color=edge_color,
            title=f"₹{d['total_amount']:,.0f}"
        )

    net.barnes_hut()

    html_str = net.generate_html()

    # Still write for CLI usage
    net.write_html("risk_graph.html")
    print("[SAVED] risk_graph.html")
    
    return html_str


# =============================================================
# SAVE REPORTS
# =============================================================

def save_reports(metrics):

    metrics.to_csv("node_risk_scores.csv", index=False)

    # Separate outputs
    metrics[
        metrics["node_type"] == "vendor"
    ].sort_values(
        "risk_score",
        ascending=False
    ).to_csv(
        "top_risky_vendors.csv",
        index=False
    )

    metrics[
        metrics["node_type"] == "approver"
    ].sort_values(
        "risk_score",
        ascending=False
    ).to_csv(
        "top_risky_approvers.csv",
        index=False
    )

    metrics[
        metrics["node_type"] == "account"
    ].sort_values(
        "risk_score",
        ascending=False
    ).to_csv(
        "top_risky_accounts.csv",
        index=False
    )

    metrics[
        metrics["node_type"] == "department"
    ].sort_values(
        "risk_score",
        ascending=False
    ).to_csv(
        "top_risky_departments.csv",
        index=False
    )

    print("[SAVED] CSV reports")


# ==========================================================
# ADD THIS NEW FUNCTION
# ==========================================================

def create_dashboard(metrics):

    import matplotlib.pyplot as plt

    # -------------------------
    # Top Vendors
    # -------------------------
    top_v = metrics[
        metrics["node_type"] == "vendor"
    ].head(10)

    plt.figure(figsize=(12,6))
    plt.barh(top_v["node"], top_v["risk_score"])
    plt.gca().invert_yaxis()
    plt.title("Top Risky Vendors")
    plt.tight_layout()
    plt.savefig("dashboard_top_vendors.png")
    plt.close()

    # -------------------------
    # Top Approvers
    # -------------------------
    top_a = metrics[
        metrics["node_type"] == "approver"
    ].head(10)

    plt.figure(figsize=(10,5))
    plt.bar(top_a["node"], top_a["risk_score"])
    plt.xticks(rotation=45, ha="right")
    plt.title("Top Risky Approvers")
    plt.tight_layout()
    plt.savefig("dashboard_top_approvers.png")
    plt.close()

    # -------------------------
    # Node Type Count
    # -------------------------
    metrics["node_type"].value_counts().plot(
        kind="pie",
        autopct="%1.1f%%",
        figsize=(7,7),
        title="Entity Distribution"
    )

    plt.ylabel("")
    plt.tight_layout()
    plt.savefig("dashboard_entity_mix.png")
    plt.close()

    print("[SAVED] Dashboard charts")



def run_risk_pipeline(df: pd.DataFrame, fuzzy_df: pd.DataFrame = None, top_vendors: int = 80):
    """
    Main entry point for Streamlit application to run risk mapping directly in memory.
    """
    print("[INFO] Starting in-memory risk pipeline...")
    
    # 1) Work with copies
    df_clean = df.copy()
    if fuzzy_df is None or fuzzy_df.empty:
        # Create dummy fuzzy DF if none provided
        fuzzy_df = pd.DataFrame(columns=["vendor_1", "vendor_2"])
    
    # Optional mapping if "vendor_1" and "vendor_2" are in fuzzy_df
    if "vendor_1" in fuzzy_df.columns and "vendor_2" in fuzzy_df.columns:
        df_clean, mapping = canonicalize_vendors(df_clean, fuzzy_df)
    
    # 2) Edges
    edges = aggregate_edges(df_clean, top_vendors=top_vendors)
    
    # 3) Build Graph
    G = build_graph(edges)
    
    # 4) Compute Scores
    metrics_df = compute_scores(G, fuzzy_df)
    
    # 5) Render Interactive HTML
    net_html = render_graph(G, metrics_df)
    
    return metrics_df, G, net_html


# =============================================================
# MAIN
# =============================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True
    )

    parser.add_argument(
        "--fuzzy",
        required=True
    )

    parser.add_argument(
        "--top-vendors",
        type=int,
        default=80
    )

    args = parser.parse_args()

    df = load_transactions(args.input)

    fuzzy = load_fuzzy(args.fuzzy)

    df, mapping = canonicalize_vendors(df, fuzzy)

    edges = aggregate_edges(
        df,
        top_vendors=args.top_vendors
    )

    G = build_graph(edges)

    metrics = compute_scores(G, fuzzy)

    render_graph(G, metrics)

    save_reports(metrics)

    create_dashboard(metrics)

    print("\n[DONE] Relationship Risk Mapping Complete")


if __name__ == "__main__":
    main()