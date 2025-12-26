"""
AI 解析服务
整合文件读取、AI 视觉模型调用
"""
import json
import re
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        解析文件为题目数据（重构版：集成公式检测和预处理器）
        :param file_path: 文件路径
        :param subject: 科目名称
        :return: 解析后的题目数据
        """
        from services.math_formula_detector import MathFormulaDetector
        from services.question_preprocessor import QuestionPreprocessor
        
        # 1. 检测文档中的公式数量（仅Word文档）
        if file_path.lower().endswith(('.docx', '.doc')):
            formula_count = MathFormulaDetector.detect_formulas_in_docx(file_path)
            use_vision = MathFormulaDetector.should_use_vision_model(formula_count)
            print(f"[公式检测] 检测到{formula_count}个公式，{'使用视觉模型' if use_vision else '使用文本处理'}")
            
            if use_vision:
                # 公式较多，使用视觉模型（需要将Word转为图片）
                # TODO: 实现Word转图片功能
                print(f"[警告] 检测到{formula_count}个公式，建议使用图片导入功能以获得更好的识别效果")
                # 当前仍使用文本处理，但会提示用户
        
        # 2. 读取文件内容
        text_content = self.file_reader.read_file(file_path)
        text_length = len(text_content)
        print(f"[文件解析] 读取文件完成: 路径={file_path}, 科目={subject}, 长度={text_length} 字符")
        
        if text_length > 0:
            preview = text_content[:500].replace("\n", " ")
            print(f"[文件解析预览] {preview}...")
        
        if not text_content.strip():
            raise ValueError("文件内容为空")
        
        # 3. 预处理：提取题目结构
        preprocessor = QuestionPreprocessor()
        structured_questions = preprocessor.extract_questions_structure(text_content)
        avg_confidence = preprocessor.calculate_average_confidence(structured_questions)
        
        print(f"[预处理] 识别{len(structured_questions)}道题目，平均置信度: {avg_confidence:.2f}")
        
        # 4. 根据置信度选择处理策略
        if len(structured_questions) > 0 and avg_confidence >= 0.7:
            # 置信度高，使用结构化AI处理
            print(f"[AI解析-结构化] 使用预处理结果 + AI补充")
            json_result = self.ai_client.parse_structured_questions(structured_questions, subject)
        else:
            # 置信度低或未识别到题目，降级到全文本AI处理
            print(f"[AI解析-全文本] 置信度不足或未识别题目，使用全文本AI处理")
            json_result = self.ai_client.parse_text_to_questions(text_content, subject)
        
        print(f"[AI解析-文件] JSON长度: {len(json_result)} 字符")
        print(f"[AI解析-文件预览] {json_result[:500]}...")
        
        # 5. 解析和验证
        parsed_data = parse_and_validate(json_result)
        questions = parsed_data.get("questions") or []
        print(f"[AI解析-文件] questions数量: {len(questions)}")
        
        # 6. 如果仍然没有识别到题目，尝试分段处理
        if not questions:
            print("[AI解析警告-文件] AI首次解析未识别到题目，开始自动分段解析")
            print(f"[AI解析-文件完整返回] {json_result}")
            segments = split_text_for_questions(text_content)
            print(f"[自动分段] 分段数量: {len(segments)}")
            merged_questions: List[Dict[str, Any]] = []

            # 定义任务函数
            def process_segment(idx, segment):
                print(f"[自动分段] 开始处理第{idx + 1}段，长度: {len(segment)} 字符")
                try:
                    segment_json = self.ai_client.parse_text_to_questions(segment, subject)
                    print(f"[AI解析-分段{idx + 1}] 完成，JSON长度: {len(segment_json)} 字符")
                    
                    segment_data = parse_and_validate(segment_json)
                    segment_questions = segment_data.get("questions") or []
                    print(f"[AI解析-分段{idx + 1}] 解析出 {len(segment_questions)} 道题目")
                    
                    for q in segment_questions:
                        normalize_question_data(q)
                    return segment_questions
                except Exception as e:
                    print(f"[AI解析警告-分段{idx + 1}] 解析失败: {str(e)}")
                    return []

            # 使用线程池并发执行
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_idx = {executor.submit(process_segment, i, seg): i for i, seg in enumerate(segments)}
                
                # 按顺序收集结果（虽然是并发执行，但我们希望保持题目顺序吗？
                # 如果题目顺序重要，我们应该按原始索引排序结果。
                # 这里我们先收集所有结果，然后按索引排序合并。
                results = []
                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        qs = future.result()
                        results.append((idx, qs))
                    except Exception as exc:
                        print(f"[自动分段] 第{idx + 1}段发生未捕获异常: {exc}")
            
            # 按索引排序并合并
            results.sort(key=lambda x: x[0])
            for _, qs in results:
                merged_questions.extend(qs)
            
            print(f"[自动分段] 汇总questions数量: {len(merged_questions)}")
            # 只要有解析出题目，就返回结果，不要因为部分失败而全盘否定
            if not merged_questions:
                # 如果所有分段都失败了，才返回空
                return {"subject": subject, "questions": []}
            return {"subject": subject, "questions": merged_questions}
        
        # 7. 标准化题目数据
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
            print("[AI解析警告-图片] AI返回的questions数组为空，尝试 OCR + 文本解析模式")
            print(f"[AI解析-图片完整返回] {json_result}")
            
            # 降级策略：先提取文本，再解析文本
            try:
                extracted_text = self.ai_client.extract_text_from_image(image_path)
                print(f"[AI解析-OCR] 提取文本长度: {len(extracted_text)} 字符")
                if len(extracted_text) > 10:
                    print(f"[AI解析-OCR] 提取文本预览: {extracted_text[:200]}...")
                    # 调用文本解析流程（复用已有的分段和预处理逻辑）
                    return self.parse_text_to_questions(extracted_text, subject)
                else:
                    print("[AI解析-OCR] 提取的文本过短，无法解析")
            except Exception as e:
                print(f"[AI解析-OCR] 提取文本失败: {e}")

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
        from services.question_preprocessor import QuestionPreprocessor

        text_length = len(text)
        print(f"[文本解析] 收到文本: 科目={subject}, 长度={text_length} 字符")
        if text_length > 0:
            preview = text[:500].replace("\n", " ")
            print(f"[文本解析预览] {preview}...")
        
        if not text.strip():
            raise ValueError("文本内容为空")
        
        # 1. 预处理：提取题目结构
        preprocessor = QuestionPreprocessor()
        structured_questions = preprocessor.extract_questions_structure(text)
        avg_confidence = preprocessor.calculate_average_confidence(structured_questions)
        
        print(f"[预处理] 识别{len(structured_questions)}道题目，平均置信度: {avg_confidence:.2f}")
        
        # 2. 根据置信度选择处理策略
        if len(structured_questions) > 0 and avg_confidence >= 0.7:
            # 置信度高，使用结构化AI处理
            print(f"[AI解析-结构化] 使用预处理结果 + AI补充")
            json_result = self.ai_client.parse_structured_questions(structured_questions, subject)
        else:
            # 置信度低或未识别到题目，降级到全文本AI处理
            print(f"[AI解析-全文本] 置信度不足或未识别题目，使用全文本AI处理")
            json_result = self.ai_client.parse_text_to_questions(text, subject)
        
        print(f"[AI解析-文本] JSON长度: {len(json_result)} 字符")
        print(f"[AI解析-文本预览] {json_result[:500]}...")
        
        # 3. 解析和验证
        parsed_data = parse_and_validate(json_result)
        questions = parsed_data.get("questions") or []
        print(f"[AI解析-文本] questions数量: {len(questions)}")
        
        # 4. 如果仍然没有识别到题目，尝试分段处理
        if not questions:
            print("[AI解析警告-文本] AI首次解析未识别到题目，开始自动分段解析")
            print(f"[AI解析-文本完整返回] {json_result}")
            segments = split_text_for_questions(text)
            print(f"[自动分段] 分段数量: {len(segments)}")
            merged_questions: List[Dict[str, Any]] = []
            
            # 定义任务函数
            def process_segment(idx, segment):
                print(f"[自动分段] 开始处理第{idx + 1}段，长度: {len(segment)} 字符")
                try:
                    segment_json = self.ai_client.parse_text_to_questions(segment, subject)
                    print(f"[AI解析-分段{idx + 1}] 完成，JSON长度: {len(segment_json)} 字符")
                    
                    segment_data = parse_and_validate(segment_json)
                    segment_questions = segment_data.get("questions") or []
                    print(f"[AI解析-分段{idx + 1}] 解析出 {len(segment_questions)} 道题目")
                    
                    for q in segment_questions:
                        normalize_question_data(q)
                    return segment_questions
                except Exception as e:
                    print(f"[AI解析警告-分段{idx + 1}] 解析失败: {str(e)}")
                    return []

            # 使用线程池并发执行
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_idx = {executor.submit(process_segment, i, seg): i for i, seg in enumerate(segments)}
                results = []
                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        qs = future.result()
                        results.append((idx, qs))
                    except Exception as exc:
                        print(f"[自动分段] 第{idx + 1}段发生未捕获异常: {exc}")
            
            # 按索引排序并合并
            results.sort(key=lambda x: x[0])
            for _, qs in results:
                merged_questions.extend(qs)
            
            print(f"[自动分段] 汇总questions数量: {len(merged_questions)}")
            # 只要有解析出题目，就返回结果，不要因为部分失败而全盘否定
            if not merged_questions:
                # 如果所有分段都失败了，才返回空
                return {"subject": subject, "questions": []}
            return {"subject": subject, "questions": merged_questions}
        
        # 5. 标准化题目数据
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
