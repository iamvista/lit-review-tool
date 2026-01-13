# 部署指南 - GitHub & Cloudflare Pages

## 📋 部署前檢查清單

- [ ] 所有敏感資訊已從代碼中移除
- [ ] .gitignore 配置正確
- [ ] 環境變數已準備
- [ ] 前端構建成功
- [ ] 後端可正常啟動

---

## 1️⃣ GitHub 部署

### 步驟 1：初始化並推送到 GitHub

```bash
# 1. 確認在專案根目錄
cd /Users/vista/lit-review-tool

# 2. 初始化 Git（如果還沒有）
git init

# 3. 添加所有文件
git add .

# 4. 創建初始提交
git commit -m "Initial commit: LitReview Tool - 博碩士生文獻管理工具

Features:
- 用戶認證（註冊、登入、忘記密碼）
- 專案管理系統
- PDF 上傳與解析
- BibTeX/DOI 文獻導入
- 橫向串讀視圖（摘要/引言/結論）
- AI 研究缺口分析（Anthropic Claude）
- 作者網絡分析
- 全繁體中文介面"

# 5. 在 GitHub 創建新倉庫
# 前往 https://github.com/new
# 倉庫名稱：lit-review-tool
# 描述：博碩士生文獻管理工具 - 基於上帝視角文獻回顧法
# 可見性：Public 或 Private

# 6. 連接到遠程倉庫（替換 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/lit-review-tool.git

# 7. 推送到 GitHub
git branch -M main
git push -u origin main
```

---

## 2️⃣ Cloudflare Pages 部署（前端）

### 方案 A：透過 Cloudflare Dashboard（推薦）

#### 步驟 1：連接 GitHub 倉庫

1. 登入 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 前往 **Workers & Pages** → **Create application** → **Pages**
3. 選擇 **Connect to Git**
4. 授權 Cloudflare 訪問你的 GitHub
5. 選擇 `lit-review-tool` 倉庫

#### 步驟 2：配置構建設置

```
Framework preset: Vite
Build command: cd frontend && npm install && npm run build
Build output directory: frontend/dist
Root directory: /
```

#### 步驟 3：環境變數配置

在 **Settings** → **Environment variables** 添加：

```
VITE_API_URL=https://your-backend-url.com
```

⚠️ **重要**：前端環境變數必須以 `VITE_` 開頭才能在構建時被訪問。

#### 步驟 4：部署

1. 點擊 **Save and Deploy**
2. 等待構建完成（約 2-3 分鐘）
3. 獲取 Cloudflare Pages URL：`https://lit-review-tool.pages.dev`

---

### 方案 B：使用 Wrangler CLI

```bash
# 1. 安裝 Wrangler
npm install -g wrangler

# 2. 登入 Cloudflare
wrangler login

# 3. 構建前端
cd frontend
npm install
npm run build

# 4. 部署到 Cloudflare Pages
npx wrangler pages deploy dist --project-name=lit-review-tool

# 5. 設置環境變數
npx wrangler pages secret put VITE_API_URL
# 輸入：https://your-backend-url.com
```

---

## 3️⃣ 後端部署選項

### 選項 1：Render.com（推薦，免費方案）

#### 步驟 1：準備 Render 配置

創建 `render.yaml`：

```yaml
services:
  - type: web
    name: litreview-backend
    env: python
    region: oregon
    plan: free
    buildCommand: |
      cd backend
      pip install -r requirements.txt
    startCommand: |
      cd backend
      python app.py
    envVars:
      - key: PORT
        value: 5001
      - key: DATABASE_URL
        generateValue: true
        value: sqlite:////opt/render/project/src/backend/instance/litreview.db
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: ANTHROPIC_API_KEY
        sync: false  # 需要手動設置
      - key: CORS_ORIGINS
        value: https://lit-review-tool.pages.dev,https://your-custom-domain.com
```

#### 步驟 2：在 Render 部署

