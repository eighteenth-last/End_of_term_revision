"""
自定义模型路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.db import get_default_db
from database.models import LLMModel

router = APIRouter(prefix="/api/models", tags=["模型配置"])


class ModelCreate(BaseModel):
    """创建模型配置请求"""
    user_id: int
    model_name: str
    base_url: str
    api_key: str


class ModelUpdate(BaseModel):
    """更新模型配置请求"""
    model_name: str
    base_url: str
    api_key: str


class ModelResponse(BaseModel):
    """模型配置响应"""
    id: int
    user_id: int
    model_name: str
    base_url: str
    api_key: str
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ModelResponse)
def create_model_config(model: ModelCreate, db: Session = Depends(get_default_db)):
    """创建模型配置"""
    db_model = LLMModel(
        user_id=model.user_id,
        model_name=model.model_name,
        base_url=model.base_url,
        api_key=model.api_key
    )
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return ModelResponse(
        id=db_model.id,
        user_id=db_model.user_id,
        model_name=db_model.model_name,
        base_url=db_model.base_url,
        api_key=db_model.api_key,
        created_at=db_model.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )


@router.get("/", response_model=List[ModelResponse])
def get_model_configs(user_id: int, db: Session = Depends(get_default_db)):
    """获取用户的所有模型配置"""
    models = db.query(LLMModel).filter(LLMModel.user_id == user_id).all()
    
    return [
        ModelResponse(
            id=m.id,
            user_id=m.user_id,
            model_name=m.model_name,
            base_url=m.base_url,
            api_key=m.api_key,
            created_at=m.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )
        for m in models
    ]


@router.get("/{model_id}", response_model=ModelResponse)
def get_model_config(model_id: int, db: Session = Depends(get_default_db)):
    """获取单个模型配置"""
    model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    return ModelResponse(
        id=model.id,
        user_id=model.user_id,
        model_name=model.model_name,
        base_url=model.base_url,
        api_key=model.api_key,
        created_at=model.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )


@router.put("/{model_id}", response_model=ModelResponse)
def update_model_config(
    model_id: int,
    model_update: ModelUpdate,
    db: Session = Depends(get_default_db)
):
    """更新模型配置"""
    model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    model.model_name = model_update.model_name
    model.base_url = model_update.base_url
    model.api_key = model_update.api_key
    
    db.commit()
    db.refresh(model)
    
    return ModelResponse(
        id=model.id,
        user_id=model.user_id,
        model_name=model.model_name,
        base_url=model.base_url,
        api_key=model.api_key,
        created_at=model.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )


@router.delete("/{model_id}")
def delete_model_config(model_id: int, db: Session = Depends(get_default_db)):
    """删除模型配置"""
    model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    db.delete(model)
    db.commit()
    
    return {"message": "模型配置删除成功"}
