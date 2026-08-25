import pandas as pd


# ============================================================
# VENDOR RECONCILIATION COPILOT
# ============================================================

# ------------------------------------------------------------
# STEP 1: Read CSV files
# ------------------------------------------------------------

vendor_data = pd.read_csv("vendor_statement.csv")
ledger_data = pd.read_csv("internal_ledger.csv")


# ------------------------------------------------------------
# STEP 2: Display input data
# ------------------------------------------------------------

print("=" * 60)
print("        VENDOR RECONCILIATION COPILOT")
print("=" * 60)

print("\nVENDOR STATEMENT")
print("-" * 60)
print(vendor_data.to_string(index=False))

print("\nINTERNAL LEDGER")
print("-" * 60)
print(ledger_data.to_string(index=False))


# ------------------------------------------------------------
# STEP 3: Calculate totals
# ------------------------------------------------------------

vendor_total = vendor_data["amount"].sum()
ledger_total = ledger_data["amount"].sum()

difference = vendor_total - ledger_total


# ------------------------------------------------------------
# STEP 4: Transaction Matching
# ------------------------------------------------------------

results = []

matched_ledger_ids = set()

for index, vendor in vendor_data.iterrows():

    transaction_id = vendor["transaction_id"]
    vendor_amount = vendor["amount"]

    # Find same transaction ID
    match = ledger_data[
        (ledger_data["transaction_id"] == transaction_id)
    ]

    if match.empty:

        results.append({
            "transaction_id": transaction_id,
            "vendor_amount": vendor_amount,
            "ledger_amount": 0,
            "difference": vendor_amount,
            "status": "MISSING IN LEDGER"
        })

    else:

        ledger_row = match.iloc[0]

        ledger_amount = ledger_row["amount"]

        matched_ledger_ids.add(transaction_id)

        amount_difference = (
            vendor_amount - ledger_amount
        )

        if amount_difference == 0:

            status = "MATCHED"

        else:

            status = "AMOUNT MISMATCH"

        results.append({
            "transaction_id": transaction_id,
            "vendor_amount": vendor_amount,
            "ledger_amount": ledger_amount,
            "difference": amount_difference,
            "status": status
        })


# ------------------------------------------------------------
# STEP 5: Find transactions present only in ledger
# ------------------------------------------------------------

for index, ledger in ledger_data.iterrows():

    transaction_id = ledger["transaction_id"]

    if transaction_id not in vendor_data[
        "transaction_id"
    ].values:

        results.append({
            "transaction_id": transaction_id,
            "vendor_amount": 0,
            "ledger_amount": ledger["amount"],
            "difference": -ledger["amount"],
            "status": "MISSING IN VENDOR"
        })


# ------------------------------------------------------------
# STEP 6: Create result DataFrame
# ------------------------------------------------------------

result_df = pd.DataFrame(results)


# ------------------------------------------------------------
# STEP 7: Display reconciliation results
# ------------------------------------------------------------

print("\n")
print("=" * 60)
print("           RECONCILIATION RESULTS")
print("=" * 60)

print(
    result_df.to_string(index=False)
)


# ------------------------------------------------------------
# STEP 8: Count statuses
# ------------------------------------------------------------

matched_count = len(
    result_df[
        result_df["status"] == "MATCHED"
    ]
)

amount_mismatch_count = len(
    result_df[
        result_df["status"] == "AMOUNT MISMATCH"
    ]
)

missing_ledger_count = len(
    result_df[
        result_df["status"] == "MISSING IN LEDGER"
    ]
)

missing_vendor_count = len(
    result_df[
        result_df["status"] == "MISSING IN VENDOR"
    ]
)


# ------------------------------------------------------------
# STEP 9: Display Summary
# ------------------------------------------------------------

print("\n")
print("=" * 60)
print("             RECONCILIATION SUMMARY")
print("=" * 60)

print(
    f"Vendor Statement Total : {vendor_total:,.2f}"
)

print(
    f"Internal Ledger Total  : {ledger_total:,.2f}"
)

print(
    f"Total Difference       : {difference:,.2f}"
)

print(
    f"Matched Transactions   : {matched_count}"
)

print(
    f"Amount Mismatches      : {amount_mismatch_count}"
)

print(
    f"Missing in Ledger      : {missing_ledger_count}"
)

print(
    f"Missing in Vendor      : {missing_vendor_count}"
)


# ------------------------------------------------------------
# STEP 10: Natural Language Explanation
# ------------------------------------------------------------

print("\n")
print("=" * 60)
print("             AI-STYLE EXPLANATION")
print("=" * 60)

if difference == 0 and amount_mismatch_count == 0:

    print(
        "The vendor statement and internal ledger "
        "are fully reconciled. No differences were found."
    )

else:

    print(
        "The reconciliation is not fully balanced."
    )

    print(
        f"A total difference of {difference:,.2f} "
        "was identified."
    )

    if amount_mismatch_count > 0:

        print(
            f"{amount_mismatch_count} transaction(s) "
            "have amount mismatches."
        )

    if missing_ledger_count > 0:

        print(
            f"{missing_ledger_count} transaction(s) "
            "are present in the vendor statement "
            "but missing from the internal ledger."
        )

    if missing_vendor_count > 0:

        print(
            f"{missing_vendor_count} transaction(s) "
            "are present in the internal ledger "
            "but missing from the vendor statement."
        )


# ------------------------------------------------------------
# STEP 11: Save result to CSV
# ------------------------------------------------------------

result_df.to_csv(
    "reconciliation_result.csv",
    index=False
)

print("\n")
print("=" * 60)
print(
    "Reconciliation result saved successfully!"
)
print(
    "File: reconciliation_result.csv"
)
print("=" * 60)