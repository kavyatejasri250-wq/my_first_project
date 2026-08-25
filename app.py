import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Vendor Reconciliation Copilot",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Vendor Reconciliation Copilot")

st.write(
    "Upload a vendor statement and internal ledger "
    "to identify matched, mismatched and missing transactions."
)


# ============================================================
# 1. FILE UPLOAD
# ============================================================

col1, col2 = st.columns(2)

with col1:
    vendor_file = st.file_uploader(
        "Upload Vendor Statement",
        type=["csv"]
    )

with col2:
    ledger_file = st.file_uploader(
        "Upload Internal Ledger",
        type=["csv"]
    )


# ============================================================
# 2. NORMALIZATION
# ============================================================

def normalize_data(df):

    df = df.copy()

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Clean transaction ID
    df["transaction_id"] = (
        df["transaction_id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Clean description
    df["description"] = (
        df["description"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Convert date
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # Convert amount
    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    return df


# ============================================================
# 3. RECONCILIATION
# ============================================================

if vendor_file and ledger_file:

    vendor_data = pd.read_csv(vendor_file)
    ledger_data = pd.read_csv(ledger_file)

    # Normalize both files
    vendor_data = normalize_data(vendor_data)
    ledger_data = normalize_data(ledger_data)

    st.success("Both CSV files uploaded and normalized successfully!")

    if st.button("🔍 Reconcile Transactions"):

        results = []

        # ----------------------------------------------------
        # Match Vendor Transactions
        # ----------------------------------------------------

        for _, vendor in vendor_data.iterrows():

            transaction_id = vendor["transaction_id"]
            vendor_amount = vendor["amount"]

            match = ledger_data[
                ledger_data["transaction_id"]
                == transaction_id
            ]

            if match.empty:

                results.append({
                    "Transaction ID": transaction_id,
                    "Vendor Amount": vendor_amount,
                    "Ledger Amount": 0,
                    "Difference": vendor_amount,
                    "Status": "MISSING IN LEDGER"
                })

            else:

                ledger_amount = match.iloc[0]["amount"]

                difference = (
                    vendor_amount - ledger_amount
                )

                if difference == 0:
                    status = "MATCHED"
                else:
                    status = "AMOUNT MISMATCH"

                results.append({
                    "Transaction ID": transaction_id,
                    "Vendor Amount": vendor_amount,
                    "Ledger Amount": ledger_amount,
                    "Difference": difference,
                    "Status": status
                })


        # ----------------------------------------------------
        # Find Ledger-only Transactions
        # ----------------------------------------------------

        for _, ledger in ledger_data.iterrows():

            transaction_id = ledger["transaction_id"]

            if transaction_id not in vendor_data[
                "transaction_id"
            ].values:

                results.append({
                    "Transaction ID": transaction_id,
                    "Vendor Amount": 0,
                    "Ledger Amount": ledger["amount"],
                    "Difference": -ledger["amount"],
                    "Status": "MISSING IN VENDOR"
                })


        # ----------------------------------------------------
        # Result DataFrame
        # ----------------------------------------------------

        result_df = pd.DataFrame(results)


        # ====================================================
        # RUNNING BALANCE
        # ====================================================

        result_df["Running Balance"] = (
            result_df["Difference"].cumsum()
        )


        # ====================================================
        # TOTALS
        # ====================================================

        vendor_total = vendor_data["amount"].sum()

        ledger_total = ledger_data["amount"].sum()

        total_difference = (
            vendor_total - ledger_total
        )


        # ====================================================
        # STATUS COUNTS
        # ====================================================

        matched = len(
            result_df[
                result_df["Status"] == "MATCHED"
            ]
        )

        mismatched = len(
            result_df[
                result_df["Status"] == "AMOUNT MISMATCH"
            ]
        )

        missing_ledger = len(
            result_df[
                result_df["Status"]
                == "MISSING IN LEDGER"
            ]
        )

        missing_vendor = len(
            result_df[
                result_df["Status"]
                == "MISSING IN VENDOR"
            ]
        )


        # ====================================================
        # SUMMARY
        # ====================================================

        st.subheader("📊 Reconciliation Summary")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Matched",
            matched
        )

        c2.metric(
            "Amount Mismatch",
            mismatched
        )

        c3.metric(
            "Missing in Ledger",
            missing_ledger
        )

        c4.metric(
            "Missing in Vendor",
            missing_vendor
        )


        st.metric(
            "💰 Final Reconciliation Balance",
            f"{total_difference:,.2f}"
        )


        # ====================================================
        # RECONCILIATION TABLE
        # ====================================================

        st.subheader("📋 Reconciliation Results")

        st.dataframe(
            result_df,
            use_container_width=True
        )


        # ====================================================
        # RUNNING BALANCE
        # ====================================================

        st.subheader("💰 Running Balance")

        st.line_chart(
            result_df.set_index(
                "Transaction ID"
            )["Running Balance"]
        )


        # ====================================================
        # NATURAL LANGUAGE SUMMARY
        # ====================================================

        st.subheader("📝 Reconciliation Explanation")

        if (
            total_difference == 0
            and mismatched == 0
            and missing_ledger == 0
            and missing_vendor == 0
        ):

            st.success(
                "The vendor statement and internal ledger "
                "are fully reconciled. No discrepancies were found."
            )

        else:

            st.warning(
                f"The reconciliation has a total difference "
                f"of {total_difference:,.2f}."
            )

            if mismatched > 0:
                st.write(
                    f"• {mismatched} transaction(s) "
                    "have amount mismatches."
                )

            if missing_ledger > 0:
                st.write(
                    f"• {missing_ledger} transaction(s) "
                    "are present in the vendor statement "
                    "but missing from the internal ledger."
                )

            if missing_vendor > 0:
                st.write(
                    f"• {missing_vendor} transaction(s) "
                    "are present in the internal ledger "
                    "but missing from the vendor statement."
                )


        # ====================================================
        # DOWNLOAD REPORT
        # ====================================================

        csv_data = result_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇️ Download Reconciliation Report",
            data=csv_data,
            file_name="reconciliation_result.csv",
            mime="text/csv"
        )