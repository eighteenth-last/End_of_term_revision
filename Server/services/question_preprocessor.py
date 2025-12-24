"""
题目预处理器
在AI处理前使用正则表达式提取题目结构（题号、选项、题型）
"""
import re
from typing import List, Dict, Any, Tuple


class QuestionPreprocessor:
    """题目预处理器"""
    
    @staticmethod
    def extract_questions_structure(text: str) -> List[Dict[str, Any]]:
        """
        从文本中提取题目结构
        :param text: 文本内容
        :return: 结构化题目列表 [{
            'raw_text': str,
            'question_number': str,
            'question_content': str,
            'detected_type': str,
            'options': List[str],
            'confidence': float
        }]
        """
        questions = []
        
        # 1. 按题号分割文本（支持多种题号格式）
        # 匹配: 1. 或 1、 或 1． 或 (1) 或 ①
        segments = re.split(r'(?m)^[\s]*(\d+|[①-⑳]|[（(]\d+[)）])[\.、．)]?\s*', text)
        
        # segments格式: ['前文', '题号1', '题目1内容', '题号2', '题目2内容', ...]
        i = 1
        while i < len(segments) - 1:
            q_num = segments[i].strip()
            q_text = segments[i + 1].strip()
            
            if not q_text:  # 跳过空题目
                i += 2
                continue
            
            # 2. 检测题型
            detected_type, confidence = QuestionPreprocessor._detect_type(q_text)
            
            # 3. 提取选项
            options = QuestionPreprocessor._extract_options(q_text)
            
            questions.append({
                'raw_text': f"{q_num}. {q_text}",
                'question_number': q_num,
                'question_content': q_text,
                'detected_type': detected_type,
                'options': options,
                'confidence': confidence
            })
            
            i += 2
        
        return questions
    
    @staticmethod
    def _detect_type(text: str) -> Tuple[str, float]:
        """
        检测题型并返回置信度
        :param text: 题目文本
        :return: (题型, 置信度)
        """
        
        # 规则1: 填空题检测（优先级最高）
        # 匹配: _____ 或 （  ） 或 ___ ___ 等
        fill_patterns = [
            r'_{3,}',  # 连续3个以上下划线
            r'（\s+）',  # 中文括号加空格
            r'\(\s+\)',  # 英文括号加空格
        ]
        for pattern in fill_patterns:
            if re.search(pattern, text):
                return ('fill', 0.95)
        
        # 规则2: 选择题检测（检测选项标记）
        # 需要至少匹配到2个选项才认定为选择题
        option_patterns = [
            (r'[A-D][\.、．]\s*.+', 'letter'),  # A. B. C. D.
            (r'[①②③④⑤⑥⑦⑧]\s*.+', 'circle'),  # ① ② ③ ④
            (r'[（(][1-4][)）]\s*.+', 'paren'),  # (1) (2) (3) (4)
        ]
        
        for pattern, ptype in option_patterns:
            matches = re.findall(pattern, text)
            if len(matches) >= 2:
                # 检查是否为多选题
                if re.search(r'多选|多项|选出所有|全部正确', text, re.IGNORECASE):
                    return ('multiple', 0.90)
                else:
                    return ('single', 0.90)
        
        # 规则3: 判断题检测
        # 3.1 包含"正确"、"错误"等关键词，且题干较短
        if re.search(r'(正确|错误|对|错|是否|T\/F|True\/False)', text) and len(text) < 100:
            return ('judge', 0.75)
        
        # 3.2 结尾是括号 ( ) 或 （ ）
        if re.search(r'[（(]\s*[)）]\s*$', text.strip()):
            return ('judge', 0.85)

        # 3.3 纯标题 "判断题"
        if text.strip() in ['判断题', '判断']:
             return ('judge', 0.9)
        
        # 规则4: 大题检测（主观题）
        # 包含特定关键词且题干较长
        major_keywords = [
            '请回答', '请简述', '请说明', '请证明', '请计算',
            '请推导', '请分析', '请论述', '请阐述',
            '试述', '试证明', '试计算', '试推导',
            '简述', '说明理由', '解答', '求解'
        ]
        
        if any(kw in text for kw in major_keywords) and len(text) > 50:
            return ('major', 0.70)
        
        # 无法确定,交给AI
        return ('unknown', 0.0)
    
    @staticmethod
    def _extract_options(text: str) -> List[str]:
        """
        提取选项内容
        :param text: 题目文本
        :return: 选项列表
        """
        options = []
        
        # 尝试提取字母选项 A. B. C. D.
        letter_pattern = r'([A-D])[\.、．]\s*(.+?)(?=[A-D][\.、．]|$)'
        letter_matches = re.findall(letter_pattern, text, re.DOTALL)
        if len(letter_matches) >= 2:
            return [f"{letter}. {content.strip()}" for letter, content in letter_matches]
        
        # 尝试提取圆圈数字 ① ② ③ ④
        circle_pattern = r'([①②③④⑤⑥⑦⑧])\s*(.+?)(?=[①②③④⑤⑥⑦⑧]|$)'
        circle_matches = re.findall(circle_pattern, text, re.DOTALL)
        if len(circle_matches) >= 2:
            return [f"{num} {content.strip()}" for num, content in circle_matches]
        
        # 尝试提取括号数字 (1) (2) (3) (4)
        paren_pattern = r'([（(][1-4][)）])\s*(.+?)(?=[（(][1-4][)）]|$)'
        paren_matches = re.findall(paren_pattern, text, re.DOTALL)
        if len(paren_matches) >= 2:
            return [f"{num} {content.strip()}" for num, content in paren_matches]
        
        return []
    
    @staticmethod
    def calculate_average_confidence(questions: List[Dict[str, Any]]) -> float:
        """
        计算所有题目的平均置信度
        :param questions: 题目列表
        :return: 平均置信度
        """
        if not questions:
            return 0.0
        
        total_confidence = sum(q['confidence'] for q in questions)
        return total_confidence / len(questions)
    
    @staticmethod
    def format_for_ai(questions: List[Dict[str, Any]]) -> str:
        """
        将预处理结果格式化为AI可读的文本
        :param questions: 题目列表
        :return: 格式化文本
        """
        lines = []
        for q in questions:
            lines.append(f"题号: {q['question_number']}")
            lines.append(f"检测题型: {q['detected_type']} (置信度: {q['confidence']})")
            lines.append(f"题干: {q['question_content'][:200]}...")
            if q['options']:
                lines.append(f"选项: {len(q['options'])}个")
                for opt in q['options'][:3]:  # 只显示前3个
                    lines.append(f"  - {opt[:50]}...")
            lines.append("---")
        
        return "\n".join(lines)


def preprocess_questions(text: str) -> List[Dict[str, Any]]:
    """
    预处理题目（便捷函数）
    :param text: 文本内容
    :return: 结构化题目列表
    """
    preprocessor = QuestionPreprocessor()
    return preprocessor.extract_questions_structure(text)
