import logging
from sqlalchemy.orm import Session
from app.db.models import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.custom_exceptions.exceptions import TransactionNotFoundException, InvalidTransactionAmountException
from app.utils.cache import cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

CACHE_TTL = 300 


def analytics_cache_keys(user_id: str):
    return {
        "average_transaction": f"average_transaction_value:{user_id}",
        "highest_transaction_day": f"highest_transaction_day:{user_id}",
        "transaction_totals": f"transaction_totals:{user_id}"
    }

async def create_transaction(db: AsyncSession, transaction_data: TransactionCreate) -> TransactionResponse:
    logger.info("Creating a new transaction for user_id: %s", transaction_data.user_id)

    if transaction_data.transaction_amount <= 0:
        logger.error("Invalid transaction amount: %s", transaction_data.transaction_amount)
        raise InvalidTransactionAmountException()

    transaction_data_dict = transaction_data.dict()
    if transaction_data_dict.get("transaction_date"):
        transaction_data_dict["transaction_date"] = transaction_data_dict["transaction_date"].replace(tzinfo=None)

    transaction = Transaction(**transaction_data_dict)
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    transaction_response = TransactionResponse.from_orm(transaction)

    await cache.set_cache(f"transaction:{transaction.id}", transaction_response.dict(), expire=CACHE_TTL)
    logger.info("Transaction created and cached with id: %s", transaction.id)

    user_cache_keys = analytics_cache_keys(transaction_data.user_id)
    await cache.clear_cache(user_cache_keys["average_transaction"])
    await cache.clear_cache(user_cache_keys["highest_transaction_day"])
    await cache.clear_cache(user_cache_keys["transaction_totals"])
    logger.info("Invalidated analytics cache for user_id: %s", transaction_data.user_id)

    return transaction_response

async def update_transaction(db: AsyncSession, transaction_id: int, transaction_data: TransactionUpdate) -> TransactionResponse:
    logger.info("Updating transaction with id: %s", transaction_id)

    stmt = select(Transaction).filter(Transaction.id == transaction_id)
    result = await db.execute(stmt)
    transaction = result.scalars().first()

    if not transaction:
        logger.warning("Transaction with id %s not found", transaction_id)
        raise TransactionNotFoundException()

    for key, value in transaction_data.dict(exclude_unset=True).items():
        setattr(transaction, key, value)

    await db.commit()
    await db.refresh(transaction)
    transaction_response = TransactionResponse.from_orm(transaction)

    await cache.set_cache(f"transaction:{transaction.id}", transaction_response.dict(), expire=CACHE_TTL)
    logger.info("Transaction with id %s updated and cache refreshed", transaction.id)

    user_cache_keys = analytics_cache_keys(transaction.user_id)
    await cache.clear_cache(user_cache_keys["average_transaction"])
    await cache.clear_cache(user_cache_keys["highest_transaction_day"])
    await cache.clear_cache(user_cache_keys["transaction_totals"])
    logger.info("Invalidated analytics cache for user_id: %s", transaction.user_id)

    return transaction_response

async def get_transaction(db: AsyncSession, transaction_id: str) -> TransactionResponse:
    logger.info("Retrieving transaction with id: %s", transaction_id)

    cached_transaction = await cache.get_cache(f"transaction:{transaction_id}")
    if cached_transaction:
        logger.info("Transaction with id %s retrieved from cache", transaction_id)
        return TransactionResponse(**cached_transaction)

    stmt = select(Transaction).filter(Transaction.id == transaction_id)
    result = await db.execute(stmt)
    transaction = result.scalars().first()

    if not transaction:
        logger.warning("Transaction with id %s not found", transaction_id)
        raise TransactionNotFoundException()

    transaction_response = TransactionResponse.from_orm(transaction)
    await cache.set_cache(f"transaction:{transaction_id}", transaction_response.dict(), expire=CACHE_TTL)
    logger.info("Transaction with id %s retrieved from database and cached", transaction_id)

    return transaction_response

async def delete_transaction(db: AsyncSession, transaction_id: int) -> None:
    logger.info("Deleting transaction with id: %s", transaction_id)

    stmt = select(Transaction).filter(Transaction.id == transaction_id)
    result = await db.execute(stmt)
    transaction = result.scalars().first()

    if not transaction:
        logger.warning("Transaction with id %s not found", transaction_id)
        raise TransactionNotFoundException()

    await db.delete(transaction)
    await db.commit()
    await cache.clear_cache(f"transaction:{transaction_id}")
    logger.info("Transaction with id %s deleted and cache cleared", transaction_id)

    if transaction.user_id:
        user_cache_keys = analytics_cache_keys(transaction.user_id)
        await cache.clear_cache(user_cache_keys["average_transaction"])
        await cache.clear_cache(user_cache_keys["highest_transaction_day"])
        await cache.clear_cache(user_cache_keys["transaction_totals"])
        logger.info("Invalidated analytics cache for user_id: %s", transaction.user_id)
