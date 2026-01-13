#!/bin/bash
# 開發環境啟動腳本

echo "🚀 啟動 LitReview Tool 後端..."

# 停止舊的後端進程
pkill -9 -f "python.*app.py" 2>/dev/null
sleep 1

# 設定環境變數
export PORT=5001
export FLASK_ENV=development

# 選擇資料庫
if [ "$1" = "sqlite" ]; then
    echo "📦 使用 SQLite 資料庫"
    export DATABASE_URL='sqlite:///litreview.db'
else
    echo "🐘 使用 PostgreSQL 資料庫"
    # 使用默認的 PostgreSQL 配置
fi

# 啟動後端
echo "✨ 啟動 Flask 服務器..."
python3 app.py

# 如果想要背景運行，使用:
# python3 app.py > /tmp/backend.log 2>&1 &
# echo "✅ 後端已在背景啟動（PID: $!）"
# echo "📝 日誌文件: /tmp/backend.log"
