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


# Password hashing
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# Password verification
# Used for /login endpoint to verify user's plain password with the hashed one.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# Creating JWT access token for authenticated users.
# Used for /login endpoint if password is correct.
def create_access_token(data: dict) -> str:
    # Creating a copy of the original payload to avoid modifying it directly.
    to_encode = data.copy()

    # access token will be expired after the '30'(access_token_expire_minutes) mins.
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    # adding the expiration time (exp) to the JWT payload ("to_encode").
    to_encode.update({"exp": expire})

    # Creating a JWT token by encoding the payload.
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Dependency function to get the current user from the JWT token.
# Used for /me endpoint.
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db_session),
):

    # Raising a HTTP error for invalid token or decoding failures.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Why decoding is needed: to verify the encoded token is valid and matched with DB.
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

    # Check if the user with the email from the token exists in DB
    result = await db.execute(select(User).where(User.email == email))

    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise credentials_exception

    return existing_user


# Checking if the current user(the existing user from "get_current_user") is active
# Used for /me endpoint to ensure only active users can access their info.
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user
