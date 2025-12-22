"""
SQLAlchemy ORM 模型定义
"""
from sqlalchemy import Column, BigInteger, String, Integer, Text, Enum, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from database.db import Base
import enum


class QuestionType(enum.Enum):
    """题目类型枚举"""
    single = "single"      # 单选
    multiple = "multiple"  # 多选
    judge = "judge"        # 判断
    fill = "fill"          # 填空
    major = "major"        # 大型题


class ShareType(enum.Enum):
    """共享类型枚举"""
    USER = "USER"      # 指定用户共享
    PUBLIC = "PUBLIC"  # 公共共享



class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='用户主键 ID')
    username = Column(String(255), unique=True, nullable=False, comment='用户名（唯一）')
    password_hash = Column(String(255), nullable=False, comment='密码哈希值（加密存储）')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), comment='创建时间')


class DBConfig(Base):
    """用户自定义数据库配置表"""
    __tablename__ = "db_configs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='数据库配置 ID')
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='所属用户 ID')
    db_host = Column(String(255), nullable=False, comment='数据库主机地址')
    db_port = Column(Integer, nullable=False, comment='数据库端口号')
    db_user = Column(String(255), nullable=False, comment='数据库用户名')
    db_password = Column(String(255), nullable=False, comment='数据库密码')
    db_name = Column(String(255), nullable=False, comment='数据库名')
    is_active = Column(Integer, default=0, comment='是否是当前使用的数据库配置')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), comment='创建时间')


class LLMModel(Base):
    """用户自定义大模型配置表"""
    __tablename__ = "llm_models"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='模型配置 ID')
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='所属用户 ID')
    model_name = Column(String(255), nullable=False, comment='模型名称')
    base_url = Column(String(255), nullable=False, comment='模型 API 地址')
    api_key = Column(String(255), nullable=False, comment='API 密钥')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), comment='创建时间')


class Subject(Base):
    """科目表"""
    __tablename__ = "subjects"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='科目ID')
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='所属用户 ID')
    name = Column(String(255), nullable=False, comment='科目名称')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), comment='创建时间')


class SubjectShare(Base):
    """科目共享表"""
    __tablename__ = "subject_shares"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='共享记录ID')
    owner_user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='科目拥有者ID')
    subject_id = Column(BigInteger, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, comment='被共享的科目ID')
    target_user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=True, comment='被共享给的用户ID（NULL表示公共）')
    share_type = Column(Enum(ShareType), nullable=False, comment='共享类型：USER=指定用户，PUBLIC=公共')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), comment='创建时间')



class Question(Base):
    """题库表"""
    __tablename__ = "questions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='题目 ID')
    subject_id = Column(BigInteger, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, comment='科目 ID')
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='用户 ID')
    type = Column(Enum(QuestionType), nullable=False, comment='题目类型')
    question = Column(Text, nullable=False, comment='题干内容')
    options_json = Column(JSON, nullable=True, comment='选项 JSON')
    answer = Column(String(255), nullable=False, comment='正确答案')
    analysis = Column(Text, nullable=False, comment='解析')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), comment='创建时间')
    # 移除is_major字段，统一用type区分


class QuestionResource(Base):
    """题目资源表（图片、表格JSON、图像描述等）"""
    __tablename__ = "question_resources"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='资源ID')
    question_id = Column(BigInteger, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, comment='关联题目ID')
    resource_type = Column(String(50), nullable=False, comment='资源类型：image/table_json/diagram_desc/other')
    resource_content = Column(Text, nullable=False, comment='资源内容：图片URL或JSON数据')
    resource_order = Column(Integer, default=0, comment='资源显示顺序')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment='更新时间')


class PracticeSession(Base):
    """练习会话表"""
    __tablename__ = "practice_sessions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='练习会话 ID')
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='用户 ID')
    subject_id = Column(BigInteger, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, comment='科目 ID')
    total_count = Column(Integer, nullable=False, comment='总题数')
    correct_count = Column(Integer, nullable=False, comment='正确题数')
    wrong_count = Column(Integer, nullable=False, comment='错误题数')
    accuracy = Column(String(10), nullable=False, comment='正确率')
    grade = Column(String(10), nullable=False, comment='成绩等级 A/B/C/D/F')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), comment='练习时间')


class PracticeRecord(Base):
    """练习记录表"""
    __tablename__ = "practice_records"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='练习记录 ID')
    session_id = Column(BigInteger, ForeignKey('practice_sessions.id', ondelete='CASCADE'), nullable=True, comment='练习会话 ID')
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False, comment='用户 ID')
    subject_id = Column(BigInteger, ForeignKey('subjects.id'), nullable=False, comment='科目 ID')
    question_id = Column(BigInteger, ForeignKey('questions.id'), nullable=False, comment='题目 ID')
    user_answer = Column(String(255), nullable=False, comment='用户作答')
    is_correct = Column(Integer, nullable=False, comment='是否正确 1=正确 0=错误')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), comment='作答时间')


class ErrorBook(Base):
    """错题集表"""
    __tablename__ = "error_book"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='错题记录 ID')
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False, comment='用户 ID')
    subject_id = Column(BigInteger, ForeignKey('subjects.id'), nullable=False, comment='科目 ID')
    question_id = Column(BigInteger, ForeignKey('questions.id'), nullable=False, comment='题目 ID')
    wrong_count = Column(Integer, default=1, comment='累计错误次数')
    last_wrong_at = Column(TIMESTAMP, server_default=func.current_timestamp(), comment='最后错误时间')
