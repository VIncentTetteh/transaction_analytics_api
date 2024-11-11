from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict
from datetime import date
from app.db.session import get_db
from app.services.analytics_service import AnalyticsService
from app.custom_exceptions.exceptions import (
    DatabaseErrorException,
    AnalyticsDataNotFoundException,
    AnalyticsComputationErrorException
)

router = APIRouter()

@router.get("/{user_id}/average_transaction_value", response_model=float)
async def get_average_transaction_value(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Retrieve the average transaction value for a specific user, converted from pesewas to GHC."""
    try:
        # Trigger cache refresh periodically
        background_tasks.add_task(AnalyticsService.refresh_cache_periodically, db, user_id)

        average_value = await AnalyticsService.get_average_transaction_value(db, user_id)
        return average_value
    except AnalyticsDataNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except AnalyticsComputationErrorException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)
    except DatabaseErrorException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)

@router.get("/{user_id}/highest_transaction_day", response_model=Dict[str, Optional[str]])
async def get_highest_transaction_day(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Retrieve the day with the highest number of transactions for a specific user."""
    try:
        # Trigger cache refresh periodically
        background_tasks.add_task(AnalyticsService.refresh_cache_periodically, db, user_id)

        highest_day = await AnalyticsService.get_highest_transaction_day(db, user_id)
        return {"highest_transaction_day": highest_day.isoformat() if highest_day else None}
    except AnalyticsDataNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except AnalyticsComputationErrorException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)
    except DatabaseErrorException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)

@router.get("/{user_id}/transaction_totals", response_model=Dict[str, float])
async def get_transaction_totals(
    user_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Retrieve the total value of debit and credit transactions for a specific user over an optional date range, converted from pesewas to GHC."""
    try:
        # Trigger cache refresh periodically
        background_tasks.add_task(AnalyticsService.refresh_cache_periodically, db, user_id)

        totals = await AnalyticsService.get_transaction_totals(db, user_id, start_date, end_date)
        return totals
    except AnalyticsDataNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except AnalyticsComputationErrorException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)
    except DatabaseErrorException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.detail)
