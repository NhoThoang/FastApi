Tiêu chí	MySQL	MongoDB
Kiến trúc lưu trữ	Dựa trên bảng, hàng, cột (RDBMS - SQL)	Dựa trên document JSON (NoSQL)
Cache chính	innodb_buffer_pool_size, query_cache_size	WiredTiger Cache (wiredTigerCacheSizeGB)
Cache truy vấn	query_cache_size (bị loại bỏ từ MySQL 8.0)	MongoDB không có cache truy vấn mặc định
Ghi dữ liệu	Ghi vào InnoDB Buffer Pool, rồi flush xuống disk	Ghi vào Journal, rồi flush xuống disk
Flush log	innodb_log_buffer_size, innodb_flush_log_at_trx_commit	WiredTiger journal, có thể bật/tắt
Tối ưu transaction	autocommit, innodb_log_buffer_size	Không hỗ trợ transaction mạnh như MySQL
Chỉ mục (Index)	B-Tree, Hash Index	B-Tree Index, Geospatial, TTL Index
Replication	Binlog-based replication	Replication tự động (Replica Set)
Sharding	Hỗ trợ nhưng phức tạp	Tích hợp sẵn (Sharded Cluster)
Tăng tốc SELECT	Tối ưu chỉ mục (EXPLAIN, INDEX)	Tối ưu index (explain(), compound index)
Tăng tốc INSERT/UPDATE	Batch INSERT, innodb_flush_log_at_trx_commit=2	Insert nhiều document 1 lần, WriteConcern thấp hơn
Tăng tốc DELETE	DELETE FROM table WHERE ... + Vacuum	TTL Index, remove() nhanh hơn MySQL
Ghi log	binlog_cache_size, innodb_log_file_size	oplog.rs (cơ chế giống binlog nhưng NoSQL)
Lệnh kiểm tra hiệu suất	SHOW GLOBAL STATUS, SHOW VARIABLES	db.serverStatus(), db.stats(), db.currentOp()

🔥 Tóm Tắt Tối Ưu Hiệu Suất MongoDB
✅ Tăng cache bằng cách thay đổi WiredTiger Cache

js
Copy
Edit
db.adminCommand({ setParameter: 1, wiredTigerCacheSizeGB: 4 });
✅ Tạo Index phù hợp cho truy vấn nhanh hơn

js
Copy
Edit
db.collection.createIndex({ field1: 1, field2: -1 });
✅ Bật sharding nếu dữ liệu lớn

js
Copy
Edit
sh.enableSharding("myDatabase");
sh.shardCollection("myDatabase.myCollection", { shardKey: 1 });
✅ Giảm ghi xuống disk bằng cách tắt journal nếu không cần thiết

yaml
Copy
Edit
storage:
  journal:
    enabled: false
✅ Kiểm tra hiệu suất hệ thống

js
Copy
Edit
db.serverStatus();
db.currentOp();
🚀 Tối ưu tốt sẽ giúp MySQL và MongoDB chạy nhanh hơn, tùy vào mục đích sử dụng!