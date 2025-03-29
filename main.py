from fastapi import FastAPI, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from crud import *
from database import get_db, engine, Base
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
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
    return await create_user(db=db, user=user)
@app.post("/login/", response_model=dict)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    print(user.username, user.password)
    username = await login_user(db, user)
    if username:
        access_token = create_access_token(data={"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}
@app.post("/phone_address/", response_model = response_phone_address)
async def route_get_phone_address(user: Username, db: AsyncSession = Depends(get_db)):
    username = await get_phone_address(db, user.username)
    return username
@app.post("/insert_update_phone_address/", response_model = Username)
async def InsertUpdatePhoneaddress(user: PhoneAddress, db: AsyncSession = Depends(get_db)):
    username = await insert_update_infor_user(db=db, user=user, insert_update_type="infor")
    return username 

@app.get("/users/", response_model=list[UserCreate])
async def get_users_endpoint(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    # Gọi hàm get_users bất đồng bộ để lấy danh sách người dùng
    users = await get_users(db=db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model= UserCreate)
async def get_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
# upload_avatar save in db and save file 
@app.post("/upload_avatar/", response_model=dict)
async def upload_avatar_endpoint(file: UploadFile = File(...), username: str = Form(...),  db: AsyncSession = Depends(get_db)):
    return await upload_avatar(db=db, file=file, username=username)

@app.post("/upload_background/", response_model=dict)
async def upload_background_endpoint(file: UploadFile = File(...), username: str = Form(...),  db: AsyncSession = Depends(get_db)):
    return await upload_background(db=db, file=file, username=username)
@app.post("/get_avatar_background_path/",response_model=response_path_avatar_background)
async def get_avatar_background_path_endpoint(user: Username, db: AsyncSession = Depends(get_db),):
    username = user.username
    return await get_avatar_background_path(db=db, username = username)


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
