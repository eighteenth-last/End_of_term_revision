"""
科目路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.db import get_default_db
from database.models import Subject

router = APIRouter(prefix="/api/subjects", tags=["科目管理"])


class SubjectCreate(BaseModel):
    """创建科目请求"""
    name: str
    user_id: int


class SubjectResponse(BaseModel):
    """科目响应"""
    id: int
    name: str
    user_id: int
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/", response_model=SubjectResponse)
def create_subject(subject: SubjectCreate, db: Session = Depends(get_default_db)):
    """创建科目"""
    # 检查是否已存在
    existing = db.query(Subject).filter(
        Subject.user_id == subject.user_id,
        Subject.name == subject.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该科目已存在")
    
    db_subject = Subject(
        user_id=subject.user_id,
        name=subject.name
    )
    
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    
    return SubjectResponse(
        id=db_subject.id,
        name=db_subject.name,
        user_id=db_subject.user_id,
        created_at=db_subject.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )


@router.get("/", response_model=List[SubjectResponse])
def get_subjects(user_id: int, db: Session = Depends(get_default_db)):
    """获取用户的所有科目"""
    subjects = db.query(Subject).filter(Subject.user_id == user_id).all()
    
    return [
        SubjectResponse(
            id=s.id,
            name=s.name,
            user_id=s.user_id,
            created_at=s.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )
        for s in subjects
    ]


@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(subject_id: int, user_id: int, db: Session = Depends(get_default_db)):
    """获取单个科目"""
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == user_id
    ).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="科目不存在或无权访问")
    
    return SubjectResponse(
        id=subject.id,
        name=subject.name,
        user_id=subject.user_id,
        created_at=subject.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )


@router.delete("/{subject_id}")
def delete_subject(subject_id: int, user_id: int, db: Session = Depends(get_default_db)):
    """删除科目"""
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == user_id
    ).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="科目不存在或无权删除")
    
    db.delete(subject)
    db.commit()
    
    return {"message": "科目删除成功"}
