# PDF 上傳與文獻導入功能設計

## 問題分析

**用戶痛點**：「搜集好文獻卻不知如何活用這套系統」

目前系統缺少直觀的文獻導入方式，用戶需要：
1. 將收集的 PDF 文獻快速導入系統
2. 自動提取論文的摘要、引言、結論
3. 整合到專案中進行 AI 分析

## 設計方案

### 方案選擇：混合式 PDF 處理

**核心功能**：
1. **拖放上傳 PDF** - 支援單個或批次上傳
2. **自動提取 Metadata** - DOI/標題/作者/年份
3. **全文解析** - 提取摘要/引言/結論/參考文獻
4. **手動修正介面** - 用戶可以編輯自動提取的資訊
5. **整合到專案** - 自動加入專案的論文列表

---

## 技術架構

### 後端 - PDF 處理流程

```
PDF 上傳
  ↓
提取文字內容 (PyPDF2/pdfplumber)
  ↓
嘗試識別 DOI/arXiv ID
  ├─ 找到 DOI → 呼叫 CrossRef API 獲取完整 metadata
  ├─ 找到 arXiv ID → 呼叫 arXiv API
  └─ 都沒有 → 使用 AI 提取（Claude API）
  ↓
全文段落分析
  ├─ 識別摘要（Abstract）
  ├─ 識別引言（Introduction）前 3-5 段
  ├─ 識別結論（Conclusion/Discussion）後 3-5 段
  └─ 識別參考文獻
  ↓
返回結構化資料給前端
```

### 前端 - 用戶介面流程

```
專案詳情頁 → 新增「上傳 PDF」按鈕
  ↓
拖放區域（可拖放多個 PDF）
  ↓
顯示上傳進度（每個 PDF 的處理狀態）
  ↓
顯示提取結果預覽
  ├─ 標題 ✓
  ├─ 作者 ✓
  ├─ 年份 ✓
  ├─ 期刊 ✓
  ├─ 摘要 ✓（可展開查看）
  └─ 編輯按鈕（修正錯誤）
  ↓
確認導入 → 加入專案論文列表
```

---

## 實現細節

### 1. 後端新增路由

**新增文件**：`backend/services/pdf_processor.py`

```python
class PDFProcessor:
    """PDF 處理器"""

    def extract_text(self, pdf_path) -> str:
        """提取 PDF 全文"""

    def extract_metadata(self, text) -> dict:
        """提取 metadata（DOI、標題、作者）"""

    def identify_doi(self, text) -> str:
        """識別 DOI"""

    def extract_sections(self, text) -> dict:
        """提取摘要、引言、結論"""

    def fetch_metadata_from_doi(self, doi) -> dict:
        """從 CrossRef API 獲取 metadata"""
```

**新增路由**：`backend/routes/papers.py`

```python
@papers_bp.route('/projects/<int:project_id>/upload-pdf', methods=['POST'])
def upload_pdf(project_id):
    """上傳 PDF 並提取資訊"""
    # 1. 保存 PDF 文件
    # 2. 提取文字
    # 3. 提取 metadata
    # 4. 返回結構化資料（不直接存入資料庫）

@papers_bp.route('/projects/<int:project_id>/confirm-paper', methods=['POST'])
def confirm_paper(project_id):
    """用戶確認後存入資料庫"""
    # 接收用戶可能修正過的資料
    # 存入 Paper 表
```

### 2. 前端新增組件

**新增組件**：`frontend/src/components/papers/PDFUploader.jsx`

```jsx
export default function PDFUploader({ projectId, onSuccess }) {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [results, setResults] = useState([])

  const handleDrop = (acceptedFiles) => {
    // 處理拖放的 PDF 文件
  }

  const handleUpload = async () => {
    // 逐個上傳 PDF 並提取資訊
    for (let file of files) {
      const result = await uploadPDF(file)
      setResults(prev => [...prev, result])
    }
  }

  const handleConfirm = async () => {
    // 確認所有提取的論文資訊
    await confirmPapers(results)
    onSuccess()
  }

  return (
    <div>
      <Dropzone onDrop={handleDrop} />
      {results.map(result => (
        <PaperPreview
          key={result.id}
          data={result}
          onEdit={(edited) => updateResult(result.id, edited)}
        />
      ))}
      <button onClick={handleConfirm}>確認導入 {results.length} 篇論文</button>
    </div>
  )
}
```

### 3. PDF 段落識別策略

#### 摘要識別
- 關鍵字：「Abstract」、「摘要」、「ABSTRACT」
- 位置：通常在第一頁，標題後
- 特徵：獨立段落，200-400 字

