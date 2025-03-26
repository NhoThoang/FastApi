from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User,InforUser
from typing import Literal, Type, Union
from schemas import UserCreate, format_post_information
from fastapi import HTTPException, status
from utils import hash_password, verify_password




    
async def check_user_exists(db: AsyncSession, username: str, table: Type[Union[User, InforUser]] = User, exist: Literal[True, False] = True)-> str | None:
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

async def check_email_exists(db: AsyncSession, email: str, exist: Literal[True, False] = True)-> str | None:
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
async def get_password(db: AsyncSession, username: str):
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
        await db.refresh(db_user)
        return db_user
    except Exception as e:
        await db.rollback()
        print(f"Error during commit: {e}")  # In lỗi ra console
        raise e  # Có thể trả về response lỗi trong API
async def login_user(db: AsyncSession, user: UserCreate):
    # print(user.username, user.password)
    username = await check_user_exists(db, user.username, exist=True)
    if username:
        password_hash = await get_password(db, username)
        check_pass= await verify_password(user.password, password_hash)
        if not check_pass:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")
        return username
    
async def information_user(db: AsyncSession, username: str)-> InforUser | None:
    username = await check_user_exists(db, username,table=InforUser, exist=True)
    if username:
        user = await db.execute(select(InforUser).filter(InforUser.username == username).limit(1))
        user = user.scalar()
        return user
async def update_infor_user(db: AsyncSession, user: InforUser)-> str | None:
    check_table_user = await check_user_exists(db, user.username, exist=True)
    if check_table_user:
        result = await db.execute(select(InforUser).filter(InforUser.username == user.username).limit(1))
        existing_info = result.scalar()
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
            await db.refresh(new_user)
            return new_user


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10):
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)  # Bất đồng bộ thực thi truy vấn
    return result.scalars().all()

async def get_user_by_id(db: AsyncSession, user_id: int):
    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    return result.scalars().first()
