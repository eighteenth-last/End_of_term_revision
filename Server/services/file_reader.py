"""
文件读取服务
支持 PDF、Word、文本文件
"""
import os
from typing import Optional
import pdfplumber
from docx import Document
from docx.document import Document as DocxDocument
from docx.table import Table
from docx.text.paragraph import Paragraph


class FileReader:
    """文件读取器"""
    
    @staticmethod
    def read_txt(file_path: str) -> str:
        """
        读取文本文件
        :param file_path: 文件路径
        :return: 文件内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
    
    @staticmethod
    def read_pdf(file_path: str) -> str:
        """
        读取 PDF 文件
        :param file_path: 文件路径
        :return: 提取的文本内容
        """
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"PDF 读取失败: {str(e)}")
        
        return text.strip()
    
    @staticmethod
    def read_docx(file_path: str) -> str:
        """
        读取 Word 文档
        :param file_path: 文件路径
        :return: 提取的文本内容
        """
        try:
            doc = Document(file_path)
            parts = []
            if isinstance(doc, DocxDocument):
                body = doc.element.body
                for child in body.iterchildren():
                    if child.tag.endswith("}p"):
                        paragraph = Paragraph(child, doc)
                        if paragraph.text:
                            parts.append(paragraph.text)
                    elif child.tag.endswith("}tbl"):
                        table = Table(child, doc)
                        for row in table.rows:
                            cells_text = [cell.text.strip() for cell in row.cells]
                            line = "\t".join(cells_text).strip()
                            if line:
                                parts.append(line)
            text = "\n".join(parts)
            return text.strip()
        except Exception as e:
            raise ValueError(f"Word 文档读取失败: {str(e)}")
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """
        根据文件扩展名自动选择读取方法
        :param file_path: 文件路径
        :return: 文件内容
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return FileReader.read_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return FileReader.read_docx(file_path)
        elif ext in ['.txt', '.text']:
            return FileReader.read_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")


def read_file_content(file_path: str) -> str:
    """
    读取文件内容（统一接口）
    :param file_path: 文件路径
    :return: 文件内容
    """
    return FileReader.read_file(file_path)
