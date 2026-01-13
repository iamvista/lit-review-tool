#!/usr/bin/env python3
"""
數據庫初始化腳本
在應用啟動前創建必要的目錄和數據庫表
"""

import os
import sys
from pathlib import Path

# 確保可以導入 app 模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db


def init_database():
    """初始化數據庫"""
    with app.app_context():
        # 確保 instance 目錄存在
        instance_path = Path(app.instance_path)
        instance_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Instance 目錄已創建: {instance_path}")

        # 創建所有數據庫表
        try:
            db.create_all()
            print("✓ 數據庫表已創建")

            # 驗證數據庫連接
            db.session.execute(db.text('SELECT 1'))
            print("✓ 數據庫連接正常")

            print("\n🎉 數據庫初始化成功！")
            return True

        except Exception as e:
            print(f"\n❌ 數據庫初始化失敗: {e}")
            return False


if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
