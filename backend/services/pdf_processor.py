"""
PDF 處理服務
PDF Processing Service - 提取論文資訊和內容
"""

import re
import os
from typing import Dict, Optional, List
import PyPDF2
import pdfplumber
import requests


class PDFProcessor:
    """PDF 文件處理器"""

    def __init__(self):
        self.crossref_api = "https://api.crossref.org/works/"

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        從 PDF 提取全文
        """
        try:
            # 優先使用 pdfplumber（對中文支援較好）
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"pdfplumber 提取失敗，嘗試 PyPDF2: {e}")
            # 降級到 PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except Exception as e2:
                print(f"PyPDF2 提取也失敗: {e2}")
                return ""

    def identify_doi(self, text: str) -> Optional[str]:
        """
        從 PDF 文字中識別 DOI
        """
        # DOI 通常格式為 10.xxxx/xxxxx
        doi_patterns = [
            r'10\.\d{4,9}/[-._;()/:A-Z0-9]+',
            r'doi:\s*(10\.\d{4,9}/[-._;()/:A-Z0-9]+)',
            r'DOI:\s*(10\.\d{4,9}/[-._;()/:A-Z0-9]+)',
        ]

        for pattern in doi_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                doi = match.group(1) if 'doi' in pattern.lower() else match.group(0)
                doi = doi.replace('doi:', '').replace('DOI:', '').strip()
                return doi

        return None

    def identify_arxiv_id(self, text: str) -> Optional[str]:
        """
        識別 arXiv ID
        """
        # arXiv 格式：arXiv:1234.5678 或 arXiv:1234.5678v1
        patterns = [
            r'arXiv:\s*(\d{4}\.\d{4,5}(?:v\d+)?)',
            r'arxiv\.org/abs/(\d{4}\.\d{4,5})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def fetch_metadata_from_doi(self, doi: str) -> Optional[Dict]:
        """
        透過 DOI 從 CrossRef API 獲取 metadata
        """
        try:
            response = requests.get(
                f"{self.crossref_api}{doi}",
                headers={'User-Agent': 'LitReviewTool/1.0 (mailto:research@example.com)'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()['message']

                # 提取作者
                authors = []
                for author in data.get('author', []):
                    name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                    if name:
                        authors.append(name)

                # 提取年份
                published = data.get('published-print') or data.get('published-online') or {}
                year = published.get('date-parts', [[None]])[0][0] if published else None

                return {
                    'title': data.get('title', [''])[0],
                    'authors': authors,
                    'year': year,
                    'journal': data.get('container-title', [''])[0],
                    'doi': doi,
                    'url': f"https://doi.org/{doi}",
                    'abstract': data.get('abstract', ''),
                    'extraction_method': 'doi'
                }
        except Exception as e:
            print(f"從 CrossRef 獲取 metadata 失敗: {e}")

        return None

    def extract_metadata_from_text(self, text: str) -> Dict:
        """
        從 PDF 文字中直接提取 metadata（當沒有 DOI 時）
        """
        lines = text.split('\n')

        # 嘗試提取標題（通常在第一頁前幾行）
        title = self._extract_title(lines[:20])

        # 嘗試提取作者
        authors = self._extract_authors(lines[:30])

        # 嘗試提取年份
        year = self._extract_year(text[:2000])

        return {
            'title': title,
            'authors': authors,
            'year': year,
            'extraction_method': 'text_parsing'
        }

    def _extract_title(self, first_lines: List[str]) -> str:
        """
        提取標題（簡單啟發式）
        標題通常是最前面且較長的一行
        """
        for line in first_lines:
            line = line.strip()
            # 標題通常 20-200 字元
            if 20 <= len(line) <= 200:
                # 排除常見的非標題行
                if not any(x in line.lower() for x in ['arxiv', 'abstract', 'published', 'copyright', 'ieee', 'acm']):
                    return line

        return "未識別標題"

    def _extract_authors(self, first_lines: List[str]) -> List[str]:
        """
        提取作者列表
        """
        authors = []

        # 尋找作者部分（通常在標題後）
        for line in first_lines:
            line = line.strip()
            # 作者行通常包含逗號或 "and"
            if ',' in line or ' and ' in line.lower():
                # 簡單分割作者名
                if ',' in line:
                    names = line.split(',')
                else:
                    names = re.split(r'\s+and\s+', line, flags=re.IGNORECASE)

                for name in names:
                    name = name.strip()
                    # 過濾掉非作者的行
                    if 5 <= len(name) <= 50 and not any(x in name.lower() for x in ['university', 'department', 'email', 'abstract']):
                        authors.append(name)

                if authors:
                    break

        return authors[:10]  # 最多返回 10 位作者

    def _extract_year(self, text: str) -> Optional[int]:
        """
        提取發表年份
        """
        # 尋找 4 位數年份（1990-2030）
        years = re.findall(r'\b(19\d{2}|20[0-3]\d)\b', text)

        if years:
            # 返回最合理的年份（通常是較新的）
            years = [int(y) for y in years if 1990 <= int(y) <= 2030]
            if years:
                return max(years)

        return None

    def extract_sections(self, text: str) -> Dict:
        """
        提取論文的不同部分（摘要、引言、結論）
        """
        return {
            'abstract': self._extract_abstract(text),
            'introduction': self._extract_introduction(text),
            'conclusion': self._extract_conclusion(text)
        }

    def _extract_abstract(self, text: str) -> str:
        """
        提取摘要
        """
        # 尋找 Abstract 關鍵字
        patterns = [
            r'Abstract\s*\n(.*?)(?=\n\n|\nIntroduction|\n1\.|\nKeywords)',
            r'ABSTRACT\s*\n(.*?)(?=\n\n|\nINTRODUCTION|\n1\.)',
            r'摘\s*要\s*\n(.*?)(?=\n\n|關鍵詞|引言)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                abstract = match.group(1).strip()
                # 限制摘要長度 100-1000 字元
                if 100 <= len(abstract) <= 1000:
                    return abstract

        return ""

    def _extract_introduction(self, text: str) -> str:
        """
        提取引言部分（前 3-5 段或前 1000 字）
        """
        # 尋找 Introduction 關鍵字
        patterns = [
            r'(?:1\.\s*)?Introduction\s*\n(.*?)(?=\n\n(?:2\.|Method|Approach))',
            r'(?:1\.\s*)?INTRODUCTION\s*\n(.*?)(?=\n\n(?:2\.|METHOD))',
            r'(?:一、)?引\s*言\s*\n(.*?)(?=\n\n(?:二、|方法))',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                intro = match.group(1).strip()
                # 限制為前 1500 字元
                return intro[:1500]

        return ""

    def _extract_conclusion(self, text: str) -> str:
        """
        提取結論部分
        """
        # 尋找 Conclusion 關鍵字（通常在論文末尾）
        patterns = [
            r'(?:\d+\.\s*)?Conclusion[s]?\s*\n(.*?)(?=\n\n(?:References|Acknowledgment)|\Z)',
            r'(?:\d+\.\s*)?Discussion\s*\n(.*?)(?=\n\n(?:References|Conclusion)|\Z)',
            r'(?:\d+\.\s*)?CONCLUSION[S]?\s*\n(.*?)(?=\n\nREFERENCES|\Z)',
            r'(?:六、)?結\s*論\s*\n(.*?)(?=\n\n參考文獻|\Z)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                conclusion = match.group(1).strip()
                return conclusion[:1500]  # 限制長度

        return ""

    def process_pdf(self, pdf_path: str) -> Dict:
        """
        完整處理 PDF：提取文字 → 識別 DOI → 獲取 metadata → 提取章節
        """
        result = {
            'success': False,
            'error': None,
            'extraction_method': None,
            'metadata': {},
            'sections': {}
        }

        # 1. 提取文字
        text = self.extract_text_from_pdf(pdf_path)
        if not text or len(text) < 100:
            result['error'] = '無法從 PDF 提取文字內容'
            return result

        # 2. 嘗試識別 DOI
        doi = self.identify_doi(text)
        if doi:
            print(f"識別到 DOI: {doi}")
            metadata = self.fetch_metadata_from_doi(doi)
            if metadata:
                result['metadata'] = metadata
                result['extraction_method'] = 'doi'
                result['success'] = True

        # 3. 如果沒有 DOI，從文字提取
        if not result['success']:
            print("未找到 DOI，嘗試從文字提取 metadata")
            result['metadata'] = self.extract_metadata_from_text(text)
            result['extraction_method'] = 'text_parsing'
            result['success'] = True

        # 4. 提取論文章節
        sections = self.extract_sections(text)
        result['sections'] = sections

        # 5. 添加原始文字（用於 AI 分析）
        result['full_text_preview'] = text[:2000]  # 前 2000 字元預覽

        return result
