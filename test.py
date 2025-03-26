from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String
from pydantic import BaseModel

app = FastAPI()

# Database Models
class Base(DeclarativeBase):
    pass

class InfoUserDB(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True)

# Pydantic Schema
class InfoUser(BaseModel):
    username: str

    class Config:
        from_attributes = True  # Chuyển từ ORM sang Pydantic model

# Dependency lấy session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Query lấy thông tin user từ database
async def information_user(db: AsyncSession, username: str) -> InfoUser | None:
    result = await db.execute(select(InfoUserDB).filter(InfoUserDB.username == username).limit(1))
    user = result.scalars().first()
    return InfoUser.model_validate(user) if user else None

@app.post("/information/", response_model=InfoUser)
async def information(user: InfoUser, db: AsyncSession = Depends(get_db)):
    user_info = await information_user(db, user.username)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return user_info
