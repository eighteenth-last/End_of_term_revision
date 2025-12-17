"""
JSON Schema 验证器
用于验证 AI 解析结果的格式
"""
import json
from typing import Dict, List, Any
from jsonschema import validate, ValidationError


# 题目 JSON Schema
QUESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "subject": {"type": "string"},
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["single", "multiple", "judge", "fill"]
                    },
                    "question": {"type": "string"},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "answer": {"type": "string"},
                    "analysis": {"type": "string"}
                },
                "required": ["type", "question", "answer", "analysis"]
            }
        }
    },
    "required": ["subject", "questions"]
}


def validate_question_json(data: Dict[str, Any]) -> bool:
    """
    验证题目 JSON 格式是否正确
    :param data: 待验证的数据
    :return: 是否验证通过
    """
    try:
        validate(instance=data, schema=QUESTION_SCHEMA)
        return True
    except ValidationError as e:
        print(f"JSON 验证失败: {e.message}")
        return False


def parse_and_validate(json_str: str) -> Dict[str, Any]:
    """
    解析并验证 JSON 字符串
    :param json_str: JSON 字符串
    :return: 解析后的字典
    :raises: ValueError 如果格式不正确
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {str(e)}")
    
    if not validate_question_json(data):
        raise ValueError("题目 JSON 格式验证失败")
    
    return data


def normalize_question_data(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    标准化题目数据
    :param question: 题目数据
    :return: 标准化后的题目数据
    """
    # 确保判断题有正确的选项
    if question["type"] == "judge":
        if not question.get("options") or len(question["options"]) == 0:
            question["options"] = ["对", "错"]
    
    # 确保填空题的选项为空列表
    if question["type"] == "fill":
        if not question.get("options"):
            question["options"] = []
    
    # 标准化答案格式
    answer = question["answer"].strip()
    
    # 多选题答案排序（例如：B,A,C -> A,B,C）
    if question["type"] == "multiple":
        if "," in answer:
            answer_list = [a.strip() for a in answer.split(",")]
            answer_list.sort()
            answer = ",".join(answer_list)
    
    question["answer"] = answer
    
    return question
