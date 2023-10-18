from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fastapi import Depends
from models.EmployeeModels import Employee

DATABASE_URL = "postgresql://employeeapi:restapi@localhost/postgres"


engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def db_get_employee(session: Depends(get_async_session()), id: str):
