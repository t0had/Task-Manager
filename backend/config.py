import os
from fastapi import security
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = "postgresql://" + POSTGRES_USER + ":" + POSTGRES_PASSWORD + "@db:5432" + "/" + POSTGRES_DB

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
get_auth_bearer = security.OAuth2PasswordBearer(tokenUrl="login")