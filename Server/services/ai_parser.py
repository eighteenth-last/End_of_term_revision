"""
AI 解析服务
整合文件读取、AI 视觉模型调用
"""
import json
from typing import Dict, Any, List
from services.file_reader import FileReader
from utils.ai_client import AIClient
from utils.schema_validator import parse_and_validate, normalize_question_data


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
        # 读取文件内容
        text_content = self.file_reader.read_file(file_path)
        
        if not text_content.strip():
            raise ValueError("文件内容为空")
        
        # 调用 AI 解析
        json_result = self.ai_client.parse_text_to_questions(text_content, subject)
        
        # 验证并解析 JSON
        parsed_data = parse_and_validate(json_result)
        
        # 标准化题目数据
        for question in parsed_data["questions"]:
            normalize_question_data(question)
        
        return parsed_data
    
    def parse_image_to_questions(self, image_path: str, subject: str) -> Dict[str, Any]:
        """
        使用视觉模型直接解析图片为题目数据
        :param image_path: 图片路径
        :param subject: 科目名称
        :return: 解析后的题目数据
        """
        print(f"[视觉模型] 直接解析图片")
        json_result = self.ai_client.parse_image_direct(image_path, subject)
        
        print(f"[AI返回] JSON长度: {len(json_result)} 字符")
        print(f"[AI返回预览] {json_result[:500]}...")
        
        # 验证并解析 JSON
        parsed_data = parse_and_validate(json_result)
        
        if not parsed_data.get("questions"):
            print(f"[AI解析警告] AI返回的questions数组为空")
            print(f"[完整AI返回] {json_result}")
        
        # 标准化题目数据
        for question in parsed_data["questions"]:
            normalize_question_data(question)
        
        return parsed_data
    
    def parse_text_to_questions(self, text: str, subject: str) -> Dict[str, Any]:
        """
        直接解析文本为题目数据
        :param text: 文本内容
        :param subject: 科目名称
        :return: 解析后的题目数据
        """
        if not text.strip():
            raise ValueError("文本内容为空")
        
        # 调用 AI 解析
        json_result = self.ai_client.parse_text_to_questions(text, subject)
        
        # 验证并解析 JSON
        parsed_data = parse_and_validate(json_result)
        
        # 标准化题目数据
        for question in parsed_data["questions"]:
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
