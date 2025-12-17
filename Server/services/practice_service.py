"""
练习服务
处理练习记录、统计等
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from database.models import PracticeRecord, PracticeSession, Question
from datetime import datetime, timedelta


class PracticeService:
    """练习服务类"""
    
    @staticmethod
    def create_practice_session(
        db: Session,
        user_id: int,
        subject_id: int,
        total_count: int,
        correct_count: int,
        wrong_count: int,
        accuracy: float,
        grade: str
    ) -> int:
        """
        创建练习会话记录
        :param db: 数据库会话
        :param user_id: 用户 ID
        :param subject_id: 科目 ID
        :param total_count: 总题数
        :param correct_count: 正确题数
        :param wrong_count: 错误题数
        :param accuracy: 正确率
        :param grade: 成绩等级
        :return: 会话 ID
        """
        session = PracticeSession(
            user_id=user_id,
            subject_id=subject_id,
            total_count=total_count,
            correct_count=correct_count,
            wrong_count=wrong_count,
            accuracy=str(accuracy),
            grade=grade
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session.id
    
    @staticmethod
    def create_practice_record(
        db: Session,
        session_id: int,
        user_id: int,
        subject_id: int,
        question_id: int,
        user_answer: str,
        is_correct: bool
    ) -> PracticeRecord:
        """
        创建练习记录
        :param db: 数据库会话
        :param session_id: 会话 ID
        :param user_id: 用户 ID
        :param subject_id: 科目 ID
        :param question_id: 题目 ID
        :param user_answer: 用户答案
        :param is_correct: 是否正确
        :return: PracticeRecord 实例
        """
        record = PracticeRecord(
            session_id=session_id,
            user_id=user_id,
            subject_id=subject_id,
            question_id=question_id,
            user_answer=user_answer,
            is_correct=1 if is_correct else 0
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return record
    
    @staticmethod
    def batch_create_records(
        db: Session,
        user_id: int,
        subject_id: int,
        answers: List[Dict[str, Any]]
    ) -> List[PracticeRecord]:
        """
        批量创建练习记录
        :param db: 数据库会话
        :param user_id: 用户 ID
        :param subject_id: 科目 ID
        :param answers: 答案列表，格式 [{"question_id": 1, "user_answer": "A", "is_correct": True}]
        :return: PracticeRecord 列表
        """
        records = []
        
        for ans in answers:
            record = PracticeService.create_practice_record(
                db=db,
                user_id=user_id,
                subject_id=subject_id,
                question_id=ans["question_id"],
                user_answer=ans["user_answer"],
                is_correct=ans["is_correct"]
            )
            records.append(record)
        
        return records
    
    @staticmethod
    def get_statistics(db: Session, user_id: int, days: Optional[int] = None) -> Dict[str, Any]:
        """
        获取练习统计数据
        :param db: 数据库会话
        :param user_id: 用户 ID
        :param days: 统计最近几天（None 表示全部）
        :return: 统计数据字典
        """
        query = db.query(PracticeRecord).filter(PracticeRecord.user_id == user_id)
        
        # 如果指定天数，添加时间过滤
        if days:
            start_date = datetime.now() - timedelta(days=days)
            query = query.filter(PracticeRecord.created_at >= start_date)
        
        records = query.all()
        
        total_count = len(records)
        correct_count = sum(1 for r in records if r.is_correct == 1)
        wrong_count = total_count - correct_count
        
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        
        # 计算等级
        grade = PracticeService._calculate_grade(accuracy)
        
        return {
            "total_count": total_count,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "accuracy": round(accuracy, 2),
            "grade": grade
        }
    
    @staticmethod
    def _calculate_grade(accuracy: float) -> str:
        """
        根据正确率计算等级
        :param accuracy: 正确率
        :return: 等级 A-F
        """
        if accuracy >= 90:
            return "A"
        elif accuracy >= 80:
            return "B"
        elif accuracy >= 70:
            return "C"
        elif accuracy >= 60:
            return "D"
        else:
            return "F"
    
    @staticmethod
    def get_today_statistics(db: Session, user_id: int) -> Dict[str, Any]:
        """
        获取今日统计
        :param db: 数据库会话
        :param user_id: 用户 ID
        :return: 今日统计数据
        """
        return PracticeService.get_statistics(db, user_id, days=1)
    
    @staticmethod
    def get_week_statistics(db: Session, user_id: int) -> Dict[str, Any]:
        """
        获取本周统计
        :param db: 数据库会话
        :param user_id: 用户 ID
        :return: 本周统计数据
        """
        return PracticeService.get_statistics(db, user_id, days=7)
    
    @staticmethod
    def get_all_statistics(db: Session, user_id: int) -> Dict[str, Any]:
        """
        获取全部统计
        :param db: 数据库会话
        :param user_id: 用户 ID
        :return: 全部统计数据
        """
        return PracticeService.get_statistics(db, user_id, days=None)
    
    @staticmethod
    def get_consecutive_days(db: Session, user_id: int) -> int:
        """
        获取连续学习天数
        :param db: 数据库会话
        :param user_id: 用户 ID
        :return: 连续天数
        """
        # 获取所有练习日期（去重）
        dates = db.query(
            func.date(PracticeRecord.created_at).label('practice_date')
        ).filter(
            PracticeRecord.user_id == user_id
        ).distinct().order_by(
            func.date(PracticeRecord.created_at).desc()
        ).all()
        
        if not dates:
            return 0
        
        # 检查今天是否有练习
        today = datetime.now().date()
        date_list = [d[0] for d in dates]
        
        if today not in date_list:
            return 0
        
        # 计算连续天数
        consecutive = 1
        current_date = today
        
        for i in range(1, len(date_list)):
            expected_date = current_date - timedelta(days=1)
            if date_list[i] == expected_date:
                consecutive += 1
                current_date = expected_date
            else:
                break
        
        return consecutive
    
    @staticmethod
    def check_answer(question: Question, user_answer: str) -> bool:
        """
        检查答案是否正确
        :param question: 题目对象
        :param user_answer: 用户答案
        :return: 是否正确
        """
        correct_answer = question.answer.strip()
        user_answer = user_answer.strip()
        
        # 多选题答案排序后比较
        if question.type.value == "multiple":
            if "," in user_answer:
                user_parts = sorted([a.strip() for a in user_answer.split(",")])
                correct_parts = sorted([a.strip() for a in correct_answer.split(",")])
                return user_parts == correct_parts
        
        return user_answer.upper() == correct_answer.upper()
