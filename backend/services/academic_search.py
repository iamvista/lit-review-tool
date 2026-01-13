"""
學術論文搜尋服務
Academic Search Service - Google Scholar, Crossref, arXiv 整合
"""

from typing import List, Dict, Optional
import re
from scholarly import scholarly
from habanero import Crossref
import arxiv
import requests


class AcademicSearchService:
    """學術論文搜尋服務"""

    def __init__(self):
        self.crossref = Crossref()

    def search_google_scholar(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        使用 Google Scholar 搜尋論文

        Args:
            query: 搜尋關鍵詞
            max_results: 最大結果數量

        Returns:
            論文列表
        """
        try:
            results = []
            search_query = scholarly.search_pubs(query)

            for i, pub in enumerate(search_query):
                if i >= max_results:
                    break

                try:
                    # 獲取論文詳細資訊
                    paper_info = {
                        'title': pub.get('bib', {}).get('title', ''),
                        'authors': pub.get('bib', {}).get('author', []),
                        'year': pub.get('bib', {}).get('pub_year'),
                        'journal': pub.get('bib', {}).get('venue', ''),
                        'abstract': pub.get('bib', {}).get('abstract', ''),
                        'citation_count': pub.get('num_citations', 0),
                        'url': pub.get('pub_url', ''),
                        'eprint_url': pub.get('eprint_url', ''),
                        'source': 'Google Scholar'
                    }

                    results.append(paper_info)
                except Exception as e:
                    print(f"解析單篇論文失敗: {e}")
                    continue

            return results

        except Exception as e:
            raise Exception(f"Google Scholar 搜尋失敗: {str(e)}")

    def search_by_doi(self, doi: str) -> Optional[Dict]:
        """
        通過 DOI 搜尋論文（使用 Crossref API）

        Args:
            doi: DOI 標識符

        Returns:
            論文資訊
        """
        try:
            # 清理 DOI（移除可能的 URL 前綴）
            clean_doi = self._extract_doi(doi)

            if not clean_doi:
                raise Exception("無效的 DOI 格式")

            # 查詢 Crossref
            work = self.crossref.works(ids=clean_doi)

            if not work or 'message' not in work:
                raise Exception("找不到該 DOI 對應的論文")

            data = work['message']

            # 解析作者
            authors = []
            if 'author' in data:
                for author in data['author']:
                    name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                    if name:
                        authors.append(name)

            # 解析年份
            year = None
            if 'published' in data:
                date_parts = data['published'].get('date-parts', [[]])[0]
                if date_parts:
                    year = date_parts[0]
            elif 'created' in data:
                date_parts = data['created'].get('date-parts', [[]])[0]
                if date_parts:
                    year = date_parts[0]

            # 解析期刊
            journal = ''
            if 'container-title' in data and data['container-title']:
                journal = data['container-title'][0]

            paper_info = {
                'title': data.get('title', [''])[0] if data.get('title') else '',
                'authors': authors,
                'year': year,
                'journal': journal,
                'doi': clean_doi,
                'url': data.get('URL', ''),
                'abstract': data.get('abstract', ''),
                'citation_count': data.get('is-referenced-by-count', 0),
                'source': 'Crossref'
            }

            return paper_info

        except Exception as e:
            raise Exception(f"DOI 查詢失敗: {str(e)}")

    def search_arxiv(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        搜尋 arXiv 論文

        Args:
            query: 搜尋關鍵詞或 arXiv ID
            max_results: 最大結果數量

        Returns:
            論文列表
        """
        try:
            results = []

            # 檢查是否是 arXiv ID
            if self._is_arxiv_id(query):
                # 直接通過 ID 獲取
                search = arxiv.Search(id_list=[query])
            else:
                # 關鍵詞搜尋
                search = arxiv.Search(
                    query=query,
                    max_results=max_results,
                    sort_by=arxiv.SortCriterion.Relevance
                )

            for paper in search.results():
                paper_info = {
                    'title': paper.title,
                    'authors': [author.name for author in paper.authors],
                    'year': paper.published.year,
                    'journal': 'arXiv',
                    'abstract': paper.summary,
                    'url': paper.entry_id,
                    'pdf_url': paper.pdf_url,
                    'arxiv_id': paper.get_short_id(),
                    'source': 'arXiv'
                }

                results.append(paper_info)

            return results

        except Exception as e:
            raise Exception(f"arXiv 搜尋失敗: {str(e)}")

    def search_by_url(self, url: str) -> Optional[Dict]:
        """
        智能 URL 解析 - 支援多種學術網站

        Args:
            url: 論文 URL

        Returns:
            論文資訊
        """
        try:
            # DOI URL (doi.org, dx.doi.org)
            if 'doi.org' in url:
                doi = self._extract_doi(url)
                if doi:
                    return self.search_by_doi(doi)

            # arXiv URL
            if 'arxiv.org' in url:
                arxiv_id = self._extract_arxiv_id(url)
                if arxiv_id:
                    results = self.search_arxiv(arxiv_id, max_results=1)
                    return results[0] if results else None

            # PubMed URL
            if 'pubmed.ncbi.nlm.nih.gov' in url or 'ncbi.nlm.nih.gov/pubmed' in url:
                return self._fetch_pubmed(url)

            # IEEE Xplore
            if 'ieeexplore.ieee.org' in url:
                return self._fetch_ieee(url)

            # ACM Digital Library
            if 'dl.acm.org' in url:
                return self._fetch_acm(url)

            # Nature、Science 等出版社（嘗試從頁面提取 DOI）
            return self._fetch_generic_publisher(url)

        except Exception as e:
            raise Exception(f"URL 解析失敗: {str(e)}")

    def search_by_title(self, title: str) -> Optional[Dict]:
        """
        通過標題搜尋論文（優先使用 Crossref）

        Args:
            title: 論文標題

        Returns:
            論文資訊
        """
        try:
            # 使用 Crossref 搜尋
            works = self.crossref.works(query=title, limit=1)

            if not works or 'message' not in works or 'items' not in works['message']:
                # 嘗試 Google Scholar
                results = self.search_google_scholar(title, max_results=1)
                return results[0] if results else None

            items = works['message']['items']
            if not items:
                return None

            data = items[0]

            # 解析作者
            authors = []
            if 'author' in data:
                for author in data['author']:
                    name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                    if name:
                        authors.append(name)

            # 解析年份
            year = None
            if 'published' in data:
                date_parts = data['published'].get('date-parts', [[]])[0]
                if date_parts:
                    year = date_parts[0]

            # 解析期刊
            journal = ''
            if 'container-title' in data and data['container-title']:
                journal = data['container-title'][0]

            paper_info = {
                'title': data.get('title', [''])[0] if data.get('title') else '',
                'authors': authors,
                'year': year,
                'journal': journal,
                'doi': data.get('DOI', ''),
                'url': data.get('URL', ''),
                'abstract': data.get('abstract', ''),
                'citation_count': data.get('is-referenced-by-count', 0),
                'source': 'Crossref'
            }

            return paper_info

        except Exception as e:
            raise Exception(f"標題搜尋失敗: {str(e)}")

    # ========== 輔助方法 ==========

    def _extract_doi(self, text: str) -> Optional[str]:
        """從文本中提取 DOI"""
        # DOI 格式：10.xxxx/xxxxx
        doi_pattern = r'10\.\d{4,}/[^\s]+'
        match = re.search(doi_pattern, text)
        return match.group(0) if match else None

    def _is_arxiv_id(self, text: str) -> bool:
        """檢查是否是 arXiv ID"""
        # arXiv ID 格式：YYMM.NNNNN 或 arch-ive/YYMMNNN
        arxiv_pattern = r'^\d{4}\.\d{4,5}(v\d+)?$'
        return bool(re.match(arxiv_pattern, text))

    def _extract_arxiv_id(self, url: str) -> Optional[str]:
        """從 URL 提取 arXiv ID"""
        # https://arxiv.org/abs/2012.12345
        # https://arxiv.org/pdf/2012.12345.pdf
        arxiv_pattern = r'(\d{4}\.\d{4,5})(v\d+)?'
        match = re.search(arxiv_pattern, url)
        return match.group(0) if match else None

    def _fetch_pubmed(self, url: str) -> Optional[Dict]:
        """獲取 PubMed 論文資訊"""
        # 提取 PMID
        pmid_pattern = r'/(\d+)'
        match = re.search(pmid_pattern, url)
        if not match:
            return None

        pmid = match.group(1)

        try:
            # 使用 PubMed E-utilities API
            api_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
            response = requests.get(api_url, timeout=10)
            data = response.json()

            if 'result' not in data or pmid not in data['result']:
                return None

            paper_data = data['result'][pmid]

            # 解析作者
            authors = []
            if 'authors' in paper_data:
                authors = [author['name'] for author in paper_data['authors']]

            paper_info = {
                'title': paper_data.get('title', ''),
                'authors': authors,
                'year': int(paper_data.get('pubdate', '').split()[0]) if paper_data.get('pubdate') else None,
                'journal': paper_data.get('fulljournalname', ''),
                'abstract': '',  # PubMed summary API 不包含摘要
                'url': url,
                'pubmed_id': pmid,
                'source': 'PubMed'
            }

            # 嘗試獲取 DOI
            if 'articleids' in paper_data:
                for id_obj in paper_data['articleids']:
                    if id_obj.get('idtype') == 'doi':
                        paper_info['doi'] = id_obj.get('value')
                        break

            return paper_info

        except Exception as e:
            print(f"PubMed 解析錯誤: {e}")
            return None

    def _fetch_ieee(self, url: str) -> Optional[Dict]:
        """獲取 IEEE Xplore 論文資訊"""
        # IEEE 通常需要 API key，這裡嘗試從頁面提取基本資訊
        # 實際應用中建議使用 IEEE API
        return self._fetch_generic_publisher(url)

    def _fetch_acm(self, url: str) -> Optional[Dict]:
        """獲取 ACM Digital Library 論文資訊"""
        # ACM 通常有 DOI，嘗試提取
        try:
            response = requests.get(url, timeout=10)
            doi = self._extract_doi(response.text)
            if doi:
                return self.search_by_doi(doi)
        except:
            pass
        return None

    def _fetch_generic_publisher(self, url: str) -> Optional[Dict]:
        """
        通用出版商頁面解析
        嘗試從頁面中提取 DOI，然後使用 Crossref 查詢
        """
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; LitReviewBot/1.0)'
            })

            # 嘗試提取 DOI
            doi = self._extract_doi(response.text)
            if doi:
                return self.search_by_doi(doi)

            return None

        except Exception as e:
            print(f"通用頁面解析錯誤: {e}")
            return None

    def generate_bibtex_from_paper(self, paper_info: Dict) -> str:
        """
        從論文資訊生成 BibTeX

        Args:
            paper_info: 論文資訊字典

        Returns:
            BibTeX 字符串
        """
        # 生成 cite key
        if paper_info.get('year') and paper_info.get('title'):
            first_word = paper_info['title'].split()[0].lower() if paper_info['title'].split() else 'paper'
            # 移除特殊字符
            first_word = re.sub(r'[^\w]', '', first_word)
            cite_key = f"{first_word}{paper_info['year']}"
        else:
            cite_key = "paper"

        bibtex = f"@article{{{cite_key},\n"
        bibtex += f"  title = {{{paper_info.get('title', '')}}},\n"

        if paper_info.get('authors'):
            authors_str = ' and '.join(paper_info['authors'])
            bibtex += f"  author = {{{authors_str}}},\n"

        if paper_info.get('year'):
            bibtex += f"  year = {{{paper_info['year']}}},\n"

        if paper_info.get('journal'):
            bibtex += f"  journal = {{{paper_info['journal']}}},\n"

        if paper_info.get('doi'):
            bibtex += f"  doi = {{{paper_info['doi']}}},\n"

        if paper_info.get('url'):
            bibtex += f"  url = {{{paper_info['url']}}},\n"

        if paper_info.get('abstract'):
            # 清理摘要中的換行符
            abstract = paper_info['abstract'].replace('\n', ' ').strip()
            bibtex += f"  abstract = {{{abstract}}},\n"

        bibtex += "}\n"

        return bibtex
