from dotenv import load_dotenv
import os

# Load biến môi trường từ .env
load_dotenv()

# Đọc DATABASE_URL từ môi trường
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"Database URL: {DATABASE_URL}")  # Kiểm tra giá trị
