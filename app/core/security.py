from cryptography.fernet import Fernet
from app.core.config import settings
import base64
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import random
from typing import Optional, Tuple
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

class Security:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
    def __init__(self):
        # Password hashing setup
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Fernet encryption key
        # Ensure the encryption key is in the correct format
        key = settings.ENCRYPTION_KEY
        if not key:
            raise ValueError("ENCRYPTION_KEY is not set in the environment.")
        self.fernet = Fernet(key)

    def encrypt(self, plain_text: str) -> str:
        """Encrypts a plain text string."""
        return self.fernet.encrypt(plain_text.encode()).decode()

    def decrypt(self, cipher_text: str) -> str:
        """Decrypts an encrypted string."""
        return self.fernet.decrypt(cipher_text.encode()).decode()

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    # JWT handling
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_token(self,token: str):
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            # Decode the token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            if email is None or user_id is None:
                raise credentials_exception
            return {"sub": email, "user_id": user_id}
        except JWTError:
            raise credentials_exception

    # Dependency to get the current user from the token
    async def get_current_user(self,token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        # Verify and decode the token
        token_data = verify_token(token) 
        user = await db.execute(select(User).filter(User.email == token_data["sub"]))
        user = user.scalars().first()
        
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        decrypted_full_name = security.decrypt(user.full_name)
        user.full_name = decrypted_full_name
        return user

    # OTP handling
    def generate_otp(self) -> Tuple[str, datetime]:
        """Generates an OTP and its expiration time."""
        otp = str(random.randint(100000, 999999))
        # expiration = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        return otp

    def verify_otp(self, provided_otp: str, stored_otp: str, expiration: datetime) -> bool:
        """Verifies the provided OTP with expiration check."""
        is_valid = (provided_otp == stored_otp) and (datetime.utcnow() < expiration)
        return is_valid

security = Security()
