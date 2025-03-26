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
    """Lấy Cache Hit Ratio và các cache variables từ MySQL InnoDB"""
    async with async_engine.connect() as conn:
        # Lấy các biến về bộ đệm và cache
        result = await conn.execute(text("SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%'"))
        buffer_pool_stats = {row[0]: int(row[1]) for row in result}
        # Tính Cache Hit Ratio
        if buffer_pool_stats.get("Innodb_buffer_pool_read_requests", 0) > 0:
            cache_hit_ratio = (1 - (buffer_pool_stats["Innodb_buffer_pool_reads"] / 
                                     buffer_pool_stats["Innodb_buffer_pool_read_requests"])) * 100
        else:
            cache_hit_ratio = 0
        return cache_hit_ratio  # Trả về tỷ lệ cache hit

async def get_cache_variables(variable):
    """Lấy giá trị của biến cache từ MySQL"""
    async with async_engine.connect() as conn:
        result = await conn.execute(text(f"SHOW VARIABLES LIKE '{variable}'"))
        var_value = result.fetchone()
        if var_value:
            return var_value[1]  # Trả về giá trị của biến cache

# Hàm chính để tạo task và in kết quả
async def main():
    # Tạo task bất đồng bộ
    # task_cache_hit_ratio = asyncio.create_task(get_cache_hit_ratio())
    # # Chờ tất cả các task hoàn thành và lấy kết quả
    # cache_hit_ratio = await task_cache_hit_ratio  # Nhận tỷ lệ cache hit
    # print(f"🔥 Cache Hit Ratio: {cache_hit_ratio:.2f}%")  # In kết quả Cache Hit Ratio

    # Tạo các task cho các biến cache
    variables = ["innodb_buffer_pool_size", "innodb_log_buffer_size", "binlog_cache_size", "thread_cache_size"]
    task_cache_variables = [asyncio.create_task(get_cache_variables(variable)) for variable in variables]


    
    # Chờ và in các kết quả của các biến cache
    cache_variables = await asyncio.gather(*task_cache_variables)
    for variable, value in zip(variables, cache_variables):
        print(f"{variable}: {value}")  # In giá trị của các biến cache

# Chạy hàm chính
asyncio.run(main())