#### 引言識別
- 關鍵字：「Introduction」、「1. Introduction」、「緒論」
- 位置：摘要後，方法前
- 提取：前 3-5 段或前 800-1000 字

#### 結論識別
- 關鍵字：「Conclusion」、「Discussion」、「結論」、「6. Conclusion」
- 位置：論文最後 2-3 頁
- 提取：該章節的完整內容

#### 參考文獻識別
- 關鍵字：「References」、「Bibliography」、「參考文獻」
- 位置：論文最後
- 用途：可以進一步挖掘引用關係

---

## 優化建議

### Phase 1（MVP）- 單個 PDF 上傳
- 上傳單個 PDF
- 提取基本資訊（標題、作者、年份、摘要）
- 手動確認後加入專案

### Phase 2 - 批次上傳與智能提取
- 支援拖放多個 PDF
- 並行處理
- 進度條顯示

### Phase 3 - AI 增強
- 使用 Claude API 提取摘要/引言/結論（當 PDF 解析失敗時）
- AI 自動分類論文主題
- AI 建議論文標籤

### Phase 4 - 高級功能
- PDF 全文搜尋
- PDF 內文高亮和註記
- 直接在系統中閱讀 PDF
- PDF 與分析報告的雙向連結

---

## 用戶使用流程

### 情境一：單篇論文上傳

1. 用戶進入專案詳情頁
2. 點擊「上傳 PDF 論文」按鈕
3. 選擇一個 PDF 文件
4. 系統自動提取資訊，顯示預覽
5. 用戶確認或修正資訊
6. 點擊「加入專案」
7. 論文出現在時間軸列表中

### 情境二：批次上傳（10+ 篇論文）

1. 用戶有 15 篇下載好的 PDF
2. 全選 15 個文件，拖放到上傳區域
3. 系統逐個處理，顯示進度（已完成 3/15）
4. 處理完畢後，顯示 15 個論文預覽卡片
5. 用戶快速檢查自動提取的資訊
6. 對於提取錯誤的，點擊「編輯」修正
7. 點擊「確認全部導入」
8. 15 篇論文批次加入專案

### 情境三：從 PDF 到 AI 分析

1. 用戶上傳 10 篇論文的 PDF
2. 系統自動提取摘要、引言、結論
3. 用戶前往「AI 分析」頁面
4. 點擊「新增分析」
5. 系統使用提取的內容進行深度分析
6. 生成研究缺口報告
7. 用戶匯出 Word 文檔

---

## 技術選型

### PDF 解析庫
- **PyPDF2**：基礎 PDF 文字提取
- **pdfplumber**：更強大的表格和佈局解析
- **pdf2image + Tesseract OCR**：處理掃描版 PDF（可選）

### Metadata API
- **CrossRef API**：通過 DOI 獲取論文 metadata
- **arXiv API**：arXiv 論文資訊
- **Semantic Scholar API**：豐富的學術資訊（可選）

### AI 輔助
- **Claude API**：當無法識別 DOI 時，用 AI 提取資訊
- **Prompt Engineering**：「請從以下 PDF 文字中提取：標題、作者、年份、期刊、摘要」

---

## 資料庫擴展

### Paper 表新增欄位

```sql
ALTER TABLE papers ADD COLUMN pdf_path TEXT;
ALTER TABLE papers ADD COLUMN pdf_file_name TEXT;
ALTER TABLE papers ADD COLUMN pdf_uploaded_at TIMESTAMP;
ALTER TABLE papers ADD COLUMN extraction_method TEXT; -- 'doi', 'ai', 'manual'
ALTER TABLE papers ADD COLUMN extraction_confidence FLOAT; -- 0.0-1.0
```

---

## 下一步行動

1. **立即實作** - PDF 上傳與基礎解析（標題、作者、年份）
2. **測試** - 用 5-10 篇真實論文 PDF 測試提取準確率
3. **迭代** - 根據測試結果改進解析算法
4. **擴展** - 加入摘要/引言/結論的深度提取
5. **整合** - 與 AI 分析功能深度整合

---

## 預期影響

透過 PDF 上傳功能：
1. **降低使用門檻** - 用戶可以直接拖放 PDF，無需手動輸入
2. **提升使用效率** - 批次處理 10+ 篇論文只需幾分鐘
3. **增加系統價值** - 從「文獻管理」提升到「文獻智能分析」
4. **完整工作流** - 收集 → 導入 → 分析 → 撰寫，一站式完成
