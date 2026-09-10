"""
config.py
---------
Configuration for the Procurement & Payment module.

WHY THIS FILE EXISTS:
The hackathon requirement says "use a configurable rate variable rather
than hardcoding business rules throughout the application." This file is
that single source of truth. If the rate/grade rules change tomorrow,
this is the ONLY file that needs to change.

INTEGRATION NOTE:
For the prototype, rates live in a plain Python dict below. In the real
system these would come from a Supabase `rates` table. To upgrade later,
replace the body of get_rate() with a Supabase query and keep the same
function signature — nothing else in this module needs to change.
"""

# crop -> grade -> rate per kg (INR)
PROCUREMENT_RATES = {
    "wheat": {"A": 21.0, "B": 19.0, "C": 17.0},
    "rice":  {"A": 25.0, "B": 22.0, "C": 20.0},
    "maize": {"A": 18.0, "B": 16.0, "C": 14.0},
    "default": {"A": 20.0, "B": 18.0, "C": 16.0},  # fallback for unknown crops
}


def get_rate(crop: str, grade: str) -> float:
    """
    Look up the rate (INR per kg) for a given crop and quality grade.

    Inputs:
        crop  (str): e.g. "wheat", "rice", "maize" (case-insensitive)
        grade (str): "A", "B", or "C" (case-insensitive)

    Returns:
        float: rate in INR per kg. Falls back to the "default" crop
               table, and then to grade "B", if an exact match isn't found.
    """
    crop_key = (crop or "").strip().lower()
    grade_key = (grade or "").strip().upper()
    crop_rates = PROCUREMENT_RATES.get(crop_key, PROCUREMENT_RATES["default"])
    return crop_rates.get(grade_key, crop_rates.get("B"))
