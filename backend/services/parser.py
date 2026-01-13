"""
文獻解析服務
Literature Parser Service - BibTeX, DOI, PDF
"""

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
import requests
import re
from typing import Dict, List, Optional


class BibTeXParser:
    """BibTeX 解析器"""

    @staticmethod
    def parse_bibtex_file(file_content: str) -> List[Dict]:
        """
        解析 BibTeX 文件內容

        Args:
            file_content: BibTeX 文件的字符串內容

        Returns:
            解析後的論文列表
        """
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode

        try:
            bib_database = bibtexparser.loads(file_content, parser=parser)
            papers = []

            for entry in bib_database.entries:
                paper = BibTeXParser._parse_entry(entry)
                papers.append(paper)

            return papers
        except Exception as e:
            raise ValueError(f"BibTeX 解析失敗: {str(e)}")

    @staticmethod
    def _parse_entry(entry: Dict) -> Dict:
        """解析單個 BibTeX 條目"""

        # 提取作者
        authors = BibTeXParser._parse_authors(entry.get('author', ''))

        # 提取年份
        year = BibTeXParser._extract_year(entry.get('year', ''))

        # 構建論文資料
        paper = {
            'title': entry.get('title', '').strip('{}'),
            'year': year,
            'authors': authors,
            'journal': entry.get('journal', '') or entry.get('booktitle', ''),
            'volume': entry.get('volume', ''),
            'issue': entry.get('number', '') or entry.get('issue', ''),
            'pages': entry.get('pages', ''),
            'doi': entry.get('doi', ''),
            'url': entry.get('url', ''),
            'abstract': entry.get('abstract', '').strip('{}'),
            'bibtex': bibtexparser.dumps(bibtexparser.bibdatabase.BibDatabase()).replace('', f"@{entry.get('ENTRYTYPE', 'article')}{{{entry.get('ID', '')},\n" + '\n'.join([f"  {k} = {{{v}}}," for k, v in entry.items() if k not in ['ENTRYTYPE', 'ID']]) + "\n}"),
            'reference_type': entry.get('ENTRYTYPE', 'article'),
            'original_source': 'bibtex'
        }

        return paper

    @staticmethod
    def _parse_authors(author_string: str) -> List[Dict]:
        """
        解析作者字符串

        Examples:
            "John Doe and Jane Smith" -> [{"first": "John", "last": "Doe"}, ...]
            "Doe, J. and Smith, J." -> [{"first": "J.", "last": "Doe"}, ...]
        """
        if not author_string:
            return []

        authors = []
        # 分割作者（by 'and'）
        author_list = re.split(r'\s+and\s+', author_string, flags=re.IGNORECASE)

        for author in author_list:
            author = author.strip().strip('{}')

            # 嘗試解析 "Last, First" 格式
            if ',' in author:
                parts = author.split(',', 1)
                last = parts[0].strip()
                first = parts[1].strip() if len(parts) > 1 else ''
            else:
                # 假設 "First Last" 格式
                parts = author.rsplit(' ', 1)
                if len(parts) == 2:
                    first, last = parts
                else:
                    first, last = '', parts[0]

            authors.append({
                'first_name': first,
                'last_name': last,
                'full_name': f"{first} {last}".strip()
            })

        return authors

    @staticmethod
    def _extract_year(year_string: str) -> Optional[int]:
        """提取年份"""
        if not year_string:
            return None

        # 提取數字
        match = re.search(r'\d{4}', year_string)
        if match:
            try:
                return int(match.group())
            except ValueError:
                return None
        return None


class DOIResolver:
    """DOI 解析器 - 使用 Crossref API"""

    CROSSREF_API = "https://api.crossref.org/works/"

    @staticmethod
    def resolve_doi(doi: str) -> Optional[Dict]:
        """
        通過 DOI 獲取論文資訊

        Args:
            doi: DOI 標識符

        Returns:
            論文資料字典，失敗返回 None
        """
        if not doi:
            return None

        # 清理 DOI
        doi = doi.strip().replace('https://doi.org/', '').replace('http://doi.org/', '')

        try:
            response = requests.get(
                f"{DOIResolver.CROSSREF_API}{doi}",
                headers={'User-Agent': 'LitReviewTool/1.0 (mailto:contact@litreview.com)'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return DOIResolver._parse_crossref_response(data['message'])
            else:
                return None

        except Exception as e:
            print(f"DOI 解析錯誤: {str(e)}")
            return None

    @staticmethod
    def _parse_crossref_response(data: Dict) -> Dict:
        """解析 Crossref API 響應"""

        # 提取作者
        authors = []
        if 'author' in data:
            for author in data['author']:
                authors.append({
                    'first_name': author.get('given', ''),
                    'last_name': author.get('family', ''),
                    'full_name': f"{author.get('given', '')} {author.get('family', '')}".strip()
                })

        # 提取年份
        year = None
        if 'published-print' in data:
            year = data['published-print']['date-parts'][0][0]
        elif 'published-online' in data:
            year = data['published-online']['date-parts'][0][0]

        # 提取期刊名稱
        journal = ''
        if 'container-title' in data and data['container-title']:
            journal = data['container-title'][0]

        paper = {
            'title': data.get('title', [''])[0],
            'authors': authors,
            'year': year,
            'journal': journal,
            'volume': data.get('volume', ''),
            'issue': data.get('issue', ''),
            'pages': data.get('page', ''),
            'doi': data.get('DOI', ''),
            'url': data.get('URL', ''),
            'abstract': data.get('abstract', ''),
            'citation_count': data.get('is-referenced-by-count', 0),
            'reference_type': data.get('type', 'article'),
            'original_source': 'doi'
        }

        return paper


class CitationCounter:
    """引用數統計（Google Scholar 備選）"""

    @staticmethod
    def get_citation_count(title: str, authors: List[Dict]) -> int:
        """
        獲取論文引用數
        注意：Google Scholar 沒有官方 API，這裡僅作為接口預留
        實際實現可能需要使用 scholarly 庫或其他服務
        """
        # TODO: 實現 Google Scholar 查詢
        # 由於 Google Scholar 沒有官方 API，暫時返回 0
        return 0
