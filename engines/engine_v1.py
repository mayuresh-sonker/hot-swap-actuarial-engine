# Actuarial Model v1.0 — Baseline Rating
# Deployed: 2024-01 | Author: Actuarial Team

ENGINE_VERSION = "1.0.0"
ENGINE_NAME = "Baseline Auto Rating Model"

def calculate_premium(age: int, vehicle_value: float,
                        zip_code: str, coverage: str) -> dict:
    """
    Simple actuarial rating engine.
    Returns premium breakdown.
    """
    base_rate = 500.0

    # Age factor (young/old drivers cost more)
    age_factor = 1.0
    if age < 25: age_factor = 1.8
    elif age > 70: age_factor = 1.4
    elif age < 35: age_factor = 1.2

    # Vehicle value factor
    value_factor = min(1.0 + (vehicle_value / 100000), 3.0)

    # Coverage factor
    coverage_map = {"liability": 1.0, "collision": 1.5,
                    "comprehensive": 1.8}
    cov_factor = coverage_map.get(coverage, 1.0)

    annual_premium = base_rate * age_factor * value_factor * cov_factor

    return {
        "engine_version": ENGINE_VERSION,
        "engine_name": ENGINE_NAME,
        "annual_premium": round(annual_premium, 2),
        "monthly_premium": round(annual_premium / 12, 2),
        "factors": {
            "base": base_rate,
            "age": age_factor,
            "vehicle": round(value_factor, 3),
            "coverage": cov_factor
        }
    }
