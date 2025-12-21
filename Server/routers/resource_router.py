"""
题目资源路由
支持题目图片、表格JSON等资源的管理
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.db import get_default_db
from database.models import QuestionResource, Question


router = APIRouter(prefix="/api/resources", tags=["题目资源"])


class ResourceCreate(BaseModel):
    """创建资源请求"""
    question_id: int
    resource_type: str  # image / table_json / diagram_desc / other
    resource_content: str
    resource_order: int = 0


class ResourceResponse(BaseModel):
    """资源响应"""
    id: int
    question_id: int
    resource_type: str
    resource_content: str
    resource_order: int
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ResourceResponse)
async def create_resource(resource: ResourceCreate, db: Session = Depends(get_default_db)):
    """创建题目资源"""
    # 验证题目是否存在
    question = db.query(Question).filter(Question.id == resource.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # 创建资源
    db_resource = QuestionResource(
        question_id=resource.question_id,
        resource_type=resource.resource_type,
        resource_content=resource.resource_content,
        resource_order=resource.resource_order
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    
    return ResourceResponse(
        id=db_resource.id,
        question_id=db_resource.question_id,
        resource_type=db_resource.resource_type,
        resource_content=db_resource.resource_content,
        resource_order=db_resource.resource_order,
        created_at=str(db_resource.created_at)
    )


@router.get("/question/{question_id}", response_model=List[ResourceResponse])
async def get_question_resources(question_id: int, db: Session = Depends(get_default_db)):
    """获取题目的所有资源"""
    resources = db.query(QuestionResource)\
        .filter(QuestionResource.question_id == question_id)\
        .order_by(QuestionResource.resource_order)\
        .all()
    
    return [
        ResourceResponse(
            id=r.id,
            question_id=r.question_id,
            resource_type=r.resource_type,
            resource_content=r.resource_content,
            resource_order=r.resource_order,
            created_at=str(r.created_at)
        )
        for r in resources
    ]


@router.delete("/{resource_id}")
async def delete_resource(resource_id: int, db: Session = Depends(get_default_db)):
    """删除资源"""
    resource = db.query(QuestionResource).filter(QuestionResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    db.delete(resource)
    db.commit()
    
    return {"message": "删除成功"}
