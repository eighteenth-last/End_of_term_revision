"""
动态数据库连接模块
根据用户配置的数据库信息创建连接
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Dict
import threading

# 存储每个用户的数据库引擎
_user_engines: Dict[int, any] = {}
_lock = threading.Lock()


def get_user_db_url(db_config: dict) -> str:
    """
    根据数据库配置生成连接 URL
    :param db_config: 数据库配置字典
    :return: 数据库连接 URL
    """
    return (
        f"mysql+pymysql://{db_config['db_user']}:{db_config['db_password']}"
        f"@{db_config['db_host']}:{db_config['db_port']}"
        f"/{db_config['db_name']}?charset=utf8mb4"
    )


def get_dynamic_engine(user_id: int, db_config: dict):
    """
    获取用户的动态数据库引擎
    :param user_id: 用户 ID
    :param db_config: 数据库配置
    :return: SQLAlchemy Engine
    """
    with _lock:
        # 如果已存在该用户的引擎，先关闭旧的
        if user_id in _user_engines:
            _user_engines[user_id].dispose()
        
        # 创建新引擎
        db_url = get_user_db_url(db_config)
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=5,
            max_overflow=10,
            echo=False
        )
        _user_engines[user_id] = engine
        return engine


def get_user_session(user_id: int, db_config: dict):
    """
    获取用户的数据库会话
    :param user_id: 用户 ID
    :param db_config: 数据库配置
    :return: SQLAlchemy Session
    """
    engine = get_dynamic_engine(user_id, db_config)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def close_user_engine(user_id: int):
    """
    关闭用户的数据库引擎
    :param user_id: 用户 ID
    """
    with _lock:
        if user_id in _user_engines:
            _user_engines[user_id].dispose()
            del _user_engines[user_id]
