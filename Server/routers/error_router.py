"""
错题集路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from database.db import get_default_db
from services.error_service import ErrorService

router = APIRouter(prefix="/api/errors", tags=["错题集"])


class ErrorQuestionResponse(BaseModel):
    """错题响应"""
    error_id: int
    question_id: int
    subject_id: int
    type: str
    question: str
    options: List
    answer: str
    analysis: str
    wrong_count: int
    last_wrong_at: str


class ErrorPracticeRequest(BaseModel):
    """错题练习请求"""
    user_id: int
    subject_id: int
    question_counts: Dict[str, int]


class QuestionItem(BaseModel):
    """题目项"""
    id: int
    type: str
    question: str
    options: List[str]


class ErrorPracticeResponse(BaseModel):
    """错题练习响应"""
    questions: List[QuestionItem]


@router.get("/", response_model=List[ErrorQuestionResponse])
def get_error_questions(
    user_id: int,
    subject_id: Optional[int] = None,
    limit: Optional[int] = None,
    db: Session = Depends(get_default_db)
):
    """
    获取错题列表
    """
    errors = ErrorService.get_error_questions(
        db=db,
        user_id=user_id,
        subject_id=subject_id,
        limit=limit
    )
    
    return [ErrorQuestionResponse(**error) for error in errors]


@router.get("/count")
def get_error_count(
    user_id: int,
    subject_id: Optional[int] = None,
    db: Session = Depends(get_default_db)
):
    """
    获取错题数量
    """
    count = ErrorService.get_error_count(db, user_id, subject_id)
    return {"count": count}


@router.get("/types/{subject_id}")
def get_error_types(
    subject_id: int,
    user_id: int,
    db: Session = Depends(get_default_db)
):
    """
    获取科目下错题的题目类型
    """
    types = ErrorService.get_error_types_by_subject(db, user_id, subject_id)
    return {"types": types}


@router.post("/practice", response_model=ErrorPracticeResponse)
def start_error_practice(
    request: ErrorPracticeRequest,
    db: Session = Depends(get_default_db)
):
    """
    开始错题练习（随机抽取错题）
    """
    # 验证至少选择一种题型
    if not request.question_counts or sum(request.question_counts.values()) == 0:
        raise HTTPException(status_code=400, detail="请至少选择一种题型")
    
    # 随机抽取错题
    questions = ErrorService.get_random_error_questions(
        db=db,
        user_id=request.user_id,
        subject_id=request.subject_id,
        question_counts=request.question_counts
    )
    
    if not questions:
        raise HTTPException(status_code=404, detail="没有找到符合条件的错题")
    
    # 格式化题目（不返回答案和解析）
    import json
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
    
    return ErrorPracticeResponse(questions=question_items)


@router.delete("/{error_id}")
def remove_error(error_id: int, user_id: int, db: Session = Depends(get_default_db)):
    """
    移除错题记录
    """
    success = ErrorService.remove_error(db, error_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="错题记录不存在或无权删除")
    
    return {"message": "错题移除成功"}
