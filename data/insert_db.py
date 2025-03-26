import random
import time
from faker import Faker
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Cấu hình Database URL
DATABASE_URL = "mysql+mysqlconnector://fast_api:km123456@localhost/database1"

# Tạo engine kết nối đồng bộ với connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # Số kết nối tối đa trong pool
    max_overflow=5,         # Số kết nối có thể mở thêm khi pool đầy
    pool_recycle=1800,      # Tự động đóng kết nối sau 30 phút
    pool_timeout=30,        # Timeout nếu lấy kết nối quá lâu
    echo=True
)

# Session Factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

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

def insert_user(session, username, email, password):
    """Chèn user nhưng kiểm tra trùng trước (đồng bộ)"""
    existing_user = session.query(User).filter((User.username == username) | (User.email == email)).first()
    
    if existing_user:
        print(f"User {username} đã tồn tại! Bỏ qua insert.")
        return  

    new_user = User(username=username, email=email, password=password)
    session.add(new_user)
    session.commit()
    print(f"Inserted: {username}")

def bulk_insert_users(n=1000):
    """Chạy insert đồng bộ với Connection Pool và nhiều session"""
    with SessionLocal() as session:
        for _ in range(n):
            insert_user(
                session=session,
                username=fake.user_name(),
                email=fake.email(),
                password=fake.password(length=12)
            )

def main():
    start = time.time()
    bulk_insert_users(1000)  # Tạo 1000 user giả
    print(f"Time: {time.time() - start} giây")

if __name__ == "__main__":
    main()
