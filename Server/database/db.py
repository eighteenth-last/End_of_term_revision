"""
默认数据库连接配置
用于初始化和管理员数据库
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 默认数据库配置（用于初始系统表）
DEFAULT_DATABASE_URL = "mysql+pymysql://admin:qwer4321@localhost:3306/end_of_term_revision?charset=utf8mb4"

# 创建默认引擎
default_engine = create_engine(
    DEFAULT_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# 创建会话工厂
DefaultSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=default_engine)

# 创建基类
Base = declarative_base()


def get_default_db():
    """获取默认数据库会话"""
    db = DefaultSessionLocal()
    try:
        yield db
    finally:
        db.close()
