from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")



engine = create_async_engine(
    DATABASE_URL, 
    pool_size=10,           # Số lượng kết nối tối đa
    max_overflow=5,         # Số kết nối vượt quá pool_size (tạo tạm thời)
    pool_recycle=1800,      # Reset connection sau 30 phút
    pool_timeout=30,        # Timeout nếu không có kết nối khả dụng
    echo=True               # Log các truy vấn SQL
    # isolation_level="AUTOCOMMIT" #KHÔNG sử dụng khi cần INSERT, UPDATE, DELETE vì nó sẽ commit ngay lập tức, không thể rollback.
)

# Session Factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False #không xóa session mặc đinh là true nó sẽ tự động query lại để trả cho client     
    # autoflush=False,   # Không tự động flush
    # autocommit=True    # Không tạo transaction không cần thiết
)
Base = declarative_base()
# async def get_db():
#     async with AsyncSessionLocal() as session:
#         try:
#             yield session
#             await session.commit()
#         except Exception:
#             await session.rollback()
#             raise

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

