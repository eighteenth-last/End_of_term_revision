"""
数学公式检测器
用于检测Word文档中的MathML公式节点数量，决定使用何种处理策略
"""
from docx import Document
from typing import Optional


class MathFormulaDetector:
    """数学公式检测器"""
    
    # 公式数量阈值，超过此值使用视觉模型
    FORMULA_THRESHOLD = 5
    
    @staticmethod
    def detect_formulas_in_docx(file_path: str) -> int:
        """
        检测Word文档中的MathML公式节点数量
        :param file_path: Word文档路径
        :return: 公式数量
        """
        try:
            doc = Document(file_path)
            formula_count = 0
            
            # 遍历所有段落，查找oMath节点
            for paragraph in doc.paragraphs:
                # 在段落的XML元素中查找所有oMath节点
                # oMath是Office Math的标记，表示数学公式
                for child in paragraph._element.iter():
                    # 检查标签名是否包含'oMath'
                    if 'oMath' in child.tag:
                        formula_count += 1
            
            return formula_count
        except Exception as e:
            print(f"[公式检测错误] 无法检测文档中的公式: {str(e)}")
            # 出错时返回0，使用文本处理方式
            return 0
    
    @staticmethod
    def should_use_vision_model(formula_count: int) -> bool:
        """
        判断是否应使用视觉模型
        :param formula_count: 公式数量
        :return: True=使用视觉模型, False=使用文本处理
        """
        return formula_count > MathFormulaDetector.FORMULA_THRESHOLD
    
    @staticmethod
    def get_processing_strategy(file_path: str) -> dict:
        """
        获取文档处理策略
        :param file_path: 文档路径
        :return: {
            'strategy': 'vision' | 'text',
            'formula_count': int,
            'reason': str
        }
        """
        # 检查文件扩展名
        if not file_path.lower().endswith(('.docx', '.doc')):
            return {
                'strategy': 'text',
                'formula_count': 0,
                'reason': '非Word文档，使用文本处理'
            }
        
        formula_count = MathFormulaDetector.detect_formulas_in_docx(file_path)
        use_vision = MathFormulaDetector.should_use_vision_model(formula_count)
        
        return {
            'strategy': 'vision' if use_vision else 'text',
            'formula_count': formula_count,
            'reason': f'检测到{formula_count}个公式，{"超过" if use_vision else "未超过"}阈值{MathFormulaDetector.FORMULA_THRESHOLD}个'
        }


def detect_formulas(file_path: str) -> int:
    """
    检测文档中的公式数量（便捷函数）
    :param file_path: 文档路径
    :return: 公式数量
    """
    return MathFormulaDetector.detect_formulas_in_docx(file_path)
