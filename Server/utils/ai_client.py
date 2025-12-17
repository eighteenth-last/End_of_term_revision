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
        prompt = f"""你是一个专业的题目解析专家。请将以下文本解析成标准的题目格式。

文本内容：
{text}

科目：{subject}

请严格按照以下 JSON 格式输出（必须是有效的 JSON）：
{{
  "subject": "{subject}",
  "questions": [
    {{
      "type": "single/multiple/judge/fill",
      "question": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "正确答案（单选填A/B/C/D，多选填A,B,C，判断填对/错，填空填具体答案）",
      "analysis": "题目解析"
    }}
  ]
}}

注意事项：
1. type 只能是：single（单选）、multiple（多选）、judge（判断）、fill（填空）
2. 判断题的 options 为 ["对", "错"]
3. 填空题的 options 可以为空数组 []
4. 如果文本中没有答案，请根据题目内容生成正确答案
5. 如果文本中没有解析，请根据题目内容生成详细解析
6. 必须返回有效的 JSON 格式，不要包含任何其他文字
"""
        
        messages = [
            {"role": "system", "content": "你是一个专业的题目解析助手，擅长将文本转换为结构化的题目数据。"},
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
        prompt = f"""你是一个专业的题目识别专家。以下是从图片中 OCR 提取的文本，可能包含题目、选项等信息。

OCR 文本：
{image_text}

科目：{subject}

请识别并解析出题目，严格按照以下 JSON 格式输出（必须是有效的 JSON）：
{{
  "subject": "{subject}",
  "questions": [
    {{
      "type": "single/multiple/judge/fill",
      "question": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "正确答案",
      "analysis": "题目解析"
    }}
  ]
}}

注意事项：
1. type 只能是：single（单选）、multiple（多选）、judge（判断）、fill（填空）
2. 判断题的 options 为 ["对", "错"]
3. 填空题的 options 可以为空数组 []
4. 如果图片中没有标注答案，请根据题目内容生成正确答案
5. 必须生成详细的题目解析
6. 必须返回有效的 JSON 格式，不要包含任何其他文字
"""
        
        messages = [
            {"role": "system", "content": "你是一个专业的图片题目识别助手，擅长从 OCR 文本中提取并结构化题目数据。"},
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
        # 读取图片并编码为base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 获取图片格式
        ext = image_path.lower().split('.')[-1]
        mime_type = f"image/{ext if ext in ['png', 'jpeg', 'jpg', 'gif', 'webp'] else 'jpeg'}"
        
        prompt = f"""你是一个专业的题目识别专家。请仔细观察图片中的题目内容，识别并解析出所有题目。

科目：{subject}

请严格按照以下 JSON 格式输出（必须是有效的 JSON）：
{{
  "subject": "{subject}",
  "questions": [
    {{
      "type": "single/multiple/judge/fill",
      "question": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "正确答案（单选填A/B/C/D，多选填A,B,C，判断填对/错，填空填具体答案）",
      "analysis": "题目解析"
    }}
  ]
}}

注意事项：
1. 仔细识别题目类型：single（单选）、multiple（多选）、judge（判断）、fill（填空）
2. 判断题的 options 为 ["对", "错"]
3. 填空题的 options 可以为空数组 []
4. 如果图片中包含答案，请使用图片中的答案；如果没有答案，请根据题目内容生成正确答案
5. 必须生成详细的题目解析，说明为什么这个答案是正确的
6. 必须返回有效的 JSON 格式，不要包含任何其他文字
7. 确保题目内容、选项、答案完整准确，不要出现乱码或遗漏
"""
        
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
        options_text = "\n".join(options) if options else "无选项"
        
        prompt = f"""请为以下题目生成详细的解析说明。

题目：{question}

选项：
{options_text}

正确答案：{answer}

请生成详细的解析，说明为什么这个答案是正确的，以及解题思路。
"""
        
        messages = [
            {"role": "system", "content": "你是一个专业的教育专家，擅长为题目提供清晰易懂的解析。"},
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
