# Tối Ưu Hiệu Suất MySQL - Cache & Transaction

## 1. Tổng Quan Kiến Trúc MySQL
Khi thực hiện các thao tác trên MySQL, dữ liệu sẽ đi qua nhiều lớp cache trước khi ghi xuống disk:
- **INSERT/UPDATE/DELETE**:
  1. Ghi vào **InnoDB Buffer Pool** (`innodb_buffer_pool_size`)
  2. Ghi vào **InnoDB Log Buffer** (`innodb_log_buffer_size`)
  3. Ghi vào **Binary Log Cache** (`binlog_cache_size`, nếu có replication)
  4. Cuối cùng mới flush xuống disk khi commit hoặc cache đầy.

- **SELECT**:
  1. MySQL kiểm tra **InnoDB Buffer Pool** trước.
  2. Nếu không có, MySQL đọc từ disk → lưu vào Buffer Pool để cache cho các truy vấn sau.

---
## 2. Các Loại Cache Quan Trọng Trong MySQL

| **Tham số**                   | **Mô tả** | **Giá trị mặc định** |
|--------------------------------|-----------|-----------------|
| `innodb_buffer_pool_size`       | Cache dữ liệu & index của InnoDB | 128M |
| `innodb_log_buffer_size`        | Cache transaction log | 16M |
| `binlog_cache_size`             | Cache binlog của transaction (Replication) | 32K |
| `query_cache_size`              | Cache kết quả truy vấn (MySQL < 8.0) | 1M |
| `table_open_cache`              | Cache số bảng mở cùng lúc | 2000 |
| `thread_cache_size`             | Cache thread kết nối để tái sử dụng | Tự động |
| `innodb_flush_log_at_trx_commit`| Cách ghi log của InnoDB | 1 (Flush ngay khi commit) |
| `max_binlog_cache_size`         | Kích thước tối đa của binlog cache | 4G |

---
## 3. Cách Thay Đổi Các Tham Số Cache

1. **Thay đổi tạm thời (áp dụng ngay nhưng mất khi restart MySQL):**
```sql
SET GLOBAL innodb_buffer_pool_size = 8G;
SET GLOBAL innodb_log_buffer_size = 128M;
SET GLOBAL binlog_cache_size = 16M;
innodb_buffer_pool_size = 8G
innodb_log_buffer_size = 128M
binlog_cache_size = 16M
```

2. **Thay đổi vĩnh viễn (giữ nguyên sau khi restart MySQL):**
- Sửa file cấu hình `/etc/mysql/my.cnf` hoặc `/etc/my.cnf`:
```ini
[mysqld]
innodb_buffer_pool_size = 8G
innodb_log_buffer_size = 128M
binlog_cache_size = 16M
```
- Restart MySQL để áp dụng:
```bash
sudo systemctl restart mysql
```

---
## 4. Kiểm Tra MySQL Có Bị Quá Tải Không?

✅ **Kiểm tra Log Buffer có bị đầy không (`innodb_log_buffer_size`)?**
```sql
SHOW GLOBAL STATUS LIKE 'innodb_log_waits';
```
➡️ Nếu `innodb_log_waits > 0`, Log Buffer quá nhỏ, cần tăng kích thước:
```sql
SET GLOBAL innodb_log_buffer_size = 256M;
```

✅ **Kiểm tra Buffer Pool có bị đầy không (`innodb_buffer_pool_size`)?**
```sql
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%';
```
📌 **Tính Cache Hit Rate:**
```sql
SELECT (1 - (Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests)) * 100 AS cache_hit_rate
FROM (SELECT VARIABLE_VALUE AS Innodb_buffer_pool_reads
      FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads') AS A,
     (SELECT VARIABLE_VALUE AS Innodb_buffer_pool_read_requests
      FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Innodb_buffer_pool_read_requests') AS B;
```
➡️ Nếu cache hit < 90%, MySQL đọc từ disk quá nhiều → Cần tăng Buffer Pool.
```sql
SET GLOBAL innodb_buffer_pool_size = 16G;
```

