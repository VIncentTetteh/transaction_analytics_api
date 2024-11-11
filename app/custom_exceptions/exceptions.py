from fastapi import HTTPException, status

class UserNotFoundException(HTTPException):
    def __init__(self, detail="User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class TransactionNotFoundException(HTTPException):
    def __init__(self, detail="Transaction not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class InvalidTransactionAmountException(HTTPException):
    def __init__(self, detail="Transaction amount must be positive"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class DatabaseErrorException(HTTPException):
    def __init__(self, detail="An error occurred with the database"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class CacheErrorException(HTTPException):
    def __init__(self, detail="An error occurred with the cache"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class AnalyticsDataNotFoundException(HTTPException):
    def __init__(self, detail="Analytics data not found for the specified user"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class AnalyticsComputationErrorException(HTTPException):
    def __init__(self, detail="Error occurred while computing analytics data"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
