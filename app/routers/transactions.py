from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.services.transaction_service import create_transaction, get_transaction, update_transaction, delete_transaction
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
async def create_transaction_route(transaction_data: TransactionCreate, db: Session = Depends(get_db)):
    new_transaction = await create_transaction(db, transaction_data)
    return new_transaction

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_route(transaction_id: str, db: Session = Depends(get_db)):
    transaction = await get_transaction(db, transaction_id)
    return transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction_route(
    transaction_id: str,
    transaction_data: TransactionUpdate,
    db: AsyncSession = Depends(get_db)
):

    return await update_transaction(db, transaction_id, transaction_data)

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction_route(
    transaction_id: str,
    db: AsyncSession = Depends(get_db)
):

    await delete_transaction(db, transaction_id)
    return None
