from pydantic import BaseModel, EmailStr, validator
from fastapi import HTTPException, status
import re

class Username(BaseModel):
    username: str

    @validator('username')
    def username_min_length(cls, v):
        if len(v) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters long"
            )
        return v

class Password(BaseModel):
    password: str
    # class Config:
    #     from_attributes = True
        

    # Kiểm tra mật khẩu có đủ các yêu cầu về độ mạnh
    @validator('password')
    def validate_password(cls, v):
        # Kiểm tra độ dài của mật khẩu
        if len(v) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Kiểm tra mật khẩu có ít nhất một chữ cái in hoa
        if not re.search(r'[A-Z]', v):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one uppercase letter"
            )
        
        # Kiểm tra mật khẩu có ít nhất một chữ cái in thường
        if not re.search(r'[a-z]', v):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one lowercase letter"
            )

        # Kiểm tra mật khẩu có ít nhất một chữ số
        if not re.search(r'[0-9]', v):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one number"
            )

        # Kiểm tra mật khẩu có ít nhất một ký tự đặc biệt
        if not re.search(r'[@$!%*?&]', v):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one special character: @$!%*?&"
            )

        return v
    
class UserCreate(Password, Username):
    email: EmailStr 

class UserLogin(Password, Username):
    pass

class PhoneAddress(Username):
    phone: str
    address: str

    
class Avatar_path(Username):
    avatar_path: str
class Background_path(Username):
    background_path: str

class response_path_avatar_background(BaseModel):
    avatar_path: str
    background_path: str


class response_phone_address(BaseModel):
    phone: str
    address: str
    avatar_path: str
    background_path: str

    
    # @validator('phone')
    # def validate_phone(cls, v):
    #     # Kiểm tra định dạng số điện thoại
    #     if not re.match(r'^\+?[0-9]{10,15}$', v):
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Invalid phone number format"
    #         )
    #     return v
    
    # @validator('address')
    # def validate_address(cls, v):
    #     if len(v.strip()) < 5:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Address must be at least 5 characters long"
    #         )
    #     return v


# class UserResponse(UserBase):
#     id: int
    # class Config:
    #     from_attributes = True
