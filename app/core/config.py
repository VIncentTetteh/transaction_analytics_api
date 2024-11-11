from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL:str = os.getenv("DATABASE_URL")
    REDIS_URL: str = os.getenv("REDIS_URL")

    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD")

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")


settings = Settings()