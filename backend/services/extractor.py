"""
PDF 内容提取服务
从学术论文 PDF 中提取关键部分（Abstract, Introduction, Conclusion）
用于横向串读视图
"""

import re
from typing import Dict, Optional
from PyPDF2 import PdfReader
import io


class PDFExtractor:
    """PDF 内容提取器"""

    # 常见的章节标题模式
    ABSTRACT_PATTERNS = [
        r'abstract',
        r'summary',
        r'摘要',
    ]

    INTRO_PATTERNS = [
        r'introduction',
        r'1\.\s*introduction',
        r'i\.\s*introduction',
        r'background',
        r'引言',
        r'绪论',
    ]

    CONCLUSION_PATTERNS = [
        r'conclusion',
        r'conclusions',
        r'discussion',
        r'conclusions?\s+and\s+discussion',
        r'summary\s+and\s+conclusion',
        r'concluding\s+remarks',
        r'结论',
        r'讨论',
    ]

    @staticmethod
    def extract_from_file(file_path: str) -> Dict[str, Optional[str]]:
        """
        从 PDF 文件提取内容

        Args:
            file_path: PDF 文件路径

        Returns:
            包含 abstract, introduction, conclusion 的字典
        """
        try:
            with open(file_path, 'rb') as file:
                return PDFExtractor.extract_from_bytes(file.read())
        except Exception as e:
            return {
                'abstract': None,
                'introduction': None,
                'conclusion': None,
                'error': str(e)
            }

    @staticmethod
    def extract_from_bytes(pdf_bytes: bytes) -> Dict[str, Optional[str]]:
        """
        从 PDF 字节流提取内容

        Args:
            pdf_bytes: PDF 文件的字节数据

        Returns:
            包含 abstract, introduction, conclusion 的字典
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)

            # 提取全文
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"

            # 清理文本
            full_text = PDFExtractor._clean_text(full_text)

            # 提取各个部分
            result = {
                'abstract': PDFExtractor._extract_abstract(full_text),
                'introduction': PDFExtractor._extract_introduction(full_text),
                'conclusion': PDFExtractor._extract_conclusion(full_text),
                'full_text': full_text[:50000]  # 限制全文长度
            }

            return result

        except Exception as e:
            return {
                'abstract': None,
                'introduction': None,
                'conclusion': None,
                'error': str(e)
            }

    @staticmethod
    def _clean_text(text: str) -> str:
        """清理文本，移除多余空白"""
        # 移除多余换行
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # 移除行内多余空格
        text = re.sub(r'[ \t]+', ' ', text)
        # 修复断行单词
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
        return text.strip()

    @staticmethod
    def _extract_abstract(text: str) -> Optional[str]:
        """提取摘要"""
        for pattern in PDFExtractor.ABSTRACT_PATTERNS:
            # 查找 Abstract 标题
            match = re.search(
                rf'\b{pattern}\b(.*?)(?:\n\s*\n|\b(?:introduction|keywords|1\.)\b)',
                text,
                re.IGNORECASE | re.DOTALL
            )
            if match:
                abstract = match.group(1).strip()
                # 如果摘要太短（<50字符）或太长（>3000字符），可能不准确
                if 50 < len(abstract) < 3000:
                    return abstract

        # 如果没找到，尝试提取前几段（可能是摘要）
        paragraphs = text.split('\n\n')
        for i, para in enumerate(paragraphs[:5]):
            # 跳过标题、作者等信息
            if len(para) > 100 and not re.search(r'^(title|authors?|affiliations?):', para, re.IGNORECASE):
                if 100 < len(para) < 3000:
                    return para

        return None

    @staticmethod
    def _extract_introduction(text: str) -> Optional[str]:
        """提取引言（前 3-5 段）"""
        for pattern in PDFExtractor.INTRO_PATTERNS:
            # 查找 Introduction 标题
            match = re.search(
                rf'\b{pattern}\b(.*?)(?:\n\s*\n.*?\n\s*\n.*?\n\s*\n.*?\b(?:\d+\.|\d+\s+[A-Z]|\bmethods?\b|\brelated\s+work\b)\b)',
                text,
                re.IGNORECASE | re.DOTALL
            )
            if match:
                intro = match.group(1).strip()
                # 限制长度，取前 2000 字符
                if len(intro) > 100:
                    return intro[:2000]

        # 如果没找到标题，尝试提取 Abstract 后的前几段
        abstract_end = 0
        for pattern in PDFExtractor.ABSTRACT_PATTERNS:
            match = re.search(rf'\b{pattern}\b.*?(?:\n\s*\n)', text, re.IGNORECASE | re.DOTALL)
            if match:
                abstract_end = match.end()
                break

        if abstract_end > 0:
            remaining_text = text[abstract_end:]
            paragraphs = remaining_text.split('\n\n')
            # 提取前 3-5 段
            intro_paragraphs = []
            for para in paragraphs[:5]:
                if len(para) > 50:
                    intro_paragraphs.append(para)
                if len('\n\n'.join(intro_paragraphs)) > 1500:
                    break

            if intro_paragraphs:
                return '\n\n'.join(intro_paragraphs)[:2000]

        return None

    @staticmethod
    def _extract_conclusion(text: str) -> Optional[str]:
        """提取结论（最后 3-5 段）"""
        for pattern in PDFExtractor.CONCLUSION_PATTERNS:
            # 查找 Conclusion 标题
            match = re.search(
                rf'\b{pattern}\b(.*?)(?:\breferences?\b|\backnowledgments?\b|\bappendix\b|$)',
                text,
                re.IGNORECASE | re.DOTALL
            )
            if match:
                conclusion = match.group(1).strip()
                # 限制长度，取前 2000 字符
                if len(conclusion) > 100:
                    return conclusion[:2000]

        # 如果没找到，尝试提取最后几段（在 References 之前）
        # 查找 References 位置
        ref_match = re.search(r'\breferences?\b', text, re.IGNORECASE)
        if ref_match:
            text_before_refs = text[:ref_match.start()]
            paragraphs = text_before_refs.split('\n\n')
            # 提取最后 3-5 段
            conclusion_paragraphs = []
            for para in reversed(paragraphs[-5:]):
                if len(para) > 50:
                    conclusion_paragraphs.insert(0, para)
                if len('\n\n'.join(conclusion_paragraphs)) > 1500:
                    break

            if conclusion_paragraphs:
                return '\n\n'.join(conclusion_paragraphs)[:2000]

        return None

    @staticmethod
    def extract_metadata(pdf_bytes: bytes) -> Dict[str, Optional[str]]:
        """
        提取 PDF 元数据

        Args:
            pdf_bytes: PDF 文件的字节数据

        Returns:
            包含标题、作者等元数据的字典
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)

            metadata = reader.metadata if reader.metadata else {}

            return {
                'title': metadata.get('/Title', None),
                'author': metadata.get('/Author', None),
                'subject': metadata.get('/Subject', None),
                'creator': metadata.get('/Creator', None),
                'producer': metadata.get('/Producer', None),
                'creation_date': metadata.get('/CreationDate', None),
            }

        except Exception as e:
            return {'error': str(e)}


class TextExtractor:
    """纯文本提取器（用于没有 PDF 的情况）"""

    @staticmethod
    def extract_sections(text: str) -> Dict[str, Optional[str]]:
        """
        从纯文本提取章节
        用于从 HTML、TXT 等格式提取内容
        """
        extractor = PDFExtractor()
        return {
            'abstract': extractor._extract_abstract(text),
            'introduction': extractor._extract_introduction(text),
            'conclusion': extractor._extract_conclusion(text),
        }
