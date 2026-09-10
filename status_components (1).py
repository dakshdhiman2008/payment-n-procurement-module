"""
status_components.py
---------------------
Small, reusable UI components for showing procurement/payment status,
plus the (non-UI) amount calculation function.

Exposes:
    render_procurement_status(status: str) -> None
    render_payment_status(status: str) -> None
    calculate_procurement_amount(measured_weight_kg, quality_grade, crop) -> float

These are meant to be imported and dropped into ANY page (farmer page,
officer page, or a future page someone else builds) so status styling
stays consistent across the whole app.
"""

import streamlit as st
from config import get_rate

PROCUREMENT_STEPS = ["BOOKED", "ARRIVED", "WEIGHING", "PROCURED"]
PAYMENT_STEPS = ["PAYMENT_PROCESSING", "PAID"]

_PROCUREMENT_LABELS = {
    "BOOKED": "Booked",
    "ARRIVED": "Arrived",
    "WEIGHING": "Weighing",
    "PROCURED": "Completed",   # shown as COMPLETED per the spec's example
}

_PROCUREMENT_ICONS = {
    "BOOKED": "🔵",
    "ARRIVED": "🟡",
    "WEIGHING": "🟠",
    "PROCURED": "🟢",
}

_PAYMENT_LABELS = {
    "PAYMENT_PROCESSING": "Processing",
    "PAID": "Paid",
}

_PAYMENT_ICONS = {
    "PAYMENT_PROCESSING": "🟠",
    "PAID": "🟢",
}


def render_procurement_status(status: str) -> None:
    """
    Renders a one-line procurement status badge.
    Input: status (str) — one of BOOKED/ARRIVED/WEIGHING/PROCURED (or None)
    Returns: None (writes directly to the Streamlit page)
    """
    label = _PROCUREMENT_LABELS.get(status, status or "Unknown")
    icon = _PROCUREMENT_ICONS.get(status, "⚪")
    st.markdown(f"**Procurement:** {icon} {label.upper()}")


def render_payment_status(status: str) -> None:
    """
    Renders a one-line payment status badge.
    Input: status (str) — "PAYMENT_PROCESSING", "PAID", or None (not started)
    Returns: None (writes directly to the Streamlit page)
    """
    if status is None:
        st.markdown("**Payment:** ⚪ NOT STARTED")
        return
    label = _PAYMENT_LABELS.get(status, status)
    icon = _PAYMENT_ICONS.get(status, "⚪")
    st.markdown(f"**Payment:** {icon} {label.upper()}")


def calculate_procurement_amount(measured_weight_kg: float, quality_grade: str, crop: str) -> float:
    """
    Calculates procurement amount = measured_weight_kg * rate(crop, grade).

    The rate itself is never hardcoded here — it always comes from
    config.get_rate(), so all pricing-rule changes happen in config.py only.

    Inputs:
        measured_weight_kg (float)
        quality_grade (str): "A" / "B" / "C"
        crop (str): e.g. "wheat"
    Returns:
        float: amount in INR, rounded to 2 decimals. Returns 0.0 if
               weight or grade is missing (e.g. weighing not done yet).
    """
    if measured_weight_kg is None or quality_grade is None:
        return 0.0
    rate = get_rate(crop, quality_grade)
    return round(measured_weight_kg * rate, 2)
