"""
AI 解析服务
整合文件读取、AI 视觉模型调用
"""
import json
import re
from typing import Dict, Any, List
from services.file_reader import FileReader
from utils.ai_client import AIClient
from utils.schema_validator import parse_and_validate, normalize_question_data


def split_text_for_questions(text: str) -> List[str]:
    text = text.replace("\r\n", "\n")
    pattern = re.compile(r"(?m)^\s*\d+[\.．、]")
    positions = [m.start() for m in pattern.finditer(text)]
    if len(positions) >= 2:
        segments: List[str] = []
        for i, start in enumerate(positions):
            end = positions[i + 1] if i + 1 < len(positions) else len(text)
            segment = text[start:end].strip()
            if segment:
                segments.append(segment)
        return segments
    max_len = 800
    segments = []
    i = 0
    n = len(text)
    while i < n:
        j = min(i + max_len, n)
        newline_pos = text.rfind("\n", i + 200, j)
        if newline_pos != -1 and newline_pos > i:
            j = newline_pos
        segment = text[i:j].strip()
        if segment:
            segments.append(segment)
        i = j
    return segments


class AIParser:
    """AI 解析器"""
    
    def __init__(self, ai_client: AIClient):
        """
        初始化 AI 解析器
        :param ai_client: AI 客户端实例
        """
        self.ai_client = ai_client
        self.file_reader = FileReader()
    
    def parse_file_to_questions(self, file_path: str, subject: str) -> Dict[str, Any]:
        """
        解析文件为题目数据
        :param file_path: 文件路径
        :param subject: 科目名称
        :return: 解析后的题目数据
        """
        text_content = self.file_reader.read_file(file_path)
        text_length = len(text_content)
        print(f"[文件解析] 读取文件完成: 路径={file_path}, 科目={subject}, 长度={text_length} 字符")
        if text_length > 0:
            preview = text_content[:500].replace("\n", " ")
            print(f"[文件解析预览] {preview}...")
        
        if not text_content.strip():
            raise ValueError("文件内容为空")
        
        json_result = self.ai_client.parse_text_to_questions(text_content, subject)
        print(f"[AI解析-文件] JSON长度: {len(json_result)} 字符")
        print(f"[AI解析-文件预览] {json_result[:500]}...")
        
        parsed_data = parse_and_validate(json_result)
        questions = parsed_data.get("questions") or []
        print(f"[AI解析-文件] questions数量: {len(questions)}")
        
        if not questions:
            print("[AI解析警告-文件] AI首次解析未识别到题目，开始自动分段解析")
            print(f"[AI解析-文件完整返回] {json_result}")
            segments = split_text_for_questions(text_content)
            print(f"[自动分段] 分段数量: {len(segments)}")
            merged_questions: List[Dict[str, Any]] = []
            for idx, segment in enumerate(segments):
                print(f"[自动分段] 第{idx + 1}段长度: {len(segment)} 字符")
                segment_json = self.ai_client.parse_text_to_questions(segment, subject)
                print(f"[AI解析-分段{idx + 1}] JSON长度: {len(segment_json)} 字符")
                print(f"[AI解析-分段{idx + 1}预览] {segment_json[:500]}...")
                segment_data = parse_and_validate(segment_json)
                segment_questions = segment_data.get("questions") or []
                print(f"[AI解析-分段{idx + 1}] questions数量: {len(segment_questions)}")
                for q in segment_questions:
                    normalize_question_data(q)
                    merged_questions.append(q)
            print(f"[自动分段] 汇总questions数量: {len(merged_questions)}")
            if not merged_questions:
                return {"subject": subject, "questions": []}
            return {"subject": subject, "questions": merged_questions}
        
        for question in questions:
            normalize_question_data(question)
        
        return parsed_data
    
    def parse_image_to_questions(self, image_path: str, subject: str) -> Dict[str, Any]:
        """
        使用视觉模型直接解析图片为题目数据
        :param image_path: 图片路径
        :param subject: 科目名称
        :return: 解析后的题目数据
        """
        print(f"[视觉模型] 直接解析图片: 路径={image_path}, 科目={subject}")
        json_result = self.ai_client.parse_image_direct(image_path, subject)
        
        print(f"[AI解析-图片] JSON长度: {len(json_result)} 字符")
        print(f"[AI解析-图片预览] {json_result[:500]}...")
        
        parsed_data = parse_and_validate(json_result)
        questions = parsed_data.get("questions") or []
        print(f"[AI解析-图片] questions数量: {len(questions)}")
        if not questions:
            print("[AI解析警告-图片] AI返回的questions数组为空")
            print(f"[AI解析-图片完整返回] {json_result}")
        
        for question in questions:
            normalize_question_data(question)
        
        return parsed_data
    
    def parse_text_to_questions(self, text: str, subject: str) -> Dict[str, Any]:
        """
        直接解析文本为题目数据
        :param text: 文本内容
        :param subject: 科目名称
        :return: 解析后的题目数据
        """
        text_length = len(text)
        print(f"[文本解析] 收到文本: 科目={subject}, 长度={text_length} 字符")
        if text_length > 0:
            preview = text[:500].replace("\n", " ")
            print(f"[文本解析预览] {preview}...")
        
        if not text.strip():
            raise ValueError("文本内容为空")
        
        json_result = self.ai_client.parse_text_to_questions(text, subject)
        print(f"[AI解析-文本] JSON长度: {len(json_result)} 字符")
        print(f"[AI解析-文本预览] {json_result[:500]}...")
        
        parsed_data = parse_and_validate(json_result)
        questions = parsed_data.get("questions") or []
        print(f"[AI解析-文本] questions数量: {len(questions)}")
        if not questions:
            print("[AI解析警告-文本] AI返回的questions数组为空")
            print(f"[AI解析-文本完整返回] {json_result}")
        
        for question in questions:
            normalize_question_data(question)
        
        return parsed_data


def create_ai_parser(base_url: str, api_key: str, model_name: str) -> AIParser:
    """
    创建 AI 解析器实例
    :param base_url: API 基础地址
    :param api_key: API 密钥
    :param model_name: 模型名称
    :return: AIParser 实例
    """
    ai_client = AIClient(base_url, api_key, model_name)
    return AIParser(ai_client)
