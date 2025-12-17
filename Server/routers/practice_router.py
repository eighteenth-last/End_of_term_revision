"""
练习路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from database.db import get_default_db
from services.question_service import QuestionService
from services.practice_service import PracticeService
from services.error_service import ErrorService
import json

router = APIRouter(prefix="/api/practice", tags=["练习"])


class PracticeRequest(BaseModel):
    """练习请求"""
    user_id: int
    subject_id: int
    question_counts: Dict[str, int]  # {"single": 10, "multiple": 5, ...}


class QuestionItem(BaseModel):
    """题目项"""
    id: int
    type: str
    question: str
    options: List[str]


class PracticeResponse(BaseModel):
    """练习响应"""
    questions: List[QuestionItem]


class AnswerItem(BaseModel):
    """答题项"""
    question_id: int
    user_answer: str


class SubmitAnswersRequest(BaseModel):
    """提交答案请求"""
    user_id: int
    subject_id: int
    answers: List[AnswerItem]


class SubmitAnswersResponse(BaseModel):
    """提交答案响应"""
    total: int
    correct: int
    wrong: int
    accuracy: float
    grade: str
    results: List[Dict]


class StatisticsResponse(BaseModel):
    """统计响应"""
    total_count: int
    correct_count: int
    wrong_count: int
    accuracy: float
    grade: str


class HomeStatisticsResponse(BaseModel):
    """首页统计响应"""
    today: StatisticsResponse
    week: StatisticsResponse
    all: StatisticsResponse
    consecutive_days: int


@router.post("/start", response_model=PracticeResponse)
def start_practice(request: PracticeRequest, db: Session = Depends(get_default_db)):
    """
    开始练习（随机抽题）
    """
    # 验证至少选择一种题型
    if not request.question_counts or sum(request.question_counts.values()) == 0:
        raise HTTPException(status_code=400, detail="请至少选择一种题型")
    
    # 随机抽题
    questions = QuestionService.get_random_questions(
        db=db,
        user_id=request.user_id,
        subject_id=request.subject_id,
        question_counts=request.question_counts
    )
    
    if not questions:
        raise HTTPException(status_code=404, detail="没有找到符合条件的题目")
    
    # 格式化题目（不返回答案和解析）
    question_items = []
    for q in questions:
        options = []
        if q.options_json:
            try:
                options = json.loads(q.options_json)
            except:
                options = []
        
        question_items.append(QuestionItem(
            id=q.id,
            type=q.type.value,
            question=q.question,
            options=options
        ))
    
    return PracticeResponse(questions=question_items)


@router.post("/submit", response_model=SubmitAnswersResponse)
def submit_answers(request: SubmitAnswersRequest, db: Session = Depends(get_default_db)):
    """
    提交答案
    """
    results = []
    correct_count = 0
    wrong_count = 0
    error_question_ids = []
    
    # 先计算结果
    for answer_item in request.answers:
        # 获取题目
        question = QuestionService.get_question_by_id(db, answer_item.question_id)
        
        if not question:
            continue
        
        # 检查答案
        is_correct = PracticeService.check_answer(question, answer_item.user_answer)
        
        if is_correct:
            correct_count += 1
        else:
            wrong_count += 1
            error_question_ids.append(answer_item.question_id)
    
    # 计算统计数据
    total = len(request.answers)
    accuracy = (correct_count / total * 100) if total > 0 else 0
    
    # 计算成绩等级
    if accuracy >= 90:
        grade = 'A'
    elif accuracy >= 80:
        grade = 'B'
    elif accuracy >= 70:
        grade = 'C'
    elif accuracy >= 60:
        grade = 'D'
    else:
        grade = 'F'
    
    # 创建练习会话记录
    session_id = PracticeService.create_practice_session(
        db=db,
        user_id=request.user_id,
        subject_id=request.subject_id,
        total_count=total,
        correct_count=correct_count,
        wrong_count=wrong_count,
        accuracy=round(accuracy, 2),
        grade=grade
    )
    
    # 创建每道题的练习记录
    for answer_item in request.answers:
        question = QuestionService.get_question_by_id(db, answer_item.question_id)
        if not question:
            continue
        
        is_correct = PracticeService.check_answer(question, answer_item.user_answer)
        
        PracticeService.create_practice_record(
            db=db,
            session_id=session_id,
            user_id=request.user_id,
            subject_id=request.subject_id,
            question_id=answer_item.question_id,
            user_answer=answer_item.user_answer,
            is_correct=is_correct
        )
        
        # 格式化结果
        options = []
        if question.options_json:
            try:
                options = json.loads(question.options_json)
            except:
                options = []
        
        results.append({
            "question_id": question.id,
            "type": question.type.value,
            "question": question.question,
            "options": options,
            "user_answer": answer_item.user_answer,
            "correct_answer": question.answer,
            "is_correct": is_correct,
            "analysis": question.analysis
        })
    
    # 批量添加错题
    if error_question_ids:
        ErrorService.batch_add_errors(
            db=db,
            user_id=request.user_id,
            subject_id=request.subject_id,
            question_ids=error_question_ids
        )
    
    return SubmitAnswersResponse(
        total=total,
        correct=correct_count,
        wrong=wrong_count,
        accuracy=round(accuracy, 2),
        grade=grade,
        results=results
    )


@router.get("/statistics/today", response_model=StatisticsResponse)
def get_today_statistics(user_id: int, db: Session = Depends(get_default_db)):
    """获取今日统计"""
    stats = PracticeService.get_today_statistics(db, user_id)
    return StatisticsResponse(**stats)


@router.get("/statistics/week", response_model=StatisticsResponse)
def get_week_statistics(user_id: int, db: Session = Depends(get_default_db)):
    """获取本周统计"""
    stats = PracticeService.get_week_statistics(db, user_id)
    return StatisticsResponse(**stats)


@router.get("/statistics/all", response_model=StatisticsResponse)
def get_all_statistics(user_id: int, db: Session = Depends(get_default_db)):
    """获取全部统计"""
    stats = PracticeService.get_all_statistics(db, user_id)
    return StatisticsResponse(**stats)


@router.get("/statistics/home", response_model=HomeStatisticsResponse)
def get_home_statistics(user_id: int, db: Session = Depends(get_default_db)):
    """获取首页统计数据"""
    today = PracticeService.get_today_statistics(db, user_id)
    week = PracticeService.get_week_statistics(db, user_id)
    all_stats = PracticeService.get_all_statistics(db, user_id)
    consecutive = PracticeService.get_consecutive_days(db, user_id)
    
    return HomeStatisticsResponse(
        today=StatisticsResponse(**today),
        week=StatisticsResponse(**week),
        all=StatisticsResponse(**all_stats),
        consecutive_days=consecutive
    )


@router.get("/history")
def get_practice_history(
    user_id: int, 
    subject_id: Optional[int] = None,
    limit: Optional[int] = 50,
    db: Session = Depends(get_default_db)
):
    """获取练习历史记录"""
    from database.models import PracticeSession, Subject
    
    # 构建查询
    query = db.query(
        PracticeSession.id,
        PracticeSession.created_at,
        PracticeSession.total_count,
        PracticeSession.correct_count,
        PracticeSession.wrong_count,
        PracticeSession.accuracy,
        PracticeSession.grade,
        Subject.name.label('subject_name')
    ).join(
        Subject, PracticeSession.subject_id == Subject.id
    ).filter(
        PracticeSession.user_id == user_id
    )
    
    # 如果指定科目，添加过滤
    if subject_id:
        query = query.filter(PracticeSession.subject_id == subject_id)
    
    # 按时间倒序
    query = query.order_by(PracticeSession.created_at.desc())
    
    # 限制返回数量
    if limit:
        query = query.limit(limit)
    
    results = query.all()
    
    # 格式化结果
    records = []
    for row in results:
        records.append({
            "session_id": row[0],
            "practice_date": row[1].strftime("%Y-%m-%d %H:%M:%S") if row[1] else "",
            "total": row[2],
            "correct": row[3],
            "wrong": row[4],
            "accuracy": float(row[5]),
            "grade": row[6],
            "subject_name": row[7] or "未知科目"
        })
    
    return {"records": records}


@router.get("/session/{session_id}/details")
def get_session_details(session_id: int, db: Session = Depends(get_default_db)):
    """获取练习会话的详细题目记录"""
    from database.models import PracticeRecord, Question
    
    # 查询该会话的所有答题记录
    records = db.query(
        PracticeRecord,
        Question
    ).join(
        Question, PracticeRecord.question_id == Question.id
    ).filter(
        PracticeRecord.session_id == session_id
    ).all()
    
    # 格式化结果
    details = []
    for record, question in records:
        options = []
        if question.options_json:
            try:
                options = json.loads(question.options_json)
            except:
                options = []
        
        details.append({
            "question_id": question.id,
            "type": question.type.value,
            "question": question.question,
            "options": options,
            "user_answer": record.user_answer,
            "correct_answer": question.answer,
            "is_correct": record.is_correct == 1,
            "analysis": question.analysis
        })
    
    return {"details": details}
