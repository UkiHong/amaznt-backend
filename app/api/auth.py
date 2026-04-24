"""
auth.py is for authentication related endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db_session
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import (
    create_access_token,
    get_current_active_user,
    get_current_user,
    hash_password,
    verify_password,
)
from sqlalchemy import select, or_
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/register-test")
def auth_check():
    return {"status": "ok"}


# Register endpoint for testing the registration request body, step 2 for testing the registration endpoint with DB interaction and password hashing
@router.post(
    "/register-test",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_test(
    user_data: UserCreate,
    db=Depends(get_db_session),
):

    # 1. Check for duplicates
    # SQL execution to check if the user already exists in db with the same username or email.
    result = await db.execute(
        select(User).where(
            or_(
                User.username == user_data.username,
                User.email == user_data.email,
            )
        )
    )

    # 2. If duplicates exist, raise error
    # Getting the first user from the result, or None if no users exist.
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    # 3. If not, hash the password
    # making a hashed password from the plain password received in the request body, to be stored in the DB.
    hashed_pw = hash_password(user_data.password)

    # 4. Create new user + save to DB
    # Creating a new User object with the data received in the request body and the hashed password, to be stored in the DB.
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        bio=user_data.bio,
        hashed_password=hashed_pw,
        role="user",
        is_active=True,
    )

    # 5. Get the latest value from DB and return it
    # Adding the new user to the DB session
    db.add(new_user)

    # Transaction commit → actually save to the DB
    await db.commit()

    # Refresh new_user to get the latest values
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db_session),
):
    result = await db.execute(select(User).where(User.email == form_data.username))

    existing_user = result.scalar_one_or_none()

    # If user with the email does not exist, or if the password is incorrect, raise error
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # If user exists, Verifying the hased password in the DB with the plain password received in the request body.
    if not verify_password(form_data.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # If the password is correct, Creating a JWT Token with the user's email as the subject.
    access_token = create_access_token(data={"sub": existing_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# Endpoint for the current user after verifying JWT token.
@router.get("/me", response_model=UserResponse)
async def read_me(current_user: User = Depends(get_current_active_user)):
    return current_user
