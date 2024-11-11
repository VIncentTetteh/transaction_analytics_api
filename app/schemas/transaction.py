from pydantic import BaseModel, conint, validator
from uuid import UUID
from enum import Enum
from datetime import datetime
from typing import Literal, Optional,Any
from uuid import uuid4

class TransactionTypeEnum(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

class TransactionBase(BaseModel):
    user_id: str
    transaction_amount: conint(gt=0)  # Stored in pesewas for precision
    transaction_type: TransactionTypeEnum
    transaction_date: datetime

class TransactionCreate(TransactionBase):
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class TransactionUpdate(BaseModel):
    transaction_amount: Optional[conint(gt=0)] = None
    transaction_type: Optional[TransactionTypeEnum] = None
    transaction_date: Optional[datetime] = None

class TransactionResponse(BaseModel):
    id: str
    user_id: str
    transaction_amount: int
    transaction_date: datetime
    transaction_type: TransactionTypeEnum
    created_at: datetime
    updated_at: datetime

    # Validator to convert UUID to string
    @validator('id', 'user_id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
    
    class Config:
        orm_mode = True
        from_attributes = True
