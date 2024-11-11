import asyncio
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from typing import Optional, Dict
from app.db.models import Transaction
from app.utils.cache import cache
from app.custom_exceptions.exceptions import (
    DatabaseErrorException,
    CacheErrorException,
    AnalyticsDataNotFoundException,
    AnalyticsComputationErrorException
)
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    CACHE_EXPIRY = 100

    @staticmethod
    async def get_average_transaction_value(db: AsyncSession, user_id: str) -> float:
        cache_key = f"average_transaction_value:{user_id}"
        logger.info("Calculating average transaction value for user_id: %s", user_id)

        try:
            # Check cache first
            cached_value = await cache.get_cache(cache_key)
            if cached_value is not None:
                logger.info("Cache hit for average transaction value, user_id: %s", user_id)
                return float(cached_value["value"]) / 100  # Convert to GHC if cached

            # Query for the average transaction amount
            result = await db.execute(
                select(func.avg(Transaction.transaction_amount)).where(Transaction.user_id == user_id)
            )
            average_value = result.scalar() or 0.0
            average_value /= 100  # Convert to GHC
            
            # Cache the result in pesewas
            await cache.set_cache(cache_key, {"value": int(average_value * 100)}, expire=AnalyticsService.CACHE_EXPIRY)
            logger.info("Cached average transaction value for user_id: %s", user_id)
            return average_value
        except Exception as e:
            logger.error("Error calculating average transaction value for user_id: %s, error: %s", user_id, str(e))
            raise AnalyticsComputationErrorException(detail=str(e))
    
    @staticmethod
    async def get_highest_transaction_day(db: AsyncSession, user_id: str) -> Optional[date]:
        cache_key = f"highest_transaction_day:{user_id}"
        logger.info("Finding highest transaction day for user_id: %s", user_id)

        try:
            # Check cache first
            cached_day = await cache.get_cache(cache_key)
            if cached_day is not None:
                logger.info("Cache hit for highest transaction day, user_id: %s", user_id)
                return datetime.fromisoformat(cached_day["day"]).date()
            
            # Query for the day with the highest transaction count
            result = await db.execute(
                select(
                    func.date_trunc('day', Transaction.transaction_date).label("day"),
                    func.count(Transaction.id).label("transaction_count")
                )
                .where(Transaction.user_id == user_id)
                .group_by("day")
                .order_by(func.count(Transaction.id).desc())
                .limit(1)
            )
            highest_transaction_day = result.first()
            
            if highest_transaction_day:
                day = highest_transaction_day.day
                await cache.set_cache(cache_key, {"day": day.isoformat()}, expire=AnalyticsService.CACHE_EXPIRY)
                logger.info("Cached highest transaction day for user_id: %s", user_id)
                return day.date()
            else:
                logger.warning("No transactions found for user_id: %s", user_id)
                raise AnalyticsDataNotFoundException(detail="No transactions found for the specified user")
        except AnalyticsDataNotFoundException:
            raise
        except Exception as e:
            logger.error("Error finding highest transaction day for user_id: %s, error: %s", user_id, str(e))
            raise AnalyticsComputationErrorException(detail=str(e))

    @staticmethod
    async def get_transaction_totals(db: AsyncSession, user_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, float]:
        cache_key = f"transaction_totals:{user_id}:{start_date}:{end_date}"
        logger.info("Calculating transaction totals for user_id: %s within dates %s - %s", user_id, start_date, end_date)

        try:
            # Check cache first
            cached_totals = await cache.get_cache(cache_key)
            if cached_totals is not None:
                logger.info("Cache hit for transaction totals, user_id: %s", user_id)
                return {k: v / 100 for k, v in cached_totals.items()}
            
            # Query totals for credit and debit transactions
            query = select(
                Transaction.transaction_type,
                func.sum(Transaction.transaction_amount).label("total_amount")
            ).where(Transaction.user_id == user_id)
            
            if start_date:
                query = query.where(Transaction.transaction_date >= datetime.combine(start_date, datetime.min.time()))
            if end_date:
                query = query.where(Transaction.transaction_date <= datetime.combine(end_date, datetime.max.time()))
                
            query = query.group_by(Transaction.transaction_type)
            result = await db.execute(query)
            
            totals = {"credit": 0.0, "debit": 0.0}
            rows = result.all()
            if not rows:
                logger.warning("No transactions found for user_id: %s within dates %s - %s", user_id, start_date, end_date)
                raise AnalyticsDataNotFoundException(detail="No transactions found for the specified user within the given period")
            
            for row in rows:
                ghc_value = (row.total_amount or 0) / 100  # Convert to GHC
                if row.transaction_type.value == "CREDIT":
                    totals["credit"] = ghc_value
                elif row.transaction_type.value == "DEBIT":
                    totals["debit"] = ghc_value
            
            await cache.set_cache(cache_key, {"credit": int(totals["credit"] * 100), "debit": int(totals["debit"] * 100)}, expire=AnalyticsService.CACHE_EXPIRY)
            logger.info("Cached transaction totals for user_id: %s", user_id)
            
            return totals
        except AnalyticsDataNotFoundException:
            raise
        except Exception as e:
            logger.error("Error calculating transaction totals for user_id: %s, error: %s", user_id, str(e))
            raise AnalyticsComputationErrorException(detail=str(e))

    @staticmethod
    async def refresh_cache_periodically(db: AsyncSession, user_id: str):
        logger.info("Starting periodic cache refresh for user_id: %s", user_id)
        while True:
            await AnalyticsService.get_average_transaction_value(db, user_id)
            await AnalyticsService.get_highest_transaction_day(db, user_id)
            await AnalyticsService.get_transaction_totals(db, user_id)
            logger.info("Refreshed analytics cache for user_id: %s", user_id)
            await asyncio.sleep(100) 