1. 前往 [Render Dashboard](https://dashboard.render.com/)
2. 選擇 **New** → **Blueprint**
3. 連接 GitHub 倉庫
4. Render 會自動讀取 `render.yaml`
5. 手動設置 `ANTHROPIC_API_KEY`
6. 點擊 **Apply**

#### 步驟 3：更新前端 API URL

在 Cloudflare Pages 環境變數中更新：
```
VITE_API_URL=https://litreview-backend.onrender.com
```

---

### 選項 2：Railway.app

```bash
# 1. 安裝 Railway CLI
npm install -g @railway/cli

# 2. 登入
railway login

# 3. 創建新專案
railway init

# 4. 連接 GitHub
railway link

# 5. 部署後端
cd backend
railway up

# 6. 設置環境變數
railway variables set DATABASE_URL="sqlite:////app/instance/litreview.db"
railway variables set SECRET_KEY="your-secret-key"
railway variables set JWT_SECRET_KEY="your-jwt-secret"
railway variables set ANTHROPIC_API_KEY="your-api-key"
```

---

### 選項 3：Fly.io（適合 Docker）

創建 `fly.toml`：

```toml
app = "litreview-backend"
primary_region = "nrt"  # Tokyo

[build]
  dockerfile = "backend/Dockerfile"

[env]
  PORT = "5001"

[[services]]
  internal_port = 5001
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

部署：
```bash
flyctl launch
flyctl secrets set SECRET_KEY="your-secret"
flyctl secrets set JWT_SECRET_KEY="your-jwt"
flyctl secrets set ANTHROPIC_API_KEY="your-api-key"
flyctl deploy
```

---

## 4️⃣ 數據庫遷移（如果使用 PostgreSQL）

### 使用 Render 的 PostgreSQL

1. 在 Render 創建 PostgreSQL 實例
2. 獲取 `DATABASE_URL`（形如 `postgresql://user:pass@host:5432/db`）
3. 更新後端環境變數
4. 運行遷移（如果有 Flask-Migrate）：

```bash
railway run python -m flask db upgrade
```

---

## 5️⃣ 自定義域名配置

### Cloudflare Pages（前端）

1. 前往 **Custom domains**
2. 添加域名：`app.yourdomain.com`
3. 在 DNS 設置中添加 CNAME 記錄：
   ```
   app.yourdomain.com → lit-review-tool.pages.dev
   ```

### Render（後端）

1. 前往 **Settings** → **Custom Domain**
2. 添加：`api.yourdomain.com`
3. 在 DNS 添加 CNAME：
   ```
   api.yourdomain.com → litreview-backend.onrender.com
   ```

---

## 6️⃣ 環境變數完整清單

### 後端環境變數

| 變數名稱 | 說明 | 範例 | 必需 |
|---------|------|------|------|
| `DATABASE_URL` | 數據庫連接 | `sqlite:///...` 或 `postgresql://...` | ✅ |
| `SECRET_KEY` | Flask 密鑰 | 隨機字串（32+ 字符） | ✅ |
| `JWT_SECRET_KEY` | JWT 密鑰 | 隨機字串（32+ 字符） | ✅ |
| `ANTHROPIC_API_KEY` | Claude API Key | `sk-ant-...` | ✅ |
| `CORS_ORIGINS` | 允許的前端域名 | `https://app.yourdomain.com` | ✅ |
| `PORT` | 服務端口 | `5001` | ❌ |

### 前端環境變數

| 變數名稱 | 說明 | 範例 | 必需 |
|---------|------|------|------|
| `VITE_API_URL` | 後端 API 地址 | `https://api.yourdomain.com` | ✅ |

---

## 7️⃣ 安全性檢查

### 生產環境必做

- [ ] 更改所有默認密鑰
- [ ] 啟用 HTTPS（Cloudflare/Render 自動提供）
- [ ] 設置 CORS 白名單（不要用 `*`）
- [ ] 數據庫定期備份
- [ ] 設置 API 速率限制
- [ ] 監控錯誤日誌

### 建議添加的安全措施

```python
# backend/app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

---

## 8️⃣ 監控與維護

### Cloudflare Analytics

- 自動提供流量、效能分析
- 查看：**Analytics & Logs** 標籤

### 後端日誌（Render）

```bash
# 查看即時日誌
render logs -s litreview-backend

# 或在 Dashboard 的 Logs 標籤查看
```

### 錯誤追蹤（可選）

集成 Sentry：
```bash
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

---

## 9️⃣ CI/CD 自動部署

### GitHub Actions

創建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Build Frontend
        run: |
          cd frontend
          npm install
          npm run build

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: lit-review-tool
          directory: frontend/dist
```

---

## 🔟 完整部署流程總結

```bash
# 1. 推送到 GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Cloudflare Pages 自動部署前端
# → 前往 https://lit-review-tool.pages.dev

# 3. Render/Railway 部署後端
# → 前往 Render Dashboard 或使用 Railway CLI

# 4. 更新前端環境變數
# → 在 Cloudflare 設置 VITE_API_URL

# 5. 測試線上版本
curl https://litreview-backend.onrender.com/
# 應該返回 API 資訊

# 6. 開始使用！
# → https://lit-review-tool.pages.dev
```

---

## 📱 部署後測試清單

- [ ] 訪問前端 URL 正常顯示
- [ ] 可以註冊新帳戶
- [ ] 可以登入
- [ ] 可以創建專案
- [ ] 可以上傳 PDF
- [ ] AI 分析功能正常（需要 API Key）
- [ ] 網絡分析顯示正常
- [ ] 閱讀視圖功能完整

---

## ❓ 常見問題

### Q: 為什麼 Cloudflare Pages 構建失敗？

A: 確認：
1. `Build command` 路徑正確：`cd frontend && npm install && npm run build`
2. `Build output directory` 是 `frontend/dist`
3. Node 版本相容（設置環境變數 `NODE_VERSION=18`）

### Q: 後端 API 無法連接？

A: 檢查：
1. CORS 設置包含前端域名
2. 環境變數正確設置
3. 後端服務正在運行（查看 Render logs）

### Q: 資料庫重啟後數據丟失？

A:
- 免費方案的 Render 可能會清除檔案系統
- 考慮使用 PostgreSQL 或外部存儲
- 設置定期備份腳本

### Q: API Key 如何安全管理？

A:
1. **絕對不要** commit 到 GitHub
2. 使用平台的 **Secrets/Environment Variables** 功能
3. 讓用戶在設置頁面輸入自己的 API Key

---

## 📞 需要幫助？

- GitHub Issues: `https://github.com/YOUR_USERNAME/lit-review-tool/issues`
- Cloudflare Docs: https://developers.cloudflare.com/pages/
- Render Docs: https://render.com/docs

---

## ✅ 部署完成！

恭喜！你的博碩士生文獻管理工具已成功部署到雲端。

下一步：
1. 📢 分享給其他博碩士生使用
2. 📝 收集用戶反饋
3. 🚀 持續優化功能
