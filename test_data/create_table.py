from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Index
import asyncio
from sqlalchemy import TIMESTAMP, text

# Cấu hình Database URL (cần chỉ định đúng tên database)
# DATABASE_URL = "mysql+asyncmy://thoang:km123456@mysql_container:3306/fastapi"
DATABASE_URL = "mysql+asyncmy://thoang:km123456@localhost:3310/fastapi"




# Tạo engine kết nối async
engine = create_async_engine(
    DATABASE_URL, 
    pool_size=10,           # Số lượng kết nối tối đa
    max_overflow=5,         # Số kết nối vượt quá pool_size (tạo tạm thời)
    pool_recycle=1800,      # Reset connection sau 30 phút
    pool_timeout=30,        # Timeout nếu không có kết nối khả dụng
    echo=True               # Log các truy vấn SQL
)

# Session Factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Khởi tạo Base
Base = declarative_base()

# Định nghĩa bảng
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False, server_default="")
    datetime = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    # __table_args__ = (Index("idx_username_email", "username", "email"),)

async def check_table_exists():
    async with engine.begin() as conn:
        result = await conn.execute(text("SHOW TABLES LIKE 'users';"))
        return result.scalar() is not None
# Function tạo bảng
async def create_tables():
    a= await check_table_exists()
    print(a)
    if a:
        print("Table already exists.")
        return
    else:
        print("Table does not exist. Creating...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Chạy tạo bảng
async def main():
    await create_tables()
    await engine.dispose()  

if __name__ == "__main__":
    asyncio.run(main())
