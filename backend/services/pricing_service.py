import math


def estimate_powerwash(sq_ft: float, rate_per_sqft_cents: int = 15) -> int:
    """Estimate powerwashing cost based on square footage.

    Args:
        sq_ft: Area to be washed in square feet.
        rate_per_sqft_cents: Price per square foot in cents (default $0.15/sq ft).

    Returns:
        Estimated price in cents, rounded up to the nearest cent.

    Raises:
        ValueError: If sq_ft is not a positive number.
    """
    if sq_ft <= 0:
        raise ValueError("sq_ft must be a positive number")

    return math.ceil(sq_ft * rate_per_sqft_cents)


# --- Gutter Cleaning Estimator ---
# TODO: determine pricing method (e.g. linear ft of gutter, number of downspouts,
#       flat rate by home size tier, or time-and-materials). Add implementation once decided.
def estimate_gutter_cleaning() -> int:
    raise NotImplementedError("Gutter cleaning estimator not yet implemented")
