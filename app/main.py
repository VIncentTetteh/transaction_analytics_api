# main.py

from fastapi import FastAPI
from app.db.models import Base
from app.db.session import engine
from app.routers import transactions, analytics, auth
from app.custom_exceptions.exceptions import (
    UserNotFoundException,
    TransactionNotFoundException,
    InvalidTransactionAmountException,
    DatabaseErrorException,
    CacheErrorException,
    AnalyticsDataNotFoundException,
    AnalyticsComputationErrorException
)

from app.custom_exceptions.exception_handlers import (
    user_not_found_handler,
    transaction_not_found_handler,
    invalid_transaction_amount_handler,
    database_error_handler,
    cache_error_handler,
    analytics_data_not_found_handler,
    analytics_computation_error_handler,
    global_exception_handler
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FidoAPI", version="1.0.0", description="Fido Transaction and Analytics API")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def on_shutdown():
    await engine.dispose()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# Register global exception handlers
app.add_exception_handler(UserNotFoundException, user_not_found_handler)
app.add_exception_handler(TransactionNotFoundException, transaction_not_found_handler)
app.add_exception_handler(InvalidTransactionAmountException, invalid_transaction_amount_handler)
app.add_exception_handler(DatabaseErrorException, database_error_handler)
app.add_exception_handler(CacheErrorException, cache_error_handler)
app.add_exception_handler(AnalyticsDataNotFoundException, analytics_data_not_found_handler)
app.add_exception_handler(AnalyticsComputationErrorException, analytics_computation_error_handler)
app.add_exception_handler(Exception, global_exception_handler)
