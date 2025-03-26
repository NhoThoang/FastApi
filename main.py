from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from schemas import UserCreate, UserLogin, UserBase, UserResponse, InfoUser,update_information
from crud import (create_user, get_users, get_user_by_id, login_user, information_user,
                  update_infor_user)
from database import get_db, engine, Base
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả domain
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức (GET, POST, OPTIONS, PUT, DELETE)
    allow_headers=["*"],  # Cho phép tất cả các headers
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hàm tạo JWT token (dùng thư viện PyJWT)
from jose import JWTError, jwt
from datetime import datetime, timedelta

# SECRET_KEY và ALGORITHM cho JWT
SECRET_KEY = "f3e9a7b9f7fcbf8e9a7b3f4c3e9d4e5e4d8d7e9f4f5e9d8f3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta = None):
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def verify_access_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception

# Hàm khởi động ứng dụng, kết nối cơ sở dữ liệu
@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()

@app.post("/register/", response_model=UserCreate)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db=db, user=user)  # Gọi hàm tạo người dùng

@app.post("/login/")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    print(user.username, user.password)
    username = await login_user(db, user)
    if username:
        access_token = create_access_token(data={"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}
@app.post("/information/")
async def information(user: InfoUser, db: AsyncSession = Depends(get_db)):
    username = await information_user(db, user.username)
    return username
@app.post("/update_information/")
async def update_information(user: update_information, db: AsyncSession = Depends(get_db)):
    username = await update_infor_user(db, user)
    return username

@app.get("/users/", response_model=list[UserResponse])
async def get_users_endpoint(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    # Gọi hàm get_users bất đồng bộ để lấy danh sách người dùng
    users = await get_users(db=db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
