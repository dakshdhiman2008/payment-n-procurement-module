"""
db_interface.py
----------------
Thin data-access layer for this module. This is the ONLY file in this
module that talks to the database — every other file goes through the
functions defined here.

INTEGRATION NOTE FOR THE INTEGRATION LEAD:
This module expects a `database.py` to already exist in the main project,
exposing a ready-to-use Supabase client, e.g.:

    # database.py (owned by Integration Lead / backend teammate)
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

If `database.py` is not importable yet (e.g. during standalone
development), this file automatically falls back to in-memory sample
data so the module still runs and can be demoed. Once `database.py`
exists and is on the Python path, no code changes are needed here —
the import will succeed and USING_REAL_DB becomes True automatically.

Tables assumed to already exist (per project spec — NOT created here):
    - bookings
    - procurements
    - payments

Expected columns this module reads/writes (align with whoever owns the
schema; rename in this file only if actual column names differ):
    bookings:     token, farmer_name, crop, booked_qty_kg, status
    procurements: token, measured_weight_kg, quality_grade, status
    payments:     token, amount, status
"""

try:
    from database import supabase  # provided by Integration Lead
    USING_REAL_DB = True
except ImportError:
    supabase = None
    USING_REAL_DB = False


# ---------------------------------------------------------------------
# Sample data — used ONLY when database.py is not available yet.
# Matches the example in the spec: MND-042, wheat, 540kg, grade A -> ₹11,340
# ---------------------------------------------------------------------
SAMPLE_BOOKINGS = [
    {"token": "MND-042", "farmer_name": "Ramesh Patil", "crop": "wheat", "booked_qty_kg": 550, "status": "PROCURED"},
    {"token": "MND-043", "farmer_name": "Sita Devi",    "crop": "rice",  "booked_qty_kg": 300, "status": "WEIGHING"},
    {"token": "MND-044", "farmer_name": "Anil Kumar",   "crop": "maize", "booked_qty_kg": 420, "status": "BOOKED"},
]

SAMPLE_PROCUREMENTS = [
    {"token": "MND-042", "measured_weight_kg": 540, "quality_grade": "A", "status": "PROCURED"},
    {"token": "MND-043", "measured_weight_kg": None, "quality_grade": None, "status": "WEIGHING"},
    {"token": "MND-044", "measured_weight_kg": None, "quality_grade": None, "status": "BOOKED"},
]

SAMPLE_PAYMENTS = [
    {"token": "MND-042", "amount": 11340.0, "status": "PAYMENT_PROCESSING"},
    {"token": "MND-043", "amount": None, "status": None},
    {"token": "MND-044", "amount": None, "status": None},
]


def fetch_bookings():
    """
    Returns: list[dict] — all booking records.
    Real implementation: supabase.table("bookings").select("*").execute().data
    """
    if USING_REAL_DB:
        return supabase.table("bookings").select("*").execute().data
    return SAMPLE_BOOKINGS


def fetch_procurements():
    """
    Returns: list[dict] — all procurement records.
    Real implementation: supabase.table("procurements").select("*").execute().data
    """
    if USING_REAL_DB:
        return supabase.table("procurements").select("*").execute().data
    return SAMPLE_PROCUREMENTS


def fetch_payments():
    """
    Returns: list[dict] — all payment records.
    Real implementation: supabase.table("payments").select("*").execute().data
    """
    if USING_REAL_DB:
        return supabase.table("payments").select("*").execute().data
    return SAMPLE_PAYMENTS


def update_procurement(token: str, measured_weight_kg: float, quality_grade: str, status: str):
    """
    Update (or create, in sample mode) a procurement record.

    Inputs:
        token (str), measured_weight_kg (float), quality_grade (str "A"/"B"/"C"),
        status (str, one of BOOKED/ARRIVED/WEIGHING/PROCURED)
    Returns: None
    Real implementation:
        supabase.table("procurements").update({...}).eq("token", token).execute()
    """
    if USING_REAL_DB:
        supabase.table("procurements").update({
            "measured_weight_kg": measured_weight_kg,
            "quality_grade": quality_grade,
            "status": status,
        }).eq("token", token).execute()
        return

    for row in SAMPLE_PROCUREMENTS:
        if row["token"] == token:
            row.update({
                "measured_weight_kg": measured_weight_kg,
                "quality_grade": quality_grade,
                "status": status,
            })
            return
    SAMPLE_PROCUREMENTS.append({
        "token": token,
        "measured_weight_kg": measured_weight_kg,
        "quality_grade": quality_grade,
        "status": status,
    })


def update_payment(token: str, amount: float, status: str):
    """
    Update (or create, in sample mode) a payment record.

    Inputs:
        token (str), amount (float), status (str, "PAYMENT_PROCESSING" or "PAID")
    Returns: None
    Real implementation:
        supabase.table("payments").update({...}).eq("token", token).execute()
    """
    if USING_REAL_DB:
        supabase.table("payments").update({
            "amount": amount,
            "status": status,
        }).eq("token", token).execute()
        return

    for row in SAMPLE_PAYMENTS:
        if row["token"] == token:
            row.update({"amount": amount, "status": status})
            return
    SAMPLE_PAYMENTS.append({"token": token, "amount": amount, "status": status})
