"""
AI 客户端 - 动态调用用户配置的 LLM
"""
import base64
from openai import OpenAI
from typing import Dict, Any, List, Optional


class AIClient:
    """AI 客户端，支持动态模型配置"""
    
    def __init__(self, base_url: str, api_key: str, model_name: str):
        """
        初始化 AI 客户端
        :param base_url: API 基础地址
        :param api_key: API 密钥
        :param model_name: 模型名称
        """
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model_name = model_name
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        调用聊天完成接口
        :param messages: 消息列表
        :param temperature: 温度参数
        :param max_tokens: 最大 token 数
        :param response_format: 响应格式，如 {"type": "json_object"}
        :return: 模型响应内容
        """
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def parse_text_to_questions(self, text: str, subject: str) -> str:
        """
        解析文本为题目 JSON
        :param text: 文本内容
        :param subject: 科目名称
        :return: JSON 字符串
        """
        from utils.Prompt import PARSE_TEXT_TO_QUESTIONS_PROMPT, SYSTEM_ROLE_PARSE_TEXT
        
        prompt = PARSE_TEXT_TO_QUESTIONS_PROMPT.format(text=text, subject=subject)
        
        messages = [
            {"role": "system", "content": SYSTEM_ROLE_PARSE_TEXT},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
    
    def parse_image_to_questions(self, image_text: str, subject: str) -> str:
        """
        解析图片 OCR 文本为题目 JSON
        :param image_text: OCR 提取的文本
        :param subject: 科目名称
        :return: JSON 字符串
        """
        from utils.Prompt import PARSE_IMAGE_TO_QUESTIONS_PROMPT, SYSTEM_ROLE_PARSE_IMAGE
        
        prompt = PARSE_IMAGE_TO_QUESTIONS_PROMPT.format(image_text=image_text, subject=subject)
        
        messages = [
            {"role": "system", "content": SYSTEM_ROLE_PARSE_IMAGE},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
    
    def parse_image_direct(self, image_path: str, subject: str) -> str:
        """
        直接使用视觉模型解析图片（不经过OCR）
        适用于支持多模态的模型如 GPT-4V、Qwen-VL 等
        :param image_path: 图片路径
        :param subject: 科目名称
        :return: JSON 字符串
        """
        from utils.Prompt import PARSE_IMAGE_DIRECT_PROMPT
        
        # 读取图片并编码为base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 获取图片格式
        ext = image_path.lower().split('.')[-1]
        mime_type = f"image/{ext if ext in ['png', 'jpeg', 'jpg', 'gif', 'webp'] else 'jpeg'}"
        
        prompt = PARSE_IMAGE_DIRECT_PROMPT.format(subject=subject)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        
        return self.chat_completion(
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
    
    def generate_analysis(self, question: str, answer: str, options: List[str] = None) -> str:
        """
        生成题目解析
        :param question: 题目内容
        :param answer: 正确答案
        :param options: 选项列表
        :return: 解析内容
        """
        from utils.Prompt import GENERATE_ANALYSIS_PROMPT, SYSTEM_ROLE_GENERATE_ANALYSIS
        
        options_text = "\n".join(options) if options else "无选项"
        
        prompt = GENERATE_ANALYSIS_PROMPT.format(
            question=question,
            options_text=options_text,
            answer=answer
        )
        
        messages = [
            {"role": "system", "content": SYSTEM_ROLE_GENERATE_ANALYSIS},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(messages=messages, temperature=0.7)


def get_ai_client(base_url: str, api_key: str, model_name: str) -> AIClient:
    """
    获取 AI 客户端实例
    :param base_url: API 基础地址
    :param api_key: API 密钥
    :param model_name: 模型名称
    :return: AIClient 实例
    """
    return AIClient(base_url, api_key, model_name)