✅ **Kiểm tra Binlog Cache có bị đầy không (`binlog_cache_size`)?**
```sql
SHOW GLOBAL STATUS LIKE 'Binlog_cache_disk_use';
```
➡️ Nếu `Binlog_cache_disk_use > 0`, MySQL dùng file tạm trên disk thay vì RAM, cần tăng binlog cache:
```sql
SET GLOBAL binlog_cache_size = 32M;
```

---
## 5. Khi Nào MySQL Flush Xuống Disk?

- **Log Buffer (`innodb_log_buffer_size`)** được flush xuống disk khi:
  1. Transaction commit.
  2. Buffer đầy.
  3. Thời gian tự động flush (1 giây/lần).

- **Buffer Pool (`innodb_buffer_pool_size`)** được flush khi:
  1. Máy chủ cần RAM cho dữ liệu mới.
  2. MySQL tự động background flush.
  3. Server shutdown.

---
## 6. Tối Ưu Hệ Thống Khi Có Nhiều Transaction
➡️ Khi có nhiều transaction đồng thời, cần tăng các giá trị:
- **Tăng `innodb_log_buffer_size`** để tránh flush xuống disk quá sớm.
- **Tăng `innodb_buffer_pool_size`** để giữ nhiều dữ liệu hơn trong RAM.
- **Tăng `binlog_cache_size`** để tránh ghi binlog xuống disk.

🔥 **Tóm Tắt Cách Tối Ưu MySQL**
✅ Tăng cache hợp lý (`innodb_buffer_pool_size`, `innodb_log_buffer_size`, `binlog_cache_size`).
✅ Kiểm tra cache hit rate để đảm bảo MySQL đọc từ RAM thay vì disk.
✅ Tăng log buffer nếu có nhiều transaction lớn (`innodb_log_buffer_size`).
✅ Giảm ghi xuống disk bằng cách tối ưu rollback & commit hợp lý.

📌 **Lệnh kiểm tra hiệu suất:**
```sql
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_reads';
SHOW GLOBAL STATUS LIKE 'Innodb_log_waits';
SHOW GLOBAL STATUS LIKE 'Binlog_cache_disk_use';
SHOW GLOBAL STATUS LIKE 'innodb_log_fsyncs';
```
🚀 **Tối ưu đúng cách giúp MySQL chạy nhanh hơn & ổn định hơn!**

Server nhỏ (<50 connections): thread_cache_size = 8
Server vừa (50-200 connections): thread_cache_size = 16
Server lớn (>200 connections): thread_cache_size = 32 hoặc cao hơn

SHOW VARIABLES LIKE 'innodb_buffer_pool_size';
SHOW VARIABLES LIKE 'innodb_log_buffer_size';
SHOW VARIABLES LIKE 'binlog_cache_size';

SHOW VARIABLES LIKE 'thread_cache_size';

Yêu cầu (requests/s)	InnoDB Buffer Pool Cache (GB)	Query Cache (GB)	InnoDB Log Buffer (MB)	Binlog Cache (MB)	Tải CPU (%)
10	2	0.5	32	4	10
50	10	1	64	8	15
100	20	2	128	16	25
200	40	3	256	32	30
500	100	5	512	64	40
1000	200	10	1024	128	50
2000	400	15	2048	256	60


Yêu cầu (requests/s)	InnoDB Buffer Pool Cache (GB)	Query Cache (GB)	InnoDB Log Buffer (MB)	Binlog Cache (MB)	Tải CPU (%)	Lượng dữ liệu mỗi yêu cầu (KB)	Tổng dữ liệu yêu cầu mỗi giây (MB)
10	2	0.5	32	4	10	100	1
50	10	1	64	8	15	100	5
100	20	2	128	16	25	100	10
200	40	3	256	32	30	100	20
500	100	5	512	64	40	100	50
1000	200	10	1024	128	50	100	100
2000	400	15	2048	256	60	100	200