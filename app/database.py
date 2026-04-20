import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from collections.abc import AsyncGenerator

# 1. .env 파일 읽기
# .env 안에 있는 DATABASE_URL 값을 파이썬에서 읽을 수 있게 해줍니다.
load_dotenv()

# 2. DB 연결 주소 가져오기
# postgresql+asyncpg://postgres:postgres@localhost:5432/amaznt
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL is not set in the .env file.")

# 3. SQLAlchemy async engine 만들기
# engine은 "DB와 연결해주는 큰 연결 관리자"라고 생각하면 됩니다.
database_engine = create_async_engine(
    database_url,
    echo=True,  # 개발 중에는 실행되는 SQL을 터미널에 보여줌
)

# 4. 세션 공장 만들기
# sessionmaker는 "세션 찍어내는 공장"입니다.
# 요청이 들어올 때마다 세션 하나씩 만들어서 쓰게 됩니다.
async_session_factory = async_sessionmaker(
    bind=database_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 5. 모든 SQLAlchemy 모델이 상속할 Base
# 나중에 User 모델 만들 때:
# class User(Base):
#     ...
# 이런 식으로 쓸 겁니다.
Base = declarative_base()


# 6. FastAPI에서 사용할 DB 세션 의존성
# API 함수에서 Depends(get_db_session) 형태로 사용합니다.
# 요청 하나당 세션 하나를 열고, 끝나면 자동으로 닫습니다.
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
