# Tối ưu Hiệu suất MySQL và FastAPI

## Cấu hình Tối ưu MySQL

### So sánh Cấu hình Mặc định và Tối ưu

| Tham số                      | Mặc định (MySQL) | Cấu hình Tối ưu | Ảnh hưởng |
|------------------------------|-----------------|----------------|----------|
| innodb_buffer_pool_size       | ~128MB         | 1G             | Lưu cache nhiều dữ liệu hơn, giảm I/O đĩa. |
| innodb_buffer_pool_instances  | 1              | 2              | Cải thiện hiệu suất khi nhiều luồng truy cập. |
| innodb_log_file_size          | 128MB          | 256M           | Giữ log đủ lớn để tránh ghi log quá thường xuyên. |
| innodb_log_buffer_size        | 16MB           | 64M            | Giảm số lần ghi log xuống đĩa, tối ưu cho giao dịch vừa. |
| innodb_flush_log_at_trx_commit| 1              | 1 (giữ nguyên) | Đảm bảo an toàn dữ liệu nhưng có thể chậm hơn so với 2. |
| innodb_flush_method           | fsync          | O_DIRECT       | Tránh cache của hệ điều hành, tối ưu ghi trực tiếp vào đĩa. |
| innodb_read_io_threads        | 4              | 4              | Tăng số luồng đọc song song để xử lý truy vấn nhanh hơn. |
| innodb_write_io_threads       | 4              | 4              | Tăng luồng ghi, giảm tắc nghẽn khi ghi dữ liệu. |
| innodb_io_capacity            | 200            | 500            | Tăng giới hạn IOPS để tận dụng SSD hoặc RAID tốt hơn. |
| tmp_table_size                | 16MB           | 128M           | Giảm tạo bảng tạm trên đĩa khi SELECT dữ liệu vừa. |
| max_heap_table_size           | 16MB           | 128M           | Tăng bộ nhớ tối đa cho bảng HEAP (bảng bộ nhớ). |
| read_buffer_size              | 128KB          | 512K           | Tăng tốc độ đọc tuần tự khi không có chỉ mục. |
| read_rnd_buffer_size          | 256KB          | 1M             | Giúp đọc dữ liệu nhanh hơn khi có ORDER BY. |
| join_buffer_size              | 256KB          | 2M             | Tăng hiệu suất JOIN khi thiếu chỉ mục. |
| max_connections               | 151            | 200            | Hỗ trợ nhiều kết nối đồng thời hơn. |
| thread_cache_size             | 9              | 32             | Giảm chi phí tạo luồng mới, cải thiện hiệu suất. |
| table_open_cache              | 2000           | 5000           | Giảm thời gian mở bảng khi có nhiều bảng. |
| open_files_limit              | 5000           | 10000          | Tăng giới hạn file mở, tránh lỗi "Too many open files". |

### Áp dụng Cấu hình

Chỉnh sửa tệp cấu hình MySQL (`my.cnf` hoặc `my.ini`):

```ini
[mysqld]
innodb_buffer_pool_size=1G
innodb_buffer_pool_instances=2
innodb_log_file_size=256M
innodb_log_buffer_size=64M
innodb_flush_log_at_trx_commit=1
innodb_flush_method=O_DIRECT
innodb_read_io_threads=4
innodb_write_io_threads=4
innodb_io_capacity=500
tmp_table_size=128M
max_heap_table_size=128M
read_buffer_size=512K
read_rnd_buffer_size=1M
join_buffer_size=2M
max_connections=200
thread_cache_size=32
table_open_cache=5000
open_files_limit=10000
```

Khởi động lại MySQL để áp dụng thay đổi:
```sh
systemctl restart mysql
```

---

## FastAPI - Hiệu suất và Quản lý Kết Nối MySQL

FastAPI là một framework web mạnh mẽ hỗ trợ bất đồng bộ (async), giúp tối ưu hiệu suất khi làm việc với MySQL.

### 1. Hiệu Suất Cao
- FastAPI được xây dựng trên ASGI, hỗ trợ async giúp xử lý hàng ngàn request mỗi giây.
- Hiệu suất gần bằng Node.js và Go, nhanh hơn Flask và Django.

### 2. Hỗ Trợ AsyncIO và Event Loop
- Sử dụng `async` và `await` để tối ưu xử lý I/O.
- Khi gặp tác vụ truy vấn database, FastAPI trả quyền điều khiển cho event loop, giúp xử lý nhiều request cùng lúc.

### 3. Quản Lý Kết Nối MySQL Bằng Connection Pool
- Dùng **connection pool** thay vì tạo kết nối mới mỗi request.
- Giảm tải MySQL, tránh lỗi "Too many connections" bằng cách giới hạn số kết nối tối đa.

### Cấu Hình MySQL Connection Pool với FastAPI
Sử dụng `aiomysql` để tạo connection pool bất đồng bộ:

```python
from fastapi import FastAPI, Depends
import aiomysql

app = FastAPI()

async def get_db_pool():
    pool = await aiomysql.create_pool(
        host='localhost',
        port=3306,
        user='root',
        password='password',
        db='mydatabase',
        minsize=5,  # Số kết nối tối thiểu trong pool
        maxsize=20  # Giới hạn kết nối tối đa
    )
    return pool

@app.get("/users")
async def get_users():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM users")
            users = await cur.fetchall()
    return {"users": users}
```

### Lợi Ích Khi Dùng Connection Pool
✅ **Giảm độ trễ (latency):** Không cần mở kết nối mới mỗi request.  
✅ **Tối ưu tài nguyên:** Tránh quá tải database, giảm lỗi kết nối.  
✅ **Tăng khả năng chịu tải:** Xử lý nhiều request mà không làm MySQL bị nghẽn.  

### Tổng Kết
FastAPI giúp tối ưu hiệu suất hệ thống web nhờ kiến trúc bất đồng bộ. Sử dụng connection pool giúp giảm tải MySQL, cải thiện tốc độ truy vấn và tăng khả năng mở rộng hệ thống.

