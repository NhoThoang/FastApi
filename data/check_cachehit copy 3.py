import mysql.connector

# Cấu hình kết nối MySQL
DATABASE_CONFIG = {
    'user': 'flask',
    'password': 'km@22071994',
    'host': '192.168.5.11',
    'port': 3307,
    'database': 'flask'
}

def check_log_buffer_status():
    connection = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = connection.cursor()

    # Lấy kích thước bộ đệm log
    cursor.execute("SHOW VARIABLES LIKE 'innodb_log_buffer_size'")
    log_buffer_size = cursor.fetchone()

    # Lấy số byte đã được ghi vào log
    cursor.execute("SHOW GLOBAL STATUS LIKE 'Innodb_log_written'")
    log_written = cursor.fetchone()

    # Lấy số byte đã được flush ra đĩa
    cursor.execute("SHOW GLOBAL STATUS LIKE 'Innodb_log_flushed'")
    log_flushed = cursor.fetchone()

    cursor.close()
    connection.close()
    print(f"log_buffer_size: {log_buffer_size}")
    print(f"log_written: {log_written}")
    print(f"log_flushed: {log_flushed}")
    if log_buffer_size and log_written and log_flushed:
        log_buffer_size_value = int(log_buffer_size[1])
        log_written_value = int(log_written[1])
        log_flushed_value = int(log_flushed[1])

        print(f"innodb_log_buffer_size: {log_buffer_size_value} bytes")
        print(f"Innodb_log_written: {log_written_value} bytes")
        print(f"Innodb_log_flushed: {log_flushed_value} bytes")

        # Kiểm tra xem log buffer có thể bị tràn không
        if log_written_value - log_flushed_value > log_buffer_size_value:
            print("⚠️ Log buffer có thể bị tràn, cần xem xét tăng kích thước log buffer.")
        else:
            print("✅ Log buffer đang hoạt động bình thường.")

    else:
        print("Khoại tạo bộ đệm log hoạt động. Vui lồng kiểm tra cấu hình MySQL.")


def get_binlog_cache_size():
    connection = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = connection.cursor()

    cursor.execute("SHOW VARIABLES LIKE 'binlog_cache_size'")
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        binlog_cache_size = int(result[1])
        print(f"binlog_cache_size: {binlog_cache_size:,} bytes")  # In giá trị với định dạng có dấu phẩy
    else:
        print("Không lấy được giá trị binlog_cache_size.")




def check_binlog_cache():
    connection = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = connection.cursor()

    # Thực thi câu lệnh để lấy thông số binlog cache
    cursor.execute("SHOW GLOBAL STATUS LIKE 'Binlog_cache%'")
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()

    # Kiểm tra và in kết quả
    binlog_cache_use = None
    binlog_cache_disk_use = None

    for row in result:
        if row[0] == 'Binlog_cache_use':
            binlog_cache_use = int(row[1])
        elif row[0] == 'Binlog_cache_disk_use':
            binlog_cache_disk_use = int(row[1])

    if binlog_cache_disk_use > 0:
        print(f"⚠️ Bộ đệm binlog đã bị tràn {binlog_cache_disk_use} lần.")
    else:
        print("✅ Bộ đệm binlog chưa bị tràn.")

    print(f"Binlog cache đã được sử dụng {binlog_cache_use} lần.")

# Gọi hàm để kiểm tra tình trạng binlog cache
check_binlog_cache()



def get_cache_hit_ratio():
    """Lấy Cache Hit Ratio và các cache variables từ MySQL"""
    # Kết nối đến MySQL
    connection = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = connection.cursor()

    try:
        # Lấy các biến về bộ đệm và cache
        cursor.execute("SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%'")
        result = cursor.fetchall()
        buffer_pool_stats = {row[0]: int(row[1]) for row in result}

        # Tính Cache Hit Ratio
        if buffer_pool_stats.get("Innodb_buffer_pool_read_requests", 0) > 0:
            cache_hit_ratio = (1 - (buffer_pool_stats["Innodb_buffer_pool_reads"] / 
                                     buffer_pool_stats["Innodb_buffer_pool_read_requests"])) * 100
        else:
            cache_hit_ratio = 0
        
        return cache_hit_ratio  # Trả về tỷ lệ cache hit

    finally:
        cursor.close()
        connection.close()

def get_cache_variables(variable):
    """Lấy giá trị của biến cache từ MySQL"""
    # Kết nối đến MySQL
    connection = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = connection.cursor()

    try:
        cursor.execute(f"SHOW VARIABLES LIKE '{variable}'")
        result = cursor.fetchone()
        if result:
            return result[1]  # Trả về giá trị của biến cache
    finally:
        cursor.close()
        connection.close()

def main():
    # Lấy tỷ lệ cache hit
    cache_hit_ratio = get_cache_hit_ratio()
    print(f"🔥 Cache Hit Ratio: {cache_hit_ratio:.2f}%")  # In kết quả Cache Hit Ratio
    
    # Lấy và in các biến cache
    variables = ["innodb_buffer_pool_size", "innodb_log_buffer_size", "binlog_cache_size", "thread_cache_size"]
    for variable in variables:
        value = get_cache_variables(variable)
        print(f"{variable}: {int(value):,}")  # In giá trị của các biến cache

# Chạy hàm chính
main()
