"""
数据库配置路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.db import get_default_db
from database.models import DBConfig

router = APIRouter(prefix="/api/dbconfig", tags=["数据库配置"])


class DBConfigCreate(BaseModel):
    """创建数据库配置请求"""
    user_id: int
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str


class DBConfigUpdate(BaseModel):
    """更新数据库配置请求"""
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str


class DBConfigResponse(BaseModel):
    """数据库配置响应"""
    id: int
    user_id: int
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    is_active: int
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/", response_model=DBConfigResponse)
def create_db_config(config: DBConfigCreate, db: Session = Depends(get_default_db)):
    """创建数据库配置"""
    db_config = DBConfig(
        user_id=config.user_id,
        db_host=config.db_host,
        db_port=config.db_port,
        db_user=config.db_user,
        db_password=config.db_password,
        db_name=config.db_name,
        is_active=0
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return DBConfigResponse(
        id=db_config.id,
        user_id=db_config.user_id,
        db_host=db_config.db_host,
        db_port=db_config.db_port,
        db_user=db_config.db_user,
        db_password=db_config.db_password,
        db_name=db_config.db_name,
        is_active=db_config.is_active,
        created_at=db_config.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )


@router.get("/", response_model=List[DBConfigResponse])
def get_db_configs(user_id: int, db: Session = Depends(get_default_db)):
    """获取用户的所有数据库配置"""
    configs = db.query(DBConfig).filter(DBConfig.user_id == user_id).all()
    
    return [
        DBConfigResponse(
            id=c.id,
            user_id=c.user_id,
            db_host=c.db_host,
            db_port=c.db_port,
            db_user=c.db_user,
            db_password=c.db_password,
            db_name=c.db_name,
            is_active=c.is_active,
            created_at=c.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )
        for c in configs
    ]


@router.get("/active")
def get_active_db_config(user_id: int, db: Session = Depends(get_default_db)):
    """获取用户当前激活的数据库配置"""
    config = db.query(DBConfig).filter(
        DBConfig.user_id == user_id,
        DBConfig.is_active == 1
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="未找到激活的数据库配置")
    
    return DBConfigResponse(
        id=config.id,
        user_id=config.user_id,
        db_host=config.db_host,
        db_port=config.db_port,
        db_user=config.db_user,
        db_password=config.db_password,
        db_name=config.db_name,
        is_active=config.is_active,
        created_at=config.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )


@router.put("/{config_id}/activate")
def activate_db_config(
    config_id: int,
    user_id: int,
    db: Session = Depends(get_default_db)
):
    """激活指定的数据库配置"""
    # 先取消该用户的所有激活配置
    db.query(DBConfig).filter(DBConfig.user_id == user_id).update({"is_active": 0})
    
    # 激活指定配置
    config = db.query(DBConfig).filter(DBConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="数据库配置不存在")
    
    config.is_active = 1
    db.commit()
    
    return {"message": "数据库配置已激活"}


@router.put("/{config_id}", response_model=DBConfigResponse)
def update_db_config(
    config_id: int,
    config_update: DBConfigUpdate,
    db: Session = Depends(get_default_db)
):
    """更新数据库配置"""
    config = db.query(DBConfig).filter(DBConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="数据库配置不存在")
    
    config.db_host = config_update.db_host
    config.db_port = config_update.db_port
    config.db_user = config_update.db_user
    config.db_password = config_update.db_password
    config.db_name = config_update.db_name
    
    db.commit()
    db.refresh(config)
    
    return DBConfigResponse(
        id=config.id,
        user_id=config.user_id,
        db_host=config.db_host,
        db_port=config.db_port,
        db_user=config.db_user,
        db_password=config.db_password,
        db_name=config.db_name,
        is_active=config.is_active,
        created_at=config.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )


@router.delete("/{config_id}")
def delete_db_config(config_id: int, db: Session = Depends(get_default_db)):
    """删除数据库配置"""
    config = db.query(DBConfig).filter(DBConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="数据库配置不存在")
    
    if config.is_active == 1:
        raise HTTPException(status_code=400, detail="无法删除当前激活的数据库配置")
    
    db.delete(config)
    db.commit()
    
    return {"message": "数据库配置删除成功"}
