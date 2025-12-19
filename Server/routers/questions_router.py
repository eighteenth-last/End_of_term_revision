"""
题目路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database.db import get_default_db
from database.models import Question
from services.question_service import QuestionService
import json

router = APIRouter(prefix="/api/questions", tags=["题目管理"])


class QuestionResponse(BaseModel):
    """题目响应"""
    id: int
    subject_id: int
    user_id: int
    type: str
    question: str
    options: List[str]
    answer: str
    analysis: str
    created_at: str


class QuestionCreate(BaseModel):
    """创建题目请求"""
    user_id: int
    subject_id: int
    type: str
    question: str
    options: List[str]
    answer: str
    analysis: str


@router.post("/", response_model=QuestionResponse)
def create_question(question: QuestionCreate, db: Session = Depends(get_default_db)):
    """创建单个题目"""
    db_question = QuestionService.create_question(
        db=db,
        user_id=question.user_id,
        subject_id=question.subject_id,
        question_type=question.type,
        question=question.question,
        options=question.options,
        answer=question.answer,
        analysis=question.analysis
    )
    
    return _format_question_response(db_question)


@router.get("/", response_model=List[QuestionResponse])
def get_questions(
    user_id: int,
    subject_id: int,
    question_type: Optional[str] = None,
    limit: Optional[int] = None,
    db: Session = Depends(get_default_db)
):
    """获取题目列表"""
    questions = QuestionService.get_questions_by_subject(
        db=db,
        user_id=user_id,
        subject_id=subject_id,
        question_type=question_type,
        limit=limit
    )
    
    return [_format_question_response(q) for q in questions]


@router.get("/types/{subject_id}")
def get_question_types(
    subject_id: int,
    user_id: int,
    db: Session = Depends(get_default_db)
):
    """获取科目下的所有题目类型"""
    types = QuestionService.get_question_types_by_subject(db, user_id, subject_id)
    return {"types": types}


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, user_id: int, db: Session = Depends(get_default_db)):
    """获取单个题目"""
    question = QuestionService.get_question_by_id(db, question_id, user_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在或无权访问")
    
    return _format_question_response(question)


@router.delete("/{question_id}")
def delete_question(question_id: int, user_id: int, db: Session = Depends(get_default_db)):
    """删除题目"""
    success = QuestionService.delete_question(db, question_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="题目不存在或无权删除")
    
    return {"message": "题目删除成功"}


def _format_question_response(question: Question) -> QuestionResponse:
    """格式化题目响应"""
    options = []
    if question.options_json:
        try:
            options = json.loads(question.options_json)
        except:
            options = []
    
    return QuestionResponse(
        id=question.id,
        subject_id=question.subject_id,
        user_id=question.user_id,
        type=question.type.value,
        question=question.question,
        options=options,
        answer=question.answer,
        analysis=question.analysis,
        created_at=question.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )
