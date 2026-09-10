"""
farmer_tracking_page.py
------------------------
Farmer-facing page: enter a token, see procurement + payment status.

Exposes:
    render_farmer_tracking_page(token: str = None) -> None

Depends on:
    db_interface.fetch_bookings / fetch_procurements / fetch_payments
    status_components.render_procurement_status / render_payment_status
"""

import streamlit as st
from db_interface import fetch_bookings, fetch_procurements, fetch_payments
from status_components import render_procurement_status, render_payment_status


def _get_records_for_token(token: str):
    """Looks up the matching booking/procurement/payment rows for a token."""
    booking = next((b for b in fetch_bookings() if b["token"] == token), None)
    procurement = next((p for p in fetch_procurements() if p["token"] == token), None)
    payment = next((p for p in fetch_payments() if p["token"] == token), None)
    return booking, procurement, payment


def render_farmer_tracking_page(token: str = None) -> None:
    """
    Renders the farmer tracking page.

    Input:
        token (str, optional): if the Integration Lead already knows the
            logged-in farmer's token (e.g. from a login/session system),
            pass it in directly and the text box is skipped. Otherwise
            leave it as None and the farmer types it in.
    Returns: None (renders directly to the Streamlit page)
    """
    st.subheader("🌾 Track Your Procurement")

    if token is None:
        token = st.text_input("Enter your Token Number", placeholder="e.g. MND-042")

    if not token:
        st.info("Enter a token number to see your status.")
        return

    booking, procurement, payment = _get_records_for_token(token)

    if booking is None:
        st.error(f"No booking found for token '{token}'.")
        return

    st.markdown(f"### Token: {booking['token']}")
    st.write(f"**Crop:** {str(booking.get('crop', '—')).capitalize()}")
    st.write(f"**Booked Quantity:** {booking.get('booked_qty_kg', '—')} kg")

    weight = procurement.get("measured_weight_kg") if procurement else None
    st.write(f"**Actual Weight:** {weight if weight is not None else '—'} kg")

    procurement_status = (procurement.get("status") if procurement else None) or booking.get("status")
    render_procurement_status(procurement_status)

    amount = payment.get("amount") if payment else None
    if amount:
        st.write(f"**Payment Amount:** ₹{amount:,.0f}")
    else:
        st.write("**Payment Amount:** —")

    payment_status = payment.get("status") if payment else None
    render_payment_status(payment_status)
