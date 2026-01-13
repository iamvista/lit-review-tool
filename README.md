# LitReview Tool - 博碩士生文獻管理工具

<div align="center">

基於「上帝視角文獻回顧法」的智能文獻管理系統，專為博碩士生設計。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)

[功能介紹](#-核心功能) • [快速開始](#-快速開始) • [部署指南](DEPLOYMENT_GUIDE.md) • [API 文檔](#-api-端點)

</div>

---

## ✨ 核心功能

### 1. **文獻導入與管理** 📚
- ✅ **多種導入方式**：BibTeX、DOI、PDF 上傳
- ✅ **智能解析**：自動提取 DOI、作者、摘要
- ✅ **CrossRef API**：自動獲取完整元數據
- ✅ **時間軸排序**：按年份自動組織文獻

### 2. **橫向串讀視圖** 📖
- ✅ **三欄結構**：摘要、引言、結論快速瀏覽
- ✅ **鍵盤導航**：`↑↓` 切換論文，高效閱讀
- ✅ **即時標註**：筆記、標籤、閱讀狀態自動保存
- ✅ **進度追蹤**：清晰顯示已讀/未讀狀態
- ✅ **學術級排版**：大幅留白、舒適行距

### 3. **AI 輔助研究缺口分析** 🤖
- ✅ **深度分析**：領域發展史、核心問題識別
- ✅ **研究缺口**：方法論、應用、理論缺口分析
- ✅ **具體建議**：可執行的研究方向與第一步行動
- ✅ **博士級報告**：總結、建議、風險提醒
- ✅ **Anthropic Claude**：使用最先進的 AI 模型

### 4. **關鍵人物網絡分析** 🕸️
- ✅ **可視化**：互動式作者合作網絡圖
- ✅ **關鍵人物識別**：自動標記核心研究者
- ✅ **作者統計**：論文數、引用數、h-index
- ✅ **合作關係**：發現研究陣營和學派

### 5. **完整的用戶系統** 👤
- ✅ **安全認證**：JWT Token、密碼加密
- ✅ **忘記密碼**：郵件重置（開發環境可直接顯示連結）
- ✅ **個人設定**：API Key 加密存儲
- ✅ **多專案管理**：支援管理多個研究主題

---

## 🎯 適用場景

- 📝 **碩博士論文寫作**：系統化整理文獻回顧章節
- 🔬 **研究計劃撰寫**：快速識別研究缺口
- 📊 **學術報告準備**：了解領域發展脈絡
- 🎓 **考試準備**：高效掌握大量論文
- 💡 **研究方向選擇**：AI 輔助找到有價值的方向

---

## 🚀 快速開始

### 線上使用（推薦）

**即將推出**：https://lit-review-tool.pages.dev

---

### 本地開發

#### 前置需求
- Python 3.11+
- Node.js 18+
- SQLite（自動創建）

#### 後端設置

```bash
# 1. 進入後端目錄
cd backend

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 設置環境變數（可選）
export PORT=5001
export ANTHROPIC_API_KEY=your-api-key  # 用於 AI 分析

# 4. 啟動後端
python app.py
```

後端運行在：http://localhost:5001

#### 前端設置

```bash
# 1. 進入前端目錄
cd frontend

# 2. 安裝依賴
npm install

# 3. 啟動開發服務器
npm run dev
```

前端運行在：http://localhost:5173

---

## 📖 使用指南

### 1. 註冊與登入

1. 訪問 http://localhost:5173
2. 點擊「立即註冊」
3. 填寫郵箱、用戶名、密碼
4. 登入系統

### 2. 創建專案

1. 點擊「+ 新建專案」
2. 填寫資訊：
   - **專案名稱**：如「深度學習在醫學影像的應用」
   - **描述**：研究問題和目標
   - **研究領域**：如「人工智慧」、「醫學」
   - **目標論文數量**：建議 10-20 篇

### 3. 導入文獻

#### 方式一：PDF 上傳（推薦） ⭐

1. 點擊「📄 上傳 PDF」
2. 拖放或選擇 PDF 文件
3. 系統自動提取：
   - 標題、作者、年份
   - DOI（如有）
   - 摘要、引言、結論
4. 確認導入

#### 方式二：BibTeX 導入

```bibtex
@article{smith2020deep,
  title={Deep Learning for Medical Image Analysis},
  author={Smith, John and Doe, Jane},
  journal={Nature Medicine},
  year={2020},
  volume={26},
  pages={1234-1245},
  doi={10.1038/s41591-020-1234-5}
}
```

#### 方式三：DOI 導入

輸入 DOI：`10.1038/s41591-020-1234-5`，自動獲取完整資訊。

### 4. 橫向串讀模式

1. 點擊「📖 開始閱讀」
2. 左側時間軸：瀏覽所有論文
3. 右側內容區：
   - **摘要**：核心貢獻和發現
   - **引言**：研究背景和動機
   - **結論**：主要結果和未來方向
4. 快捷鍵：
   - `↑` / `↓`：上下切換論文
   - `j` / `k`：Vim 風格導航
5. 添加筆記、標籤

### 5. AI 研究缺口分析

1. 進入專案後點擊「🤖 AI 分析」
2. 點擊「生成新分析」
3. 等待 AI 處理（約 1-2 分鐘）
4. 獲得完整報告：
   - 📊 **領域發展史**：起源、演進、轉折點
   - 🎯 **核心問題**：反覆出現的挑戰
   - 🔍 **研究缺口**：方法論、應用、理論缺口
   - 💡 **具體建議**：3-4 個可執行的研究方向
   - 📚 **必讀文獻**：最重要的 3-5 篇論文
   - ⚠️ **風險提醒**：避免陷阱和誤區

### 6. 網絡分析

1. 點擊「🕸️ 網絡分析」
2. 查看：
   - 作者合作網絡圖
   - 關鍵人物列表
   - 作者統計資料

---

## 🛠️ 技術棧

### 後端
- **框架**：Flask 3.0
- **數據庫**：SQLite / PostgreSQL + SQLAlchemy
- **認證**：Flask-JWT-Extended（JWT Token）
- **文獻解析**：bibtexparser、PyPDF2、pdfplumber
- **外部 API**：CrossRef、Semantic Scholar
- **AI**：Anthropic Claude API
- **網絡分析**：NetworkX、Pyvis

### 前端
- **框架**：React 18
- **構建工具**：Vite 5
- **樣式**：Tailwind CSS
- **路由**：React Router 6
- **請求**：Axios
- **Markdown**：react-markdown
- **可視化**：D3.js

---

## 📡 API 端點

### 認證
```
POST   /api/auth/register         # 註冊
POST   /api/auth/login            # 登入
GET    /api/auth/me               # 當前用戶
POST   /api/auth/forgot-password  # 忘記密碼
POST   /api/auth/reset-password   # 重置密碼
```

### 專案
```
GET    /api/projects              # 所有專案
POST   /api/projects              # 創建專案
GET    /api/projects/:id          # 專案詳情
PUT    /api/projects/:id          # 更新專案
DELETE /api/projects/:id          # 刪除專案
GET    /api/projects/:id/papers   # 專案論文
GET    /api/projects/:id/stats    # 專案統計
```

### 論文
```
POST   /api/papers/import/bibtex  # BibTeX 導入
POST   /api/papers/import/doi     # DOI 導入
POST   /api/papers/upload-pdf     # PDF 上傳
POST   /api/papers/confirm-pdf    # 確認 PDF
GET    /api/papers/:id            # 論文詳情
PUT    /api/papers/:id            # 更新論文
DELETE /api/papers/:id            # 刪除論文
PUT    /api/papers/:id/notes      # 更新筆記
PUT    /api/papers/:id/tags       # 更新標籤
PUT    /api/papers/:id/read-status # 閱讀狀態
```

### AI 分析
```
POST   /api/analysis/projects/:id/analyze  # 生成分析
GET    /api/analysis/projects/:id          # 獲取分析列表
GET    /api/analysis/:id                   # 單個分析
DELETE /api/analysis/:id                   # 刪除分析
POST   /api/analysis/:id/export/docx       # 導出 Word
POST   /api/analysis/:id/export/markdown   # 導出 Markdown
```

### 網絡分析
```
GET    /api/network/projects/:id/authors   # 作者網絡
GET    /api/network/projects/:id/stats     # 網絡統計
```

---

## 🚢 部署指南

詳細部署步驟請參考：[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### 快速部署到 Cloudflare + Render

1. **推送到 GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **部署前端到 Cloudflare Pages**
   - 連接 GitHub 倉庫
   - 構建設置：`cd frontend && npm install && npm run build`
   - 輸出目錄：`frontend/dist`

3. **部署後端到 Render**
   - 連接 GitHub 倉庫
   - 自動讀取 `render.yaml`
   - 設置環境變數（API Key）

4. **更新 API URL**
   - 在 Cloudflare 設置：`VITE_API_URL=https://your-backend.onrender.com`

完成！🎉

---

## 🔒 安全性

- ✅ 密碼使用 Werkzeug 加密存儲
- ✅ JWT Token 認證機制
- ✅ API Key 使用 Fernet 加密
- ✅ CORS 白名單保護
- ✅ SQL 注入防護（SQLAlchemy）
- ✅ XSS 防護（React 自動轉義）

**生產環境檢查清單**：
- [ ] 更改 `SECRET_KEY` 和 `JWT_SECRET_KEY`
- [ ] 設置 CORS 白名單（移除 `*`）
- [ ] 啟用 HTTPS
- [ ] 定期備份數據庫
- [ ] 設置 API 速率限制
- [ ] 監控錯誤日誌

---

## 📊 開發進度

- [x] **Phase 1: 基礎架構** ✅
- [x] **Phase 2: 文獻管理** ✅
- [x] **Phase 3: 橫向串讀** ✅
- [x] **Phase 4: 網絡分析** ✅
- [x] **Phase 5: AI 分析** ✅
- [x] **Phase 6: 優化部署** ✅

**新功能計劃**：
- [ ] 郵件通知系統
- [ ] 協作功能（多人共享專案）
- [ ] 移動端 App
- [ ] Chrome 插件（快速添加論文）
- [ ] 自動文獻推薦

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

### 開發流程

```bash
# 1. Fork 專案
# 2. 創建功能分支
git checkout -b feature/amazing-feature

# 3. 提交更改
git commit -m 'Add some amazing feature'

# 4. 推送到分支
git push origin feature/amazing-feature

# 5. 開啟 Pull Request
```

---

## 📄 授權

MIT License - 自由使用和修改

---

## 🙏 致謝

- **設計理念**：基於[匹茲堡Y教授的文獻回顧方法](https://www.ptt.cc/bbs/PhD/M.1599579356.A.D52.html)
- **AI 支持**：Anthropic Claude
- **文獻 API**：CrossRef、Semantic Scholar
- **開源社群**：Flask、React、Tailwind CSS

---

## 📧 聯繫方式

- **Issues**：[GitHub Issues](https://github.com/YOUR_USERNAME/lit-review-tool/issues)
- **討論**：[GitHub Discussions](https://github.com/YOUR_USERNAME/lit-review-tool/discussions)

---

<div align="center">

**⭐ 如果這個工具對你有幫助，請給個 Star！**

Made with ❤️ for PhD students

</div>
