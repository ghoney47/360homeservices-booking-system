from fastapi import APIRouter, HTTPException, Request, status
from schemas import EstimateRequest, EstimateResponse
from services.pricing_service import estimate_powerwash, estimate_gutter_cleaning
from services.footprint_service import get_building_perimeter_ft
from limiter import limiter

router = APIRouter(prefix="/services", tags=["Services"])


@router.post("/estimate", response_model=EstimateResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_estimate_endpoint(request: Request, req: EstimateRequest):
    """Calculate a price estimate."""

    address = f"{req.street_number} {req.street_name}, {req.city}, {req.state} {req.zip_code}"

    if req.job_type == "pwash":
        if req.sq_ft is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="sq_ft is required for power washing estimates",
            )
        price_cents = estimate_powerwash(req.sq_ft)

    elif req.job_type == "gutter_cleaning":
        if req.num_floors is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="num_floors is required for gutter cleaning estimates",
            )
        try:
            perimeter_ft = await get_building_perimeter_ft(address)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            )
        price_cents = estimate_gutter_cleaning(perimeter_ft, req.num_floors)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown job type: '{req.job_type}'",
        )

    # Sheets deployment — estimate counter skipped (DB_MODE=sheets, no database).
    # await increment_total_estimates(db)

    return EstimateResponse(
        address=address,
        job_type=req.job_type,
        estimated_price_cents=price_cents,
        estimated_price_display=f"${price_cents / 100:,.2f}",
    )
