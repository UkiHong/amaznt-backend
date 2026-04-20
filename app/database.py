import os


from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

# reading .env file to get environment variables.
load_dotenv()

# Bring DATABASE_URL from environment variable, and raise error if not set
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL is not set in the .env file.")

# SQLAlchemy async engine creation, connecting database.
database_engine = create_async_engine(
    database_url,
    echo=True,  # showing SQL queries in the console for debugging, can be turned off in production
)

# sessionmaker is a "factory for creating sessions". Each request will get its own session from this factory.
async_session_factory = async_sessionmaker(
    bind=database_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base is a base class for all SQLAlchemy models.
Base = declarative_base()


# Dependency function to provide a database session for FastAPI endpoints, ensuring proper opening and closing of sessions per request.
# Using Depends(get_db_session) in API functions allows each request to have its own session that is automatically closed after the request is processed.
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
