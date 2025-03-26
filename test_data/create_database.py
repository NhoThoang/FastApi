from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio

# Cấu hình Database URL (không chứa tên database)
DATABASE_URL = "mysql+asyncmy://thoang:km123456@172.21.0.2:3310"




# Tạo engine kết nối đến MySQL (không chỉ định database)
engine = create_async_engine(DATABASE_URL, echo=True)

async def create_database():
    async with engine.begin() as conn:
        # Kiểm tra database có tồn tại không
        result = await conn.execute(text("SHOW DATABASES LIKE 'flask';"))
        exists = result.scalar() is not None

        if not exists:
            print("Database does not exist. Creating...")
            await conn.execute(text("CREATE DATABASE flask CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
        else:
            print("Database already exists.")

async def main():
    await create_database()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
