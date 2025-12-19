"""
错题集服务
错题的记录、查询、练习等
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from database.models import ErrorBook, Question
from datetime import datetime
import json


class ErrorService:
    """错题服务类"""
    
    @staticmethod
    def add_error(
        db: Session,
        user_id: int,
        subject_id: int,
        question_id: int
    ) -> ErrorBook:
        """
        添加或更新错题记录
        :param db: 数据库会话
        :param user_id: 用户 ID
        :param subject_id: 科目 ID
        :param question_id: 题目 ID
        :return: ErrorBook 实例
        """
        # 查询是否已存在
        error = db.query(ErrorBook).filter(
            and_(
                ErrorBook.user_id == user_id,
                ErrorBook.subject_id == subject_id,
                ErrorBook.question_id == question_id
            )
        ).first()
        
        if error:
            # 已存在，增加错误次数
            error.wrong_count += 1
            error.last_wrong_at = datetime.now()
        else:
            # 不存在，创建新记录
            error = ErrorBook(
                user_id=user_id,
                subject_id=subject_id,
                question_id=question_id,
                wrong_count=1
            )
            db.add(error)
        
        db.commit()
        db.refresh(error)
        
        return error
    
    @staticmethod
    def batch_add_errors(
        db: Session,
        user_id: int,
        subject_id: int,
        question_ids: List[int]
    ) -> List[ErrorBook]:
        """
        批量添加错题
        :param db: 数据库会话
        :param user_id: 用户 ID
        :param subject_id: 科目 ID
        :param question_ids: 题目 ID 列表
        :return: ErrorBook 列表
        """
        errors = []
        
        for question_id in question_ids:
            error = ErrorService.add_error(db, user_id, subject_id, question_id)
            errors.append(error)
        
        return errors
    
    @staticmethod
    def get_error_questions(
        db: Session,
        user_id: int,
        subject_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取错题列表（包含题目详情）
        :param db: 数据库会话
        :param user_id: 用户 ID
        :param subject_id: 科目 ID（可选）
        :param limit: 限制数量（可选）
        :return: 错题列表
        """
        query = db.query(ErrorBook, Question).join(
            Question, ErrorBook.question_id == Question.id
        ).filter(ErrorBook.user_id == user_id)
        
        if subject_id:
            query = query.filter(ErrorBook.subject_id == subject_id)
        
        query = query.order_by(ErrorBook.last_wrong_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        results = query.all()
        
        error_list = []
        for error, question in results:
            # 解析 JSON 字符串为列表
            options = json.loads(question.options_json) if question.options_json else []
            
            error_list.append({
                "error_id": error.id,
                "question_id": question.id,
                "subject_id": question.subject_id,
                "type": question.type.value,
                "question": question.question,
                "options": options,
                "answer": question.answer,
                "analysis": question.analysis,
                "wrong_count": error.wrong_count,
                "last_wrong_at": error.last_wrong_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return error_list
    
    @staticmethod
    def get_random_error_questions(
        db: Session,
        user_id: int,
        subject_id: int,
        question_counts: Dict[str, int]
    ) -> List[Question]:
        """
        随机获取错题（按题型）
        :param db: 数据库会话
        :param user_id: 用户 ID
        :param subject_id: 科目 ID
        :param question_counts: 题目类型和数量字典
        :return: Question 列表
        """
        questions = []
        
        for question_type, count in question_counts.items():
            if count > 0:
                # 查询该类型的错题
                error_questions = db.query(Question).join(
                    ErrorBook, ErrorBook.question_id == Question.id
                ).filter(
                    and_(
                        ErrorBook.user_id == user_id,
                        ErrorBook.subject_id == subject_id,
                        Question.type == question_type
                    )
                ).order_by(func.rand()).limit(count).all()
                
                questions.extend(error_questions)
        
        return questions
    
    @staticmethod
    def remove_error(db: Session, error_id: int, user_id: int = None) -> bool:
        """
        移除错题记录
        :param db: 数据库会话
        :param error_id: 错题记录 ID
        :param user_id: 用户 ID（可选，用于数据隔离验证）
        :return: 是否移除成功
        """
        query = db.query(ErrorBook).filter(ErrorBook.id == error_id)
        if user_id is not None:
            query = query.filter(ErrorBook.user_id == user_id)
        error = query.first()
        if error:
            db.delete(error)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_error_count(db: Session, user_id: int, subject_id: Optional[int] = None) -> int:
        """
        获取错题数量
        :param db: 数据库会话
        :param user_id: 用户 ID
        :param subject_id: 科目 ID（可选）
        :return: 错题数量
        """
        query = db.query(ErrorBook).filter(ErrorBook.user_id == user_id)
        
        if subject_id:
            query = query.filter(ErrorBook.subject_id == subject_id)
        
        return query.count()
    
    @staticmethod
    def get_error_types_by_subject(db: Session, user_id: int, subject_id: int) -> List[str]:
        """
        获取科目下错题的题目类型
        :param db: 数据库会话
        :param user_id: 用户 ID
        :param subject_id: 科目 ID
        :return: 题目类型列表
        """
        types = db.query(Question.type).join(
            ErrorBook, ErrorBook.question_id == Question.id
        ).filter(
            and_(
                ErrorBook.user_id == user_id,
                ErrorBook.subject_id == subject_id
            )
        ).distinct().all()
        
        return [t[0].value for t in types]
