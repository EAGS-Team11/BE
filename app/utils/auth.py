# app/utils/auth.py

from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "IniRahasiaJWT1234567890"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    # --- PERBAIKAN: TRUNCATE PASSWORD KE 72 BYTE ---
    # Konversi ke bytes dan potong hingga 72 byte (batas bcrypt)
    password_bytes = password.encode('utf-8')
    truncated_password = password_bytes[:72]
    
    return pwd_context.hash(truncated_password)

def verify_password(plain_password, hashed_password):
    # --- PERBAIKAN: TRUNCATE PASSWORD SAAT VERIFIKASI ---
    # Konversi ke bytes dan potong hingga 72 byte
    password_bytes = plain_password.encode('utf-8')
    truncated_password = password_bytes[:72]
    
    return pwd_context.verify(truncated_password, hashed_password)

def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)