import asyncio
import random
import time
from faker import Faker
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text

# Cấu hình Database URL
DATABASE_URL = "mysql+asyncmy://thoang:km123456@localhost:3310/fastapi"

# Tạo engine kết nối async
engine = create_async_engine(
    DATABASE_URL, 
    pool_size=20,         
    max_overflow=10,      
    pool_recycle=1800,    
    pool_timeout=30,      
    echo=False            
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
semaphore = asyncio.Semaphore(50) 

async def insert_user(username, email, password):
    """Chèn user nhưng kiểm tra trùng trước"""
    async with semaphore:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where((User.username == username) | (User.email == email)).limit(1)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                return  

            new_user = User(username=username, email=email, password=password)
            session.add(new_user)
            await session.commit()

async def bulk_insert_users(n=1000):
    """Chạy nhiều kết nối insert song song với giới hạn tối đa"""
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
    await bulk_insert_users(10000)  
    # await engine.dispose()  # Giải phóng tài nguyên của engine

    print(f"Time: {time.time() - start:.2f} giây (Async)")

if __name__ == "__main__":
    asyncio.run(main())



# # code đồng bộ 
# import time
# from faker import Faker
# from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text
# from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

# # Cấu hình Database URL
# DATABASE_URL = "mysql+mysqlconnector://thoang:km123456@localhost:3310/fastapi"

# # Tạo engine kết nối đồng bộ
# engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10)

# # Session Factory
# SessionLocal = scoped_session(sessionmaker(bind=engine))

# # Khởi tạo Base
# Base = declarative_base()

# # Định nghĩa bảng User
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, autoincrement=True, index=True)
#     username = Column(String(50), unique=True, nullable=False)
#     email = Column(String(100), unique=True, nullable=False)
#     password = Column(String(255), nullable=False, server_default="")
#     datetime = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

# # Khởi tạo Faker
# fake = Faker()

# def insert_user(session, username, email, password):
#     """Chèn user nhưng kiểm tra trùng trước (đồng bộ)"""
#     existing_user = session.query(User).filter((User.username == username) | (User.email == email)).first()
#     if existing_user:
#         return  
#     new_user = User(username=username, email=email, password=password)
#     session.add(new_user)
#     session.commit()

# def bulk_insert_users(n=1000):
#     """Chạy vòng lặp để chèn user (đồng bộ)"""
#     session = SessionLocal()
#     for _ in range(n):
#         insert_user(session, fake.user_name(), fake.email(), fake.password(length=12))
#     session.close()

# def main():
#     start = time.time()
#     bulk_insert_users(10000)
#     print(f"Time: {time.time() - start:.2f} giây (Đồng bộ)")

# if __name__ == "__main__":
#     main()
