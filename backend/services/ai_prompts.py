"""
AI 提示詞模板
AI Prompt Templates - 用於研究缺口識別和領域分析
"""


class AIPromptTemplates:
    """AI 分析提示詞模板集合"""

    @staticmethod
    def format_papers_for_prompt(papers):
        """
        格式化論文數據為提示詞輸入

        Args:
            papers: 論文列表

        Returns:
            格式化的論文文本
        """
        formatted = []
        for i, paper in enumerate(papers, 1):
            paper_text = f"""
論文 {i}:
標題: {paper.title}
作者: {', '.join([author.name for author in paper.authors]) if hasattr(paper, 'authors') else 'N/A'}
年份: {paper.year or 'N/A'}
期刊: {paper.journal or 'N/A'}
摘要: {paper.abstract or '無摘要'}
"""
            if paper.introduction:
                paper_text += f"引言節錄: {paper.introduction[:500]}...\n"
            if paper.conclusion:
                paper_text += f"結論節錄: {paper.conclusion[:500]}...\n"

            formatted.append(paper_text)

        return "\n".join(formatted)

    @staticmethod
    def domain_history_prompt(papers_text, domain_name=""):
        """領域發展史摘要提示詞"""
        return f"""
你是一位資深的學術研究顧問。我將提供一組按照年代排序的學術論文資料。
請分析這些論文，生成一份領域發展史摘要。

研究領域: {domain_name or '未指定'}

論文資料（按年代排序）：
{papers_text}

請按照以下結構回答：

## 領域發展史

### 起源階段（最早的研究）
- 這個研究問題最早是誰在哪一年提出的？
- 最初的動機是什麼？
- 早期使用了什麼方法？

### 發展階段（方法演進）
- 哪些方法或理論被提出並成為主流？
- 是誰在什麼時候提出的？
- 為什麼這些方法被採用？

### 轉折點（重要突破）
- 有哪些關鍵的技術突破或理論創新？
- 這些突破解決了什麼問題？
- 是誰做出的貢獻？

### 當前狀態（最新進展）
- 目前這個領域的主流方法是什麼？
- 最近幾年的研究重心在哪裡？

請用清晰、學術性的繁體中文回答，並標註關鍵人物和年份。
"""

    @staticmethod
    def core_problems_prompt(papers_text):
        """核心問題識別提示詞"""
        return f"""
基於以下論文集，請識別這個研究領域的核心問題。

論文資料：
{papers_text}

請回答：

## 核心研究問題

### 反覆出現的問題
列出在多篇論文中反覆被提及的研究問題，並標註：
- 問題描述
- 首次提出時間
- 有多少篇論文討論過
- 目前的解決狀態（已解決/部分解決/未解決）

### 問題演變
描述這些問題如何隨時間演變：
- 問題定義是否改變？
- 是否從一個大問題分解為多個子問題？

請以結構化、易讀的繁體中文格式回答。
"""

    @staticmethod
    def method_evolution_prompt(papers_text, early_period="", mid_period="", recent_period=""):
        """方法演進分析提示詞"""
        return f"""
分析以下論文中使用的研究方法的演進過程。

論文資料：
{papers_text}

請分析：

## 方法演進

### 早期方法{f"（{early_period}）" if early_period else ""}
- 使用了什麼方法？
- 優點和限制是什麼？

### 中期方法{f"（{mid_period}）" if mid_period else ""}
- 哪些新方法被提出？
- 為什麼要改變方法？
- 解決了什麼限制？

### 當前方法{f"（{recent_period}）" if recent_period else ""}
- 目前主流的方法是什麼？
- 與早期方法相比有什麼改進？
- 仍存在什麼限制？

### 被淘汰的方法
- 哪些方法曾經流行但後來被放棄？
- 為什麼被淘汰？

請提供具體的方法名稱和年份，使用繁體中文回答。
"""

    @staticmethod
    def research_gaps_prompt(papers_text):
        """研究缺口識別提示詞"""
        return f"""
作為一位批判性思考的學術研究者，請分析以下論文集，識別研究缺口和未解決的問題。

論文資料：
{papers_text}

請從以下角度分析：

## 研究缺口

### 方法論缺口
- 現有方法有什麼假設？這些假設是否總是成立？
- 有哪些情境或條件尚未被測試？
- 是否有被主流忽略的替代方法？

### 應用缺口
- 現有研究主要集中在什麼樣的數據或族群？
- 哪些應用場景被忽略了？
- 是否存在特定的人群或情境未被覆蓋？

### 理論缺口
- 有哪些現象尚未得到充分解釋？
- 是否有相互矛盾的發現？
- 哪些理論基礎仍需要加強？

### 被忽略的方向
- 整個領域是否有集體偏向（如過度關注準確率而忽略可解釋性）？
- 有沒有重要但被邊緣化的研究方向？

請為每個缺口提供：
- 具體描述
- 為什麼重要
- 潛在的研究價值
- 可能的研究方向

使用繁體中文回答。
"""

    @staticmethod
    def controversies_prompt(papers_text):
        """爭議點識別提示詞"""
        return f"""
分析以下論文，識別領域內的爭議點和不同學派的觀點。

論文資料：
{papers_text}

請分析：

## 學術爭議與分歧

### 方法論爭議
- 有哪些關於方法選擇的分歧？
- 不同陣營各自的主張是什麼？
- 哪些學者站在哪一邊？

### 理論爭議
- 對於核心概念的定義是否有不同看法？
- 是否有相互矛盾的理論解釋？

### 結果爭議
- 是否有研究得出相反的結論？
- 這些差異可能的原因是什麼（數據、方法、解釋）？

### 學術陣營
- 是否能識別出不同的研究陣營或學派？
- 這些陣營的核心差異是什麼？
- 各自的代表人物和機構是誰？

請客觀呈現各方觀點，不要偏袒任何一方。使用繁體中文回答。
"""

    @staticmethod
    def research_directions_prompt(papers_text, identified_gaps=""):
        """研究方向建議提示詞"""
        gaps_section = f"已識別的研究缺口：\n{identified_gaps}\n" if identified_gaps else ""
        return f"""
基於對以下論文集的分析，請提出有價值的未來研究方向。

論文資料：
{papers_text}

{gaps_section}

請提出：

## 未來研究方向建議

對於每個建議的方向，請提供：

### 研究問題
- 具體的研究問題是什麼？

### 重要性
- 為什麼這個方向重要？
- 可能產生什麼影響？

### 可行性
- 需要什麼樣的資源和技術？
- 目前是否具備條件進行研究？

### 切入點
- 如何開始這個研究？
- 第一步應該做什麼？

### 潛在挑戰
- 可能面臨什麼困難？
- 如何應對這些挑戰？

請優先推薦那些：
1. 有實際價值的方向
2. 具備一定可行性的方向
3. 能填補重要缺口的方向
4. 有創新性的方向

使用繁體中文回答，提供 3-5 個具體的研究方向建議。
"""

    @staticmethod
    def comprehensive_analysis_prompt(papers_text, domain_name=""):
        """綜合分析提示詞（一次性分析）"""
        return f"""
你是一位資深的學術研究顧問。我將提供一組學術論文資料，請進行全面的研究領域分析。

研究領域: {domain_name or '未指定'}

論文資料：
{papers_text}

請按照以下結構進行完整分析：

## 一、領域發展史
簡要描述這個研究領域的發展歷程，包括：
- 起源和早期研究
- 重要的方法論突破
- 關鍵轉折點
- 當前狀態

## 二、核心研究問題
列出 3-5 個反覆出現的核心問題，說明其演變過程和當前狀態。

## 三、方法演進
描述研究方法如何隨時間演進，包括：
- 早期方法及其局限
- 當前主流方法
- 被淘汰的方法及原因

## 四、研究缺口
從方法論、應用、理論三個角度，識別至少 3 個重要的研究缺口。

## 五、學術爭議
如果存在明顯的學術爭議或不同學派，請描述其核心分歧。

## 六、研究方向建議
提出 3-5 個具體的未來研究方向，包括：
- 研究問題
- 重要性
- 可行性評估
- 建議的切入點

請用學術性但易懂的繁體中文撰寫，總字數約 2000-3000 字。
"""
