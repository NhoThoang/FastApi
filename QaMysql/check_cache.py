from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Cấu hình Database URL
DATABASE_URL = "mysql+mysqlconnector://your_user:your_password@your_host:3306/your_database"

# Tạo engine kết nối với MySQL
engine = create_engine(DATABASE_URL, echo=True)

def get_innodb_buffer_pool_size():
    """Trả về kích thước của InnoDB buffer pool"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SHOW VARIABLES LIKE 'innodb_buffer_pool_size'")
            # Chuyển kết quả thành dictionary
            innodb_buffer_pool_size = {row[0]: int(row[1]) for row in result}
            return innodb_buffer_pool_size
    except SQLAlchemyError as e:
        print(f"Error while fetching MySQL variable: {e}")
        return None

if __name__ == "__main__":
    result = get_innodb_buffer_pool_size()
    if result:
        print(f"InnoDB Buffer Pool Size: {result['innodb_buffer_pool_size']} bytes")
