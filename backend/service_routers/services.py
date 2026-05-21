from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import EstimateRequest, EstimateResponse
from services.pricing_service import estimate_powerwash
from model_crud.business_info_crud import increment_total_estimates

router = APIRouter(prefix="/services", tags=["Services"])


@router.post("/estimate", response_model=EstimateResponse, status_code=status.HTTP_200_OK)
async def get_estimate_endpoint(req: EstimateRequest, db: AsyncSession = Depends(get_db)):
    """Calculate a price estimate and increment the business estimate counter."""

    if req.job_type == "pwash":
        if req.sq_ft is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="sq_ft is required for power washing estimates",
            )
        price_cents = estimate_powerwash(req.sq_ft)

    elif req.job_type == "gutter_cleaning":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Gutter cleaning estimator is not yet implemented",
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown job type: '{req.job_type}'",
        )

    await increment_total_estimates(db)

    address = f"{req.street_number} {req.street_name}, {req.city}, {req.state} {req.zip_code}"

    return EstimateResponse(
        address=address,
        job_type=req.job_type,
        estimated_price_cents=price_cents,
        estimated_price_display=f"${price_cents / 100:,.2f}",
    )
