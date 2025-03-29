from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User,InforUser
from typing import Literal, Type, Union
from schemas import *
from utils import hash_password, verify_password
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Form
from fastapi.responses import JSONResponse
import shutil
from fastapi.responses import FileResponse


import os
import uuid

UPLOAD_AVATAR_DIR = "uploads/avatars"
UPLOAD_BACKGROUND_DIR = "uploads/backgrounds"
os.makedirs(UPLOAD_BACKGROUND_DIR, exist_ok=True)
os.makedirs(UPLOAD_AVATAR_DIR, exist_ok=True)

async def get_avatar_background_path(db: AsyncSession, username: str):
    await check_user_exists(db=db, username=username, table=InforUser, exist=True)
    result  = await db.execute(select(InforUser).filter(InforUser.username == username).limit(1))
    user = result.scalar()
    return user
    # print(user.background_path)
    # print(user.avatar_path)
    # avata_path = user.avatar_path
    # background_path = user.background_path
    # if not avata_path or not background_path:
    #     return {"error": "File not found"}
    # return FileResponse(avata_path, media_type="image/png")
    # file_path = f"{UPLOAD_BACKGROUND_DIR}/{username}.jpg"
    # file_path = f"{UPLOAD_AVATAR_DIR}/{username}.jpg"
    # # Kiểm tra nếu file tồn tại
    # if not os.path.exists(file_path):
    #     return {"error": "File not found"}
    # return FileResponse(file_path, media_type="image/png")
    # return {"background_path": user.background_path, "avatar_path": user.avatar_path}

# async def get_image_avatar_background(username: str, db: AsyncSession):
#     await check_user_exists(db=db, username=username, table=InforUser, exist=True)
    
#     result  = await db.execute(select(InforUser).filter(InforUser.username == username).limit(1))
#     user = result.scalar()
    
#     if not user or not user.avatar_path or not user.background_path:
#         raise HTTPException(status_code=404, detail="File not found")

#     # Trả về URL thay vì gửi ảnh trực tiếp
#     return {
#         "avatar_url": f"/static/{username}.jpg",
#         "background_url": f"/static/{username}_bg.jpg"
#     }

async def upload_background(db: AsyncSession,
                            file: UploadFile = File(...),
                            username: str = Form(...)):
    await check_user_exists(db=db, username=username, exist=True)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File không phải là ảnh")
    file_path = f"{UPLOAD_BACKGROUND_DIR}/{username}.jpg"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    result = await db.execute(select(InforUser).filter(InforUser.username == username).limit(1))
    existing_info = result.scalar()
    if existing_info:
        existing_info.background_path = file_path
        await db.commit()
    else:
        new_user = InforUser(username=username, background_path=file_path)
        db.add(new_user)
        await db.commit()
    return ({"message": "Background uploaded successfully"})
async def upload_avatar(db: AsyncSession,
                        file: UploadFile = File(...),
                        username: str=Form(...)):
    await check_user_exists(db=db, username=username, exist=True)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File không phải là ảnh")
    # new_filename = f"{uuid.uuid4()}_avatar_{username}.jpg"
    file_path = f"{UPLOAD_AVATAR_DIR}/{username}.jpg"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    result = await db.execute(select(InforUser).filter(InforUser.username == username).limit(1))
    existing_info = result.scalar()
    if existing_info:
        existing_info.avatar_path = file_path
        await db.commit()
    else:
        new_user = InforUser(username=username, avatar_path=file_path)
        db.add(new_user)
        await db.commit()
    return ({"message": "Avatar uploaded successfully"})


    
async def check_user_exists(db: AsyncSession, username: str,
                            table: Type[Union[User, InforUser]] = User,
                            exist: Literal[True, False] = True)-> str | None:
    existing_user = await db.execute(select(table.username).filter(table.username == username).limit(1))
    existing_user = existing_user.scalar()
    '''if exist= true when fined return true, else return reise error else exists=false when fined return raise error else return true'''
    if exist:
        if existing_user:
            return existing_user
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    else:
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        return existing_user

