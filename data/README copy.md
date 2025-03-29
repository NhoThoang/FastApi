# Cấu hình Tối ưu MySQL

## So sánh Cấu hình Mặc định và Tối ưu

| Tham số                      | Mặc định (MySQL) | Cấu hình Tối ưu | Ảnh hưởng |
|------------------------------|-----------------|----------------|----------|
| innodb_buffer_pool_size       | ~128MB         | 16G            | Tăng đáng kể bộ nhớ cache dữ liệu, giảm I/O đĩa. |
| innodb_buffer_pool_instances  | 1              | 8              | Cải thiện hiệu suất khi nhiều luồng truy cập. |
| innodb_log_file_size          | 128MB          | 1G             | Tăng kích thước log để tránh ghi log quá thường xuyên. |
| innodb_log_buffer_size        | 16MB           | 256M           | Giảm số lần ghi log xuống đĩa, tối ưu cho giao dịch lớn. |
| innodb_flush_log_at_trx_commit| 1              | 1 (giữ nguyên) | Đảm bảo an toàn dữ liệu nhưng có thể chậm hơn so với 2. |
| innodb_flush_method           | fsync          | O_DIRECT       | Tránh cache của hệ điều hành, tối ưu ghi trực tiếp vào đĩa. |
| innodb_read_io_threads        | 4              | 8              | Tăng số luồng đọc song song để xử lý truy vấn nhanh hơn. |
| innodb_write_io_threads       | 4              | 8              | Tăng luồng ghi, giảm tắc nghẽn khi ghi dữ liệu. |
| innodb_io_capacity            | 200            | 1000           | Tăng giới hạn IOPS để tận dụng SSD hoặc RAID tốt hơn. |
| query_cache_size              | 0 (đã loại bỏ) | 0              | Không ảnh hưởng vì MySQL 8.x không còn dùng query cache. |
| tmp_table_size                | 16MB           | 512M           | Giảm tạo bảng tạm trên đĩa khi SELECT dữ liệu lớn. |
| max_heap_table_size           | 16MB           | 512M           | Tăng bộ nhớ tối đa cho bảng HEAP (bảng bộ nhớ). |
| read_buffer_size              | 128KB          | 2M             | Tăng tốc độ đọc tuần tự khi không có chỉ mục. |
| read_rnd_buffer_size          | 256KB          | 4M             | Giúp đọc dữ liệu nhanh hơn khi có ORDER BY. |
| join_buffer_size              | 256KB          | 8M             | Tăng hiệu suất JOIN khi thiếu chỉ mục. |
| max_connections               | 151            | 500            | Hỗ trợ nhiều kết nối đồng thời hơn. |
| thread_cache_size             | 9              | 64             | Giảm chi phí tạo luồng mới, cải thiện hiệu suất. |
| table_open_cache              | 2000           | 20000          | Giảm thời gian mở bảng khi có nhiều bảng. |
| open_files_limit              | 5000           | 50000          | Tăng giới hạn file mở, tránh lỗi "Too many open files". |

## Ghi chú
- Các tối ưu này dựa trên hệ thống có RAM đủ lớn (ví dụ: 32GB+) và sử dụng SSD.
- Điều chỉnh `innodb_buffer_pool_size` dựa trên bộ nhớ có sẵn để tránh tình trạng swap.
- `innodb_log_file_size` nên được tối ưu theo tải công việc và thời gian phục hồi.
- Đảm bảo `open_files_limit` phù hợp với cấu hình của hệ điều hành để tránh giới hạn.

### Áp dụng Cấu hình
Để áp dụng các thiết lập này, hãy cập nhật tệp cấu hình MySQL (`my.cnf` hoặc `my.ini`):

```ini
[mysqld]
innodb_buffer_pool_size=16G
innodb_buffer_pool_instances=8
innodb_log_file_size=1G
innodb_log_buffer_size=256M
innodb_flush_log_at_trx_commit=1
innodb_flush_method=O_DIRECT
innodb_read_io_threads=8
innodb_write_io_threads=8
innodb_io_capacity=1000
tmp_table_size=512M
max_heap_table_size=512M
read_buffer_size=2M
read_rnd_buffer_size=4M
join_buffer_size=8M
max_connections=500
thread_cache_size=64
table_open_cache=20000
open_files_limit=50000
```

Khởi động lại MySQL sau khi thay đổi:
```sh
systemctl restart mysql
```