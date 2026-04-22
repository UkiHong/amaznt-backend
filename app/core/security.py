from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from sqlalchemy import select
from app.core.config import settings

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.database import get_db_session
from app.models.user import User


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Dependency function to get the current user from the JWT token.
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db_session),
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.email == token))

    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise credentials_exception

    return existing_user


# Password hashing
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# Password verification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    # Creating a copy of the original payload to avoid modifying it directly.
    to_encode = data.copy()

    # access token will be expired after the '30'(access_token_expire_minutes) mins.
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    # adding the expiration time (exp) to the JWT payload
    to_encode.update({"exp": expire})

    # Creating a JWT token by encoding the payload.
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    return encoded_jwt
