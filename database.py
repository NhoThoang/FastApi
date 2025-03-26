from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+asyncmy://thoang:km123456@localhost:3310/fastapi"



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

Base = declarative_base()

# Hàm để lấy session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# def get_db():
#     db = async_session()
#     try:
#         yield db
#     finally:
#         db.close()

