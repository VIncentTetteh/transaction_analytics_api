from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import UserRegister, UserLogin, OTPVerify, Token
from app.services.auth_service import AuthService
from pydantic import EmailStr

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    user = await AuthService.register_user(db, user_data)
    return {"message": "User registered successfully", "user_id": user.id}

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user and generate OTP."""
    otp = await AuthService.login_user(db, user_data.email, user_data.password)
    return {"message": "OTP sent for verification", "otp": otp}

@router.post("/verify-otp", response_model=Token)
async def verify_otp(otp_data: OTPVerify, db: AsyncSession = Depends(get_db)):
    """Verify OTP and issue JWT token upon successful verification."""
    token = await AuthService.verify_otp(db, otp_data)
    return {"access_token": token, "token_type": "bearer"}
