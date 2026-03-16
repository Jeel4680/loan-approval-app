from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

# Secret key and settings from .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Password encryption context — uses bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─────────────────────────────────────────
# PASSWORD FUNCTIONS
# ─────────────────────────────────────────

def hash_password(password: str) -> str:
    """Encrypt a plain text password — bcrypt max is 72 chars"""
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if a plain password matches the encrypted one"""
    return pwd_context.verify(plain_password[:72], hashed_password)

# ─────────────────────────────────────────
# JWT TOKEN FUNCTIONS
# ─────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """Create a JWT token that expires after set minutes"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify a JWT token and return its data"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
