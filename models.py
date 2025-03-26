# from sqlalchemy import Column, Integer, String
# from database import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)


# from sqlalchemy import Column, Integer, String
# from database import Base

# class User(Base):
#     __tablename__ = "users_async"

#     id = Column(Integer, primary_key=True)  # Không cần index vì mặc định PRIMARY KEY đã có index
#     email = Column(String)  # Bỏ unique và index để tăng tốc độ insert
#     hashed_password = Column(String)

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, index=True, nullable=False)  # Đặt chiều dài cho `username`
    email = Column(String(255), unique=True, index=True, nullable=False)     # Đặt chiều dài cho `email`
    password = Column(String(255), nullable=False)  # Đặt chiều dài cho `password` nếu cần

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, password={self.password})>"
class InforUser(Base):
    __tablename__ = 'infor_user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(255))
    address = Column(String(255))
    avata_path = Column(String(255), nullable=False, default="")
    background_path = Column(String(255), nullable=False, default="")

    def __repr__(self):
        return f"<InforUser(id={self.id}, username={self.username}, avata_path={self.avata_path}, background_path={self.background_path}, address={self.address}, phone={self.phone})>"
