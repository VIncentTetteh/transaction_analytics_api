# services/auth_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.core.security import security
from sqlalchemy.future import select
from fastapi import HTTPException, status
from pydantic import EmailStr
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, user_data):
        logger.info("Attempting to register user with email: %s", user_data.email)
        async with db as session:
            query = select(User).filter(User.email == user_data.email)
            result = await session.execute(query)
            existing_user = result.scalars().first()
            
            if existing_user:
                logger.warning("Registration failed: Email %s already registered.", user_data.email)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
            
            hashed_password = security.hash_password(user_data.password)
            hashed_full_name = security.encrypt(user_data.full_name)
            new_user = User(email=user_data.email, full_name=hashed_full_name, password=hashed_password)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            logger.info("Successfully registered new user with email: %s", user_data.email)
            return new_user

    @staticmethod
    async def login_user(db: AsyncSession, email: str, password: str):
        logger.info("User attempting to log in with email: %s", email)
        query = select(User).filter(User.email == email)
        result = await db.execute(query)
        user = result.scalars().first()

        if not user or not security.verify_password(password, user.password):
            logger.warning("Login failed for email: %s, invalid credentials.", email)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
        
        user.otp_code = security.generate_otp()
        logger.info("Generated OTP for user with email: %s", email)

        await db.commit()
        await db.refresh(user)
        
        return user.otp_code  

    @staticmethod
    async def verify_otp(db: AsyncSession, otp_data):
        logger.info("Verifying OTP for email: %s", otp_data.email)
        query = select(User).filter(User.email == otp_data.email)
        result = await db.execute(query)
        user = result.scalars().first()

        if not user or user.otp_code != otp_data.otp:
            logger.warning("OTP verification failed for email: %s", otp_data.email)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP.")
        
        token_data = {"sub": user.email, "user_id": str(user.id)}
        token = security.create_access_token(data=token_data)
        logger.info("OTP verified successfully for email: %s, access token generated.", otp_data.email)
        
        user.otp_code = None
        await db.commit()
        logger.info("Cleared OTP for user with email: %s after successful verification", otp_data.email)
        
        return token
