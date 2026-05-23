import math


def estimate_powerwash(sq_ft: float, rate_per_sqft_cents: int = 35 #POWER WASH PRICE ADJUSTMENT
                       ) -> int:
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



def estimate_gutter_cleaning(
    perimeter_ft: float,
    num_floors: int,
    rate_per_linear_ft_cents: int = 150, #GUTTER CLEANING PRICE ADJUSTMENT
) -> int:
    """Estimate gutter cleaning cost from building perimeter and number of floors.

    Args:
        perimeter_ft: Building perimeter in linear feet (derived from satellite footprint).
        num_floors: Number of stories on the home.
        rate_per_linear_ft_cents: Price per linear foot of gutter in cents (default $0.75/ft).

    Returns:
        Estimated price in cents, rounded up to the nearest cent.

    Raises:
        ValueError: If perimeter_ft or num_floors is invalid.
    """
    if perimeter_ft <= 0:
        raise ValueError("perimeter_ft must be a positive number")
    if num_floors < 1:
        raise ValueError("num_floors must be at least 1")

    linear_ft = perimeter_ft * num_floors
    return math.ceil(linear_ft * rate_per_linear_ft_cents)
