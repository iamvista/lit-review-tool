# LitReview Tool - 部署指南

## 生產環境部署步驟

### 1. 環境準備

#### 系統要求
- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB RAM
- 至少 10GB 磁碟空間

#### 必需的服務
- PostgreSQL 15+（或使用 Docker Compose 提供的）
- （可選）Nginx 反向代理

### 2. 環境變數配置

#### 後端環境變數

複製 `backend/.env.production.example` 為 `backend/.env.production`：

```bash
cp backend/.env.production.example backend/.env.production
```

編輯 `.env.production` 並填入實際值：

```bash
# 必須修改
SECRET_KEY=生成一個隨機的長字串
JWT_SECRET_KEY=另一個隨機的長字串
DATABASE_URL=postgresql://user:password@host:5432/dbname

# 設置前端 URL（重要！）
CORS_ORIGINS=https://yourdomain.com

# AI 功能（可選）
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

**生成安全的密鑰**:
```bash
# 生成 SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成 JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 前端環境變數

創建 `frontend/.env.production`：

```bash
VITE_API_URL=https://api.yourdomain.com
```

### 3. 數據庫設置

#### 選項 A: 使用外部 PostgreSQL

1. 創建數據庫：
```sql
CREATE DATABASE litreview_prod;
CREATE USER litreview_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE litreview_prod TO litreview_user;
```

2. 更新 `DATABASE_URL` 指向外部數據庫

#### 選項 B: 使用 Docker Compose 的 PostgreSQL

1. 更新 `docker-compose.yml` 中的數據庫密碼
2. 數據庫數據將保存在 Docker volume 中

### 4. 構建和部署

#### 使用 Docker Compose（推薦）

```bash
# 1. 構建 Docker 映像
docker-compose build

# 2. 啟動服務
docker-compose up -d

# 3. 檢查容器狀態
docker-compose ps

# 4. 查看日誌
docker-compose logs -f
```

#### 初始化數據庫

```bash
# 進入後端容器
docker-compose exec backend bash

# 運行數據庫遷移
flask db upgrade

# 或使用 Python 直接創建表
python3 -c "from app import create_app; from models import db; app = create_app('production'); app.app_context().push(); db.create_all()"
```

### 5. Nginx 反向代理配置（推薦）

創建 `/etc/nginx/sites-available/litreview`：

```nginx
# 後端 API
server {
    listen 80;
    server_name api.yourdomain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL 憑證
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    # 代理到後端
    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支援（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 文件上傳大小限制
    client_max_body_size 20M;
}

# 前端應用
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # HMR (開發模式)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

啟用站點：
```bash
sudo ln -s /etc/nginx/sites-available/litreview /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL/TLS 憑證（Let's Encrypt）

```bash
# 安裝 certbot
sudo apt-get install certbot python3-certbot-nginx

# 獲取憑證
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# 自動續約
sudo certbot renew --dry-run
```

### 7. 系統服務配置（開機自啟）

創建 systemd 服務 `/etc/systemd/system/litreview.service`：

```ini
[Unit]
Description=LitReview Tool
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/lit-review-tool
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

啟用服務：
```bash
sudo systemctl enable litreview
sudo systemctl start litreview
```

### 8. 監控和日誌

#### 查看應用日誌
```bash
# 所有服務的日誌
docker-compose logs -f

# 只看後端
docker-compose logs -f backend

# 只看前端
docker-compose logs -f frontend

# 只看數據庫
docker-compose logs -f db
```

#### 健康檢查
```bash
# 檢查後端健康
curl https://api.yourdomain.com/health

# 預期回應
# {"status": "healthy", "service": "litreview-tool", "version": "1.0.0"}
```

### 9. 備份策略

#### 數據庫備份

創建備份腳本 `/opt/scripts/backup_litreview.sh`：

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/litreview"
DB_NAME="litreview_prod"

mkdir -p $BACKUP_DIR

# 備份數據庫
docker-compose exec -T db pg_dump -U postgres $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 保留最近 30 天的備份
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_$DATE.sql.gz"
```

設置每日自動備份（crontab）：
```bash
# 每天凌晨 2 點備份
0 2 * * * /opt/scripts/backup_litreview.sh >> /var/log/litreview_backup.log 2>&1
```

### 10. 性能優化

#### 後端優化

1. **使用生產級 WSGI 服務器**（Gunicorn）

更新 `backend/Dockerfile`:
```dockerfile
# 安裝 gunicorn
RUN pip install gunicorn

# 修改啟動命令
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--threads", "2", "app:create_app('production')"]
```

2. **啟用數據庫連接池**

在 `config.py` 中：
```python
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_MAX_OVERFLOW = 20
```

#### 前端優化

1. **構建生產版本**

更新 `frontend/Dockerfile`:
```dockerfile
# 構建階段
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 生產階段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

2. **啟用 Gzip 壓縮**（nginx.conf）

### 11. 安全檢查清單

- [ ] 所有密鑰使用隨機生成的強密碼
- [ ] 數據庫不直接暴露在公網
- [ ] 啟用 HTTPS（SSL/TLS）
- [ ] 配置 CORS 只允許可信域名
- [ ] 設置合理的文件上傳大小限制
- [ ] 定期備份數據庫
- [ ] 監控日誌中的異常活動
- [ ] 更新依賴項以修復安全漏洞
- [ ] 配置防火牆規則

### 12. 故障排除

#### 後端無法啟動

```bash
# 檢查後端日誌
docker-compose logs backend

# 常見問題：
# 1. 數據庫連接失敗 → 檢查 DATABASE_URL
# 2. 端口被佔用 → 檢查 5001 端口是否被使用
# 3. 環境變數缺失 → 檢查 .env.production
```

#### 前端無法連接後端

```bash
# 檢查前端環境變數
cat frontend/.env.production

# 檢查 CORS 配置
# backend/config.py 中的 CORS_ORIGINS 是否包含前端域名
```

#### 數據庫遷移失敗

```bash
# 重置數據庫（警告：會清空所有數據）
docker-compose down -v
docker-compose up -d
```

### 13. 擴展部署

#### 使用 Docker Swarm 或 Kubernetes

對於大規模部署，考慮使用容器編排工具：

- Docker Swarm: 適合中小型部署
- Kubernetes: 適合大規模、高可用部署

#### 多實例部署

在負載均衡器後運行多個後端實例：

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
    ports:
      - "5001-5003:5001"
```

## 維護指南

### 定期任務

1. **每週**：檢查日誌是否有異常
2. **每月**：更新依賴項
3. **每季**：審查安全性
4. **每年**：更新 SSL 憑證（如果未自動續約）

### 更新應用

```bash
# 1. 拉取最新代碼
git pull origin main

# 2. 重新構建
docker-compose build

# 3. 滾動更新（零停機）
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend

# 4. 檢查狀態
docker-compose ps
```

---

**需要幫助？** 查看項目 Issues 或文檔獲取更多信息。
