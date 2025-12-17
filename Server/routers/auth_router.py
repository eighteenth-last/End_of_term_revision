"""
用户认证路由模块
提供用户注册、登录、获取当前用户信息等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import bcrypt
import jwt

from database.db import get_default_db
from database.models import User

router = APIRouter(prefix="/api/auth", tags=["用户认证"])

# JWT配置
SECRET_KEY = "your-secret-key-change-in-production"  # 生产环境请使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# 请求/响应模型
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")

class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

class LoginResponse(BaseModel):
    token: str
    user: UserResponse


def hash_password(password: str) -> str:
    """密码加密"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict) -> str:
    """创建JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token无效")


@router.post("/register", response_model=LoginResponse, summary="用户注册")
def register(request: RegisterRequest, db: Session = Depends(get_default_db)):
    """
    用户注册接口
    - 检查用户名是否已存在
    - 密码使用bcrypt加密
    - 返回JWT token和用户信息
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户
    hashed_pw = hash_password(request.password)
    new_user = User(
        username=request.username,
        password_hash=hashed_pw
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 生成token
    token = create_access_token({"user_id": new_user.id, "username": new_user.username})
    
    return {
        "token": token,
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "created_at": new_user.created_at
        }
    }


@router.post("/login", response_model=LoginResponse, summary="用户登录")
def login(request: LoginRequest, db: Session = Depends(get_default_db)):
    """
    用户登录接口
    - 验证用户名和密码
    - 返回JWT token和用户信息
    """
    # 查找用户
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 生成token
    token = create_access_token({"user_id": user.id, "username": user.username})
    
    return {
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at
        }
    }


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
def get_current_user(token: str, db: Session = Depends(get_default_db)):
    """
    获取当前登录用户信息
    - 需要在请求头中提供token
    """
    # 解码token
    payload = decode_token(token)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="无效的token")
    
    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "id": user.id,
        "username": user.username,
        "created_at": user.created_at
    }


@router.post("/logout", summary="用户登出")
def logout():
    """
    用户登出接口
    - 前端需要删除本地存储的token
    """
    return {"message": "登出成功"}
