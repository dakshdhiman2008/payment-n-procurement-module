"""
officer_payment_overview.py
-----------------------------
Officer-facing page: see all bookings, enter measured weight + quality
grade, calculate procurement amount, and move records through the flow:

    BOOKED -> ARRIVED -> WEIGHING -> PROCURED -> PAYMENT PROCESSING -> PAID

Exposes:
    render_officer_payment_overview() -> None

Depends on:
    db_interface.fetch_bookings / fetch_procurements / fetch_payments
    db_interface.update_procurement / update_payment
    status_components.calculate_procurement_amount

===========================================================================
SIMULATED PAYMENT — READ THIS
===========================================================================
There is NO real bank integration, NO real payment gateway, and NO real
money movement anywhere in this file. "Marking as PAID" simply updates
the `payments.status` column to the string "PAID". This is intentional
and required for the hackathon prototype. A real payment gateway (Razorpay,
UPI, NEFT, etc.) would replace the body of `_simulate_mark_as_paid()` only.
===========================================================================
"""

import streamlit as st
import pandas as pd
from db_interface import (
    fetch_bookings, fetch_procurements, fetch_payments,
    update_procurement, update_payment,
)
from status_components import calculate_procurement_amount


def _build_overview_table() -> pd.DataFrame:
    """Joins bookings + procurements + payments (by token) into one table."""
    bookings = fetch_bookings()
    procurements = {p["token"]: p for p in fetch_procurements()}
    payments = {p["token"]: p for p in fetch_payments()}

    rows = []
    for b in bookings:
        token = b["token"]
        proc = procurements.get(token, {})
        pay = payments.get(token, {})
        rows.append({
            "Token": token,
            "Farmer": b.get("farmer_name", "—"),
            "Crop": b.get("crop", "—"),
            "Booked (kg)": b.get("booked_qty_kg"),
            "Weight (kg)": proc.get("measured_weight_kg"),
            "Grade": proc.get("quality_grade"),
            "Procurement Status": proc.get("status") or b.get("status"),
            "Payment Amount": pay.get("amount"),
            "Payment Status": pay.get("status") or "—",
        })
    return pd.DataFrame(rows)


def _simulate_mark_as_paid(token: str, amount: float) -> None:
    """
    SIMULATED payment action. No real gateway is called.
    Replace this function's body if/when a real payment gateway is wired up.
    """
    update_payment(token, amount, "PAID")


def render_officer_payment_overview() -> None:
    """
    Renders the officer's procurement + payment overview page.
    Input: none
    Returns: None (renders directly to the Streamlit page)
    """
    st.subheader("🧑‍💼 Officer: Procurement & Payment Overview")

    df = _build_overview_table()
    st.dataframe(df, use_container_width=True)

    if df.empty:
        st.info("No bookings found.")
        return

    st.markdown("---")
    st.markdown("### Step 1 — Enter Weighing Details")

    tokens = df["Token"].tolist()
    selected_token = st.selectbox("Select Token", tokens)
    row = df[df["Token"] == selected_token].iloc[0]

    col1, col2 = st.columns(2)
    with col1:
        measured_weight = st.number_input(
            "Measured Weight (kg)",
            min_value=0.0,
            value=float(row["Weight (kg)"]) if row["Weight (kg)"] else 0.0,
        )
    with col2:
        existing_grade = row["Grade"] if row["Grade"] in ["A", "B", "C"] else "A"
        quality_grade = st.selectbox("Quality Grade", ["A", "B", "C"], index=["A", "B", "C"].index(existing_grade))

    if st.button("Calculate & Mark as PROCURED"):
        amount = calculate_procurement_amount(measured_weight, quality_grade, row["Crop"])
        update_procurement(selected_token, measured_weight, quality_grade, "PROCURED")
        update_payment(selected_token, amount, "PAYMENT_PROCESSING")
        st.success(f"Procurement completed for {selected_token}. Calculated amount: ₹{amount:,.0f}")
        st.rerun()

    st.markdown("---")
    st.markdown("### Step 2 — Payment Action (Simulated)")
    st.caption("⚠️ SIMULATED — no real bank or payment gateway is called here.")

    if row["Payment Status"] == "PAYMENT_PROCESSING":
        st.write(f"Amount ready for payout: **₹{row['Payment Amount']:,.0f}**")
        if st.button(f"Simulate: Mark {selected_token} as PAID"):
            _simulate_mark_as_paid(selected_token, row["Payment Amount"])
            st.success(f"{selected_token} marked as PAID (simulated).")
            st.rerun()
    else:
        st.write(f"Current payment status: **{row['Payment Status']}**")
