#!/usr/bin/env python3
"""
測試 Anthropic API Key 並列出可用的模型
"""

import anthropic
import sys

def test_api_key(api_key):
    """測試 API Key 是否有效"""

    print(f"🔑 測試 API Key: {api_key[:20]}...")
    print()

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # 測試的模型列表（從最新到最舊）
        models_to_test = [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

        print("📋 測試可用的模型：\n")

        available_models = []

        for model in models_to_test:
            try:
                # 發送最小的測試請求
                response = client.messages.create(
                    model=model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )

                print(f"✅ {model} - 可用")
                available_models.append(model)

            except anthropic.NotFoundError:
                print(f"❌ {model} - 不可用 (404 Not Found)")
            except anthropic.PermissionDeniedError:
                print(f"⚠️  {model} - 權限不足")
            except Exception as e:
                print(f"❌ {model} - 錯誤: {str(e)[:50]}")

        print()

        if available_models:
            print(f"🎉 找到 {len(available_models)} 個可用模型：")
            for model in available_models:
                print(f"   - {model}")
            print()
            print(f"💡 建議使用：{available_models[0]}")
        else:
            print("⚠️  沒有找到可用的模型")
            print()
            print("可能的原因：")
            print("1. API Key 尚未激活（需要先在 Anthropic Console 儲值）")
            print("2. API Key 已過期或被撤銷")
            print("3. 帳戶尚未完成驗證")
            print()
            print("請前往 https://console.anthropic.com/ 檢查你的 API Key 狀態")

    except anthropic.AuthenticationError:
        print("❌ API Key 無效或已過期")
        print("請確認你的 API Key 是否正確")
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 test_api_key.py YOUR_API_KEY")
        sys.exit(1)

    api_key = sys.argv[1]
    test_api_key(api_key)
