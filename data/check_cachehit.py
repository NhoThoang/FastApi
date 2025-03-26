import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Cấu hình Async MySQL (asyncmy)
DATABASE_URL = "mysql+asyncmy://flask:km%4022071994@192.168.5.11:3307/flask"

# Tạo engine async
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Tạo session async
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_cache_hit_ratio():
    """Lấy Cache Hit Ratio từ MySQL InnoDB"""
    async with async_engine.connect() as conn:
        result = await conn.execute(text("SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%'"))
        buffer_pool_stats = {row[0]: int(row[1]) for row in result}
    if buffer_pool_stats["Innodb_buffer_pool_read_requests"] > 0:
        cache_hit_ratio = (
            1 - (buffer_pool_stats["Innodb_buffer_pool_reads"] / buffer_pool_stats["Innodb_buffer_pool_read_requests"])
        ) * 100
    else:
        cache_hit_ratio = 0

    print(f"🔥 Cache Hit Ratio: {cache_hit_ratio:.2f}%")

# Chạy function async
asyncio.run(get_cache_hit_ratio())
