from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.custom_exceptions.exceptions import (
    UserNotFoundException,
    TransactionNotFoundException,
    InvalidTransactionAmountException,
    DatabaseErrorException,
    CacheErrorException,
    AnalyticsDataNotFoundException,
    AnalyticsComputationErrorException,
)


async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

async def transaction_not_found_handler(request: Request, exc: TransactionNotFoundException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

async def invalid_transaction_amount_handler(request: Request, exc: InvalidTransactionAmountException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

async def database_error_handler(request: Request, exc: DatabaseErrorException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

async def cache_error_handler(request: Request, exc: CacheErrorException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

async def analytics_data_not_found_handler(request: Request, exc: AnalyticsDataNotFoundException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

async def analytics_computation_error_handler(request: Request, exc: AnalyticsComputationErrorException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )
