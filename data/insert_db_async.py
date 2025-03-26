import random
import time
import asyncio
from faker import Faker
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

from sqlalchemy import Column, Integer, String, TIMESTAMP, text

# Cấu hình Database URL
# DATABASE_URL = "mysql+asyncmy://flask:km%4022071994@192.168.5.11/database1"
DATABASE_URL = "mysql+asyncmy://flask:km%4022071994@192.168.5.11:3307/flask"


# Tạo engine kết nối async
engine = create_async_engine(
    DATABASE_URL, 
    pool_size=10,           
    max_overflow=5,         
    pool_recycle=1800,      
    pool_timeout=30,        
    echo=True               
)

# Session Factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Khởi tạo Base
Base = declarative_base()

# Định nghĩa bảng User
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False, server_default="")
    datetime = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

# Khởi tạo Faker
fake = Faker()

async def insert_user(username, email, password):
    """Chèn user nhưng kiểm tra trùng trước"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
                select(User).where((User.username == username) | (User.email == email)).limit(1)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"User {username} đã tồn tại! Bỏ qua insert.")
            return  

        new_user = User(username=username, email=email, password=password)
        session.add(new_user)
        await session.commit()
        print(f"Inserted: {username}")

async def bulk_insert_users(n=1000):
    """Chạy nhiều kết nối insert song song với dữ liệu giả"""
    tasks = [
        insert_user(
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(length=12)
        )
        for _ in range(n)
    ]
    await asyncio.gather(*tasks)  

async def main():
    start = time.time()
    await bulk_insert_users(1000)  # Tạo 1000 user giả
    print(f"Time: {time.time() - start} giây")
    await asyncio.sleep(1)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
