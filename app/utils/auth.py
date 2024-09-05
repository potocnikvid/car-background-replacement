# app/utils/auth.py

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from app.services.supabase import supabase
# Load environment variables
load_dotenv()

# Load Supabase JWT secret from environment
from app.core.config import SUPABASE_JWT_SECRET, EXPECTED_AUDIENCE, JWT_ALGORITHM
print(EXPECTED_AUDIENCE)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_jwt(token: str = Depends(oauth2_scheme)):
    """Verify Supabase JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:

        # Decode the JWT token
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=[JWT_ALGORITHM], audience=EXPECTED_AUDIENCE)
    
        # Extract the subject (user_id)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Check for token expiration
        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(tz=timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise credentials_exception