async def check_email_exists(db: AsyncSession,
                             email: str,
                             exist: Literal[True, False] = True)-> str | None:
    existing_email = await db.execute(select(User.email).filter(User.email == email).limit(1))
    existing_email = existing_email.scalar()
    if exist:
        if existing_email:
            return existing_email
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not found")
    else:
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        return existing_email
async def get_password(db: AsyncSession, username: str)-> str:
    password = await db.execute(select(User.password).filter(User.username == username).limit(1))
    password = password.scalar()
    return password
    
async def create_user(db: AsyncSession, user: UserCreate):
    await check_user_exists(db, user.username, exist=False)
    await check_email_exists(db, user.email, exist=False)
    hashed_password = await hash_password(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    try:
        await db.commit()
        # await db.refresh(db_user)
        return db_user
    except Exception as e:
        await db.rollback()
        print(f"Error during commit: {e}")
        raise e
async def login_user(db: AsyncSession, user: UserLogin):
    # print(user.username, user.password)
    username = await check_user_exists(db, user.username, exist=True)
    if username:
        password_hash = await get_password(db, username)
        check_pass= await verify_password(user.password, password_hash)
        if not check_pass:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")
        return username
    
async def get_phone_address(db: AsyncSession, username: str)-> InforUser | None:
    username = await check_user_exists(db, username, table=InforUser, exist=True)
    if username:
        print("return phone address",username)
        user = await db.execute(select(InforUser).filter(InforUser.username == username).limit(1))
        return user.scalar()
        # user = await db.execute(select(InforUser.phone, InforUser.address)
        #                         .filter(InforUser.username == username).limit(1))
        # # return user.first()
        # phone_address = user.first()
        # return {
        #     "phone": phone_address[0],
        #     "address": phone_address[1]
        # }
async def get_avatar_path(db: AsyncSession, username: str)-> InforUser | None:
    username = await check_user_exists(db, username, table=InforUser, exist=True)
    if username:
        user = await db.execute(select(InforUser.avatar_path).filter(InforUser.username == username).limit(1))
        return user.scalar()
   
async def insert_update_infor_user(db: AsyncSession,
        user: Type[Union[PhoneAddress, Avatar_path, Background_path]]= PhoneAddress,
        insert_update_type: Literal["infor", "avatar", "background"] = "infor")-> str | None:
    check_table_user = await check_user_exists(db, user.username, exist=True)
    if check_table_user:
        result = await db.execute(select(InforUser).filter(InforUser.username == user.username).limit(1))
        existing_info = result.scalar()
        if insert_update_type == "infor":
            if existing_info:
                # Cập nhật thông tin nếu đã tồn tại
                existing_info.phone = user.phone
                existing_info.address = user.address
                await db.commit()
                return existing_info
            else:
                # Tạo mới nếu chưa tồn tại
                new_user = InforUser(
                    username=user.username, 
                    phone=user.phone, 
                    address=user.address
                )
                db.add(new_user)
                await db.commit()
                # await db.refresh(new_user)
                return new_user
        elif insert_update_type == "avatar":
            if existing_info:
                existing_info.avatar_path = user.avatar_path
                await db.commit()
                return existing_info
            else:
                new_user = InforUser(
                    username=user.username, 
                    avatar=user.avatar_path
                )
                db.add(new_user)
                await db.commit()
                return new_user
        elif insert_update_type == "background":
            if existing_info:
                existing_info.background_path = user.background_path
                await db.commit()
                return existing_info
            else:
                new_user = InforUser(
                    username=user.username, 
                    background=user.background
                )                
                db.add(new_user)
                await db.commit()
                return new_user


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10):
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)  # Bất đồng bộ thực thi truy vấn
    return result.scalars().all()

async def get_user_by_id(db: AsyncSession, user_id: int):
    query = await db.execute(select(User).filter(User.id == user_id).limit(1))
    return query.scalar()
    # result = await db.execute(query)
    # return result.scalars().first()
