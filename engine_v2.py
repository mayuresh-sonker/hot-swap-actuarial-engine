# Actuarial Model v2.0 — Post-Hurricane CAT Adjustment
# Emergency deploy: 2024-09 | Triggered: Hurricane Milton

ENGINE_VERSION = "2.0.0"
ENGINE_NAME = "CAT-Adjusted Florida Model"

# Florida coastal ZIP codes — elevated risk
HIGH_RISK_ZIPS = {"33101", "33109", "34102", "32801"}

def calculate_premium(age: int, vehicle_value: float,
                        zip_code: str, coverage: str) -> dict:
    """
    CAT-adjusted model with geographic surcharges.
    Replaces v1 after catastrophe event.
    """
    base_rate = 650.0  # Increased base due to CAT losses

    age_factor = 1.0
    if age < 25: age_factor = 2.0   # Tightened
    elif age > 70: age_factor = 1.6
    elif age < 35: age_factor = 1.3

    value_factor = min(1.0 + (vehicle_value / 80000), 4.0)

    coverage_map = {"liability": 1.1, "collision": 1.7,
                    "comprehensive": 2.2}
    cov_factor = coverage_map.get(coverage, 1.1)

    # NEW: Geographic CAT surcharge
    geo_factor = 1.45 if zip_code in HIGH_RISK_ZIPS else 1.0

    annual_premium = base_rate * age_factor * value_factor * cov_factor * geo_factor

    return {
        "engine_version": ENGINE_VERSION,
        "engine_name": ENGINE_NAME,
        "annual_premium": round(annual_premium, 2),
        "monthly_premium": round(annual_premium / 12, 2),
        "cat_surcharge_applied": zip_code in HIGH_RISK_ZIPS,
        "factors": {
            "base": base_rate,
            "age": age_factor,
            "vehicle": round(value_factor, 3),
            "coverage": cov_factor,
            "geographic_cat": geo_factor
        }
    }
