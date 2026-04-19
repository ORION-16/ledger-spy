import pandas as pd
import numpy as np

def reconcile(ledger_df, bank_df):
    ledger = ledger_df.copy()
    bank = bank_df.copy()

    # Determine a common key
    possible_keys = ["invoice_id", "txn_id", "transaction_id", "id", "bank_txn_id"]
    merge_key = None
    for k in possible_keys:
        if k in ledger.columns and k in bank.columns:
            merge_key = k
            break
            
    if merge_key:
        merged = ledger.merge(bank, on=merge_key, how="left", suffixes=("_ledger", "_bank"))
        if "amount_ledger" not in merged.columns:
            merged["amount_ledger"] = ledger.get("amount", 0)
        if "amount_bank" not in merged.columns:
            merged["amount_bank"] = merged.get("amount", None)
    else:
        # Fallback amount-based matching with duplicate prevention
        merged = ledger.copy()
        merged["amount_ledger"] = merged.get("amount", 0)
        merged["amount_bank"] = None
        
        if "amount" in bank.columns and "amount_ledger" in merged.columns:
            bank_copy = bank.copy()
            bank_copy["amount"] = pd.to_numeric(bank_copy["amount"], errors="coerce").fillna(0)
            merged["amount_ledger"] = pd.to_numeric(merged["amount_ledger"], errors="coerce").fillna(0)
            bank_copy["_matched"] = False
            
            for i, row in merged.iterrows():
                amt = row["amount_ledger"]
                if pd.notna(amt) and amt != 0:
                    candidates = bank_copy[
                        (~bank_copy["_matched"]) &
                        (bank_copy["amount"] >= amt * 0.95) &
                        (bank_copy["amount"] <= amt * 1.05)
                    ]
                    if not candidates.empty:
                        match_idx = candidates.index[0]
                        merged.at[i, "amount_bank"] = candidates.loc[match_idx, "amount"]
                        bank_copy.at[match_idx, "_matched"] = True
                        
    def classify(row):
        if pd.isna(row.get("amount_bank")):
            return "MISSING"
        elif abs(row.get("amount_ledger", 0) - row.get("amount_bank", 0)) < 1e-6:
            return "MATCHED"
        else:
            return "PARTIAL"

    merged["status"] = merged.apply(classify, axis=1)

    # Ensure required UI columns exist natively for strict endpoints
    if "txn_id" not in merged.columns and "transaction_id" in merged.columns:
        merged["txn_id"] = merged["transaction_id"]
    elif "txn_id" not in merged.columns:
        merged["txn_id"] = merged.index

    if "vendor_name" not in merged.columns:
        merged["vendor_name"] = "Unknown Vendor"

    return merged[[
        "txn_id",
        "vendor_name",
        "amount_ledger",
        "amount_bank",
        "status"
    ]]