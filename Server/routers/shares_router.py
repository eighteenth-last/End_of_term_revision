"""
共享管理路由
提供科目共享的API接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from database.db import get_default_db
from database.models import User
from services.share_service import ShareService

router = APIRouter(prefix="/api/shares", tags=["共享管理"])


class SetShareRequest(BaseModel):
    """设置共享请求"""
    owner_user_id: int = Field(..., description="科目拥有者ID")
    subject_id: int = Field(..., description="科目ID")
    target_user_id: Optional[int] = Field(None, description="目标用户ID（公共共享时不需要）")
    share_type: str = Field(..., description="共享类型：USER/PUBLIC")


class ShareResponse(BaseModel):
    """共享响应"""
    id: int
    subject_id: int
    target_user_id: Optional[int]
    target_username: Optional[str] = None
    share_type: str
    created_at: str


class MySharedSubjectResponse(BaseModel):
    """我共享的科目响应"""
    id: int
    subject_id: int
    subject_name: str
    target_user_id: Optional[int]
    share_type: str
    created_at: str


class UserSearchResponse(BaseModel):
    """用户搜索响应"""
    id: int
    username: str


@router.post("/", response_model=ShareResponse)
def set_share(request: SetShareRequest, db: Session = Depends(get_default_db)):
    """
    设置科目共享
    - 支持指定用户共享（USER）和公共共享（PUBLIC）
    - 只有科目拥有者可以设置共享
    """
    result = ShareService.set_share(
        owner_user_id=request.owner_user_id,
        subject_id=request.subject_id,
        target_user_id=request.target_user_id,
        share_type=request.share_type,
        db=db
    )
    
    return ShareResponse(**result)


@router.delete("/{subject_id}")
def cancel_share(
    subject_id: int,
    owner_user_id: int = Query(..., description="科目拥有者ID"),
    target_user_id: Optional[int] = Query(None, description="目标用户ID"),
    share_type: Optional[str] = Query(None, description="共享类型"),
    db: Session = Depends(get_default_db)
):
    """
    取消科目共享
    - 只有科目拥有者可以取消共享
    - 可以指定target_user_id和share_type来精确删除某条共享记录
    """
    result = ShareService.cancel_share(
        owner_user_id=owner_user_id,
        subject_id=subject_id,
        target_user_id=target_user_id,
        share_type=share_type,
        db=db
    )
    
    return result


@router.get("/status/{subject_id}", response_model=List[ShareResponse])
def get_share_status(subject_id: int, db: Session = Depends(get_default_db)):
    """
    查询科目的共享状态
    - 返回该科目所有的共享记录
    """
    result = ShareService.get_share_status(subject_id, db)
    return [ShareResponse(**item) for item in result]


@router.get("/my-shared", response_model=List[MySharedSubjectResponse])
def get_my_shared_subjects(user_id: int, db: Session = Depends(get_default_db)):
    """
    查询我共享出去的科目列表
    """
    result = ShareService.get_my_shared_subjects(user_id, db)
    return [MySharedSubjectResponse(**item) for item in result]


@router.get("/users/search", response_model=List[UserSearchResponse])
def search_users(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    current_user_id: int = Query(..., description="当前用户ID（用于排除自己）"),
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    db: Session = Depends(get_default_db)
):
    """
    搜索用户（用于指定用户共享）
    - 根据用户名模糊搜索
    - 排除当前登录用户（不能共享给自己）
    """
    users = db.query(User).filter(
        User.username.like(f"%{keyword}%"),
        User.id != current_user_id  # 排除当前用户
    ).limit(limit).all()
    
    return [UserSearchResponse(id=u.id, username=u.username) for u in users]
