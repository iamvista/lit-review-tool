"""
AI 輔助研究缺口識別服務
AI-Powered Research Gap Analysis Service
使用 Anthropic Claude API 進行深度文獻分析
"""

import anthropic
from typing import List, Dict, Optional
import json


class AIAnalysisService:
    """AI 分析服務"""

    def __init__(self, api_key: str):
        """初始化 AI 服務"""
        if not api_key:
            raise ValueError("Anthropic API Key 未設置")

        self.client = anthropic.Anthropic(api_key=api_key)
        # 使用 Claude 3 Haiku (快速且經濟實惠)
        self.model = "claude-3-haiku-20240307"  # Claude 3 Haiku

    def analyze_research_gap(self, papers: List[Dict], project_info: Dict) -> Dict:
        """
        完整的研究缺口分析

        Args:
            papers: 論文列表，每篇論文包含 title, authors, year, abstract 等
            project_info: 專案資訊，包含 name, description, domain

        Returns:
            分析結果字典，包含：
            - development_history: 領域發展史
            - core_problems: 核心問題列表
            - method_evolution: 方法演進
            - research_gaps: 研究缺口
            - recommendations: 研究方向建議
        """

        # 準備論文數據
        papers_text = self._prepare_papers_text(papers)

        # 生成分析提示
        prompt = self._generate_analysis_prompt(papers_text, project_info)

        # 調用 Claude API
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,  # Haiku 最大支援 4096 tokens
                temperature=0.3,  # 較低的溫度以獲得更一致的分析
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # 解析響應
            response_text = message.content[0].text
            analysis_result = self._parse_analysis_result(response_text)

            return {
                "success": True,
                "analysis": analysis_result,
                "papers_analyzed": len(papers),
                "model_used": self.model
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _prepare_papers_text(self, papers: List[Dict]) -> str:
        """準備論文文本用於分析"""

        papers_by_year = {}
        for paper in papers:
            year = paper.get('year', '未知')
            if year not in papers_by_year:
                papers_by_year[year] = []
            papers_by_year[year].append(paper)

        # 按年份排序
        sorted_years = sorted(papers_by_year.keys())

        text_parts = []
        for year in sorted_years:
            text_parts.append(f"\n## {year} 年\n")

            for paper in papers_by_year[year]:
                title = paper.get('title', '無標題')
                authors = paper.get('authors', [])
                authors_str = ', '.join([a.get('name', a) if isinstance(a, dict) else str(a) for a in authors[:3]])
                if len(authors) > 3:
                    authors_str += f" 等 {len(authors)} 人"

                abstract = paper.get('abstract', '無摘要')
                journal = paper.get('journal', '')

                text_parts.append(f"### 論文：{title}\n")
                text_parts.append(f"**作者**: {authors_str}\n")
                if journal:
                    text_parts.append(f"**期刊**: {journal}\n")
                text_parts.append(f"**摘要**: {abstract}\n")
                text_parts.append("\n---\n")

        return '\n'.join(text_parts)

    def _generate_analysis_prompt(self, papers_text: str, project_info: Dict) -> str:
        """生成分析提示"""

        project_name = project_info.get('name', '未命名專案')
        project_description = project_info.get('description', '')
        domain = project_info.get('domain', '')

        prompt = f"""你是一位資深的學術研究顧問，擁有 20 年的研究經驗，專門幫助博碩士生進行深度文獻回顧和研究缺口識別。

# 專案資訊
- **研究主題**：{project_name}
- **研究領域**：{domain}
- **研究問題**：{project_description}

# 論文集（按時間排序）
{papers_text}

# 分析任務

請對這些論文進行**深度且批判性的分析**，提供詳細、具體且有洞察力的研究缺口識別。請按照以下結構提供分析：


## 一、領域發展史深度剖析

**字數要求**：400-500 字

請詳細分析：

**起源時刻**

這個研究問題最早在哪一年、由誰、在什麼背景下提出？當時的動機是什麼？

**發展階段**

識別至少 3 個關鍵發展階段，每個階段的時間範圍、代表性研究、主要貢獻。

**轉折點**

哪些研究成果導致了範式轉移？為什麼？具體引用論文和年份。

**重要人物**

識別 5-8 位關鍵研究者，說明他們的主要貢獻和影響力。

**研究趨勢**

從早期到現在，研究焦點如何演變？


## 二、核心研究問題深入分析

**數量要求**：4-6 個核心問題

對每個核心問題提供**詳細分析**：

**問題本質**

用 2-3 句話清晰描述問題。

**歷史脈絡**

首次提出時間、提出者、當時的研究背景。

**演變過程**

這個問題的定義或理解如何隨時間改變？

**當前狀態**

- 已解決：哪些研究成果解決了？如何解決的？
- 部分解決：哪些方面已解決？哪些仍未解決？為什麼？
- 未解決：為什麼這個問題難以解決？主要障礙是什麼？

**重要性論證**

為什麼這個問題值得持續研究？對領域和實務的影響是什麼？

**相關爭議**

不同學者對這個問題有什麼不同看法？


## 三、方法演進批判性分析

### 早期方法

**年份範圍**：請標註具體年份

- 具體方法名稱和描述
- 使用這些方法的代表性研究（引用作者和年份）
- 方法的優勢和**根本性限制**
- 為什麼這些限制在當時無法克服？

### 中期演進

**年份範圍**：請標註具體年份

- 新方法的出現：具體名稱、提出者、年份
- **為什麼需要新方法**？舊方法哪些問題促使改變？
- 新方法如何克服舊限制？用了什麼創新技術或概念？
- 新方法帶來了什麼新限制？

### 當前主流方法

**時間範圍**：近 3-5 年

- 目前最常用的 2-3 種方法
- 為什麼這些方法成為主流？
- 當前方法的**未解決問題**和**內在假設**
- 哪些情境下這些方法失效？

### 被淘汰的方法與原因

- 具體列舉 2-3 個曾流行但被放棄的方法
- **深入分析為什麼被淘汰**：是方法本身的問題？還是技術演進？還是研究興趣轉移？


## 四、研究缺口批判性識別

**數量要求**：4-6 個缺口
**字數要求**：每個缺口 150-200 字

對每個缺口進行**深度剖析**，請為每個缺口取一個具體的名稱。

### 缺口一：【請具體命名】

**詳細描述**

這個缺口的具體內容是什麼？為什麼現有研究沒有覆蓋？

**證據支持**

從論文集中找出哪些證據支持這個缺口的存在？引用具體論文。

**根本原因**

為什麼這個領域忽略了這個方向？
- 技術限制？
- 資料獲取困難？
- 研究範式的集體盲點？
- 跨領域知識不足？

**研究價值**

填補這個缺口會帶來什麼：
- 理論貢獻？
- 實務應用價值？
- 方法論突破？

**可行性評估**

目前的技術條件是否足以研究這個缺口？需要什麼資源？

### 缺口二至六：【請依此格式繼續】


## 五、研究方向具體建議

**數量要求**：3-4 個方向
**字數要求**：每個方向 200-250 字

對每個建議提供**可執行的研究計劃**，請為每個方向取一個具體的名稱。

### 方向一：【請具體命名】

**研究問題**

用研究問題的形式表述（如「如何⋯⋯」、「什麼因素⋯⋯」、「是否存在⋯⋯」）。

**問題來源**

這個問題如何從上述缺口分析中得出？

**研究意義**

- 理論意義：會推進哪些理論發展？
- 實務意義：會解決什麼實際問題？
- 創新性：與現有研究的差異在哪裡？

**研究設計初步建議**

- 可能的研究方法（質性／量化／混合）
- 需要什麼樣的資料？
- 預期的挑戰是什麼？

**資源需求**

技術、資料、時間、人力。

**第一步行動**

具體到可以立即執行的步驟。

**預期貢獻**

成功後可以產出什麼類型的論文？（期刊論文、會議論文）

### 方向二至四：【請依此格式繼續】


## 六、學術爭議與不同學派

若領域內存在學術爭議，請分析：

- 識別領域內的主要爭議點
- 不同學派的代表人物和觀點
- 這些爭議對未來研究的啟示


## 七、整體總結與核心建議

**字數要求**：300-400 字

### 領域現狀總結

用 3-4 句話總結這個研究領域的當前狀態、主要成就和面臨的核心挑戰。

### 最具價值的研究方向

從上述分析中，提煉出**最值得投入的 1-2 個研究方向**，說明為什麼這些方向最重要。

### 給博碩士生的具體建議

針對博碩士生的實際情況，提供：

- **入手點**：如果現在開始研究，應該從哪裡切入？
- **必讀文獻**：哪 3-5 篇論文是必須精讀的？（從提供的論文中選擇）
- **技能準備**：需要掌握哪些技術或方法？
- **時間規劃**：一個可行的研究時程建議（如碩士 2 年、博士 4 年）

### 風險提醒

客觀指出：

- 這個領域有哪些「看起來有趣但實際很難發表」的陷阱？
- 哪些方向競爭過於激烈，不適合學生入場？
- 需要警惕的研究誤區


# 輸出要求

**引用規範**

每個關鍵論述都要引用具體的作者和年份（如「Zhang et al., 2020 提出⋯⋯」）。

**深度優先**

寧願深入分析 4 個缺口，也不要泛泛而談 6 個。

**批判性思維**

不只是總結論文說了什麼，更要分析**沒說什麼**、**為什麼沒說**。

**具體化**

避免「需要更多研究」這類空洞建議，要說明**具體研究什麼**、**如何研究**。

**可行性**

建議要基於現實條件，不要提出目前技術無法實現的方向。

**結構清晰**

使用 Markdown 格式，清晰的標題層級和要點。

**標點符號**

全部使用全形標點符號（，。、！？：；「」『』）。


請提供一份**博士水準的深度分析報告**，透過系統化的分析，幫助研究者找到真正有價值且可行的研究方向。"""

        return prompt

    def _parse_analysis_result(self, response_text: str) -> Dict:
        """解析 AI 響應為結構化數據"""

        # 簡單解析：將響應文本分段
        sections = {
            "full_text": response_text,
            "development_history": "",
            "core_problems": "",
            "method_evolution": "",
            "research_gaps": "",
            "recommendations": ""
        }

        # 嘗試提取各個部分
        if "## 1. 領域發展史摘要" in response_text or "領域發展史" in response_text:
            sections["development_history"] = self._extract_section(response_text, ["領域發展史", "## 1"])

        if "## 2. 核心研究問題" in response_text or "核心研究問題" in response_text:
            sections["core_problems"] = self._extract_section(response_text, ["核心研究問題", "## 2"])

        if "## 3. 方法演進分析" in response_text or "方法演進" in response_text:
            sections["method_evolution"] = self._extract_section(response_text, ["方法演進", "## 3"])

        if "## 4. 研究缺口識別" in response_text or "研究缺口" in response_text:
            sections["research_gaps"] = self._extract_section(response_text, ["研究缺口", "## 4"])

        if "## 5. 研究方向建議" in response_text or "研究方向" in response_text:
            sections["recommendations"] = self._extract_section(response_text, ["研究方向", "## 5"])

        return sections

    def _extract_section(self, text: str, markers: List[str]) -> str:
        """提取文本中的特定段落"""

        for marker in markers:
            if marker in text:
                start_idx = text.find(marker)
                # 找到下一個 ## 標題作為結束
                next_section_idx = text.find("\n## ", start_idx + len(marker))

                if next_section_idx > start_idx:
                    return text[start_idx:next_section_idx].strip()
                else:
                    return text[start_idx:].strip()

        return ""

    def generate_summary(self, papers: List[Dict]) -> str:
        """生成論文集的快速摘要"""

        if not papers:
            return "沒有論文可供分析"

        papers_text = self._prepare_papers_text(papers)

        prompt = f"""請用 200 字以內簡要總結以下論文集的主要研究主題和趨勢：

{papers_text[:3000]}  # 限制長度

請用 1-2 段話總結：
1. 主要研究的是什麼問題？
2. 有什麼明顯的研究趨勢或變化？
"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text

        except Exception as e:
            return f"生成摘要失敗: {str(e)}"
