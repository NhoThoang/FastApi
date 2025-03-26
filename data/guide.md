nghiên cứ sự ảnh hưởng tới tốc độ của database  
dùng sql_pool đẻ tạo các connection có sẵn   
chạy bất đồng bộ để dùng các connection đó  
tối ưu tốc đọ bằng connfig   
+ setindex, partition, index hint, partition hint  
+ kiểm tra cache mysql gồm các cache nào  
pip install sqlalchemy[asyncio] asyncmy aiomysql
## Option trong sqlalstremy
name	Tên cột trong database. Nếu không đặt, SQLAlchemy tự động lấy tên biến trong class.
type_	Kiểu dữ liệu của cột (ví dụ: Integer, String(50), Boolean, DateTime...).
primary_key	Đánh dấu cột này là Primary Key (khóa chính).
autoincrement	Chỉ định cột có tự động tăng hay không (True / False / "auto").
nullable	Cho phép giá trị NULL nếu True, không cho phép nếu False.
unique	Đánh dấu cột là duy nhất (không được trùng giá trị).
index	Tạo index trên cột để tối ưu truy vấn.
default	Giá trị mặc định cho cột khi thêm dữ liệu mới.
server_default	Giá trị mặc định trên database (ví dụ: server_default=text("CURRENT_TIMESTAMP")).
onupdate	Giá trị mới khi bản ghi được cập nhật.
server_onupdate	Giá trị cập nhật trên database (ví dụ: server_onupdate=text("CURRENT_TIMESTAMP")).
info	Dictionary lưu thông tin thêm về cột (metadata).
comment	Ghi chú cho cột trong database.
system	Nếu True, cột này không xuất hiện trong các lệnh SELECT *.