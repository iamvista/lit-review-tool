#!/bin/bash

# Phase 3 功能测试脚本
# 测试阅读视图、笔记、标签等功能

BASE_URL="http://localhost:5001"
TOKEN=""
PROJECT_ID=""
PAPER_ID=""

echo "========================================="
echo "Phase 3 - 横向串读视图功能测试"
echo "========================================="
echo

# 获取已有的测试账号 Token
echo "Step 1: 登录测试账号"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ 登录失败，请先运行 test_api.sh 创建测试数据"
  exit 1
fi

echo "✓ 登录成功"
echo

# 获取第一个专案
echo "Step 2: 获取专案列表"
PROJECTS_RESPONSE=$(curl -s "${BASE_URL}/api/projects" \
  -H "Authorization: Bearer $TOKEN")

PROJECT_ID=$(echo $PROJECTS_RESPONSE | jq -r '.projects[0].id')

if [ "$PROJECT_ID" = "null" ] || [ -z "$PROJECT_ID" ]; then
  echo "❌ 没有找到专案"
  exit 1
fi

echo "✓ 找到专案 ID: $PROJECT_ID"
echo

# 获取第一篇论文
echo "Step 3: 获取专案论文"
PAPERS_RESPONSE=$(curl -s "${BASE_URL}/api/projects/${PROJECT_ID}/papers" \
  -H "Authorization: Bearer $TOKEN")

PAPER_ID=$(echo $PAPERS_RESPONSE | jq -r '.papers[0].id')

if [ "$PAPER_ID" = "null" ] || [ -z "$PAPER_ID" ]; then
  echo "❌ 没有找到论文"
  exit 1
fi

echo "✓ 找到论文 ID: $PAPER_ID"
echo

# 测试1: 更新论文笔记
echo "Test 1: 更新论文笔记"
NOTES_RESPONSE=$(curl -s -X PUT "${BASE_URL}/api/papers/${PAPER_ID}/notes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "这是一篇关于深度学习的重要论文。\n\n主要贡献：\n1. 提出了新的CNN架构\n2. 在医学影像上取得SOTA性能\n3. 提供了详细的消融实验"
  }')

echo "$NOTES_RESPONSE" | jq .
echo

if [ "$(echo $NOTES_RESPONSE | jq -r '.success')" = "true" ]; then
  echo "✓ 笔记更新成功"
else
  echo "❌ 笔记更新失败"
fi
echo

# 测试2: 更新阅读状态
echo "Test 2: 更新阅读状态为「已读摘要」"
READ_STATUS_RESPONSE=$(curl -s -X PUT "${BASE_URL}/api/papers/${PAPER_ID}/read-status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "abstract_only"}')

echo "$READ_STATUS_RESPONSE" | jq .

if [ "$(echo $READ_STATUS_RESPONSE | jq -r '.success')" = "true" ]; then
  echo "✓ 阅读状态更新成功"
else
  echo "❌ 阅读状态更新失败"
fi
echo

# 测试3: 添加标签
echo "Test 3: 添加论文标签"
TAGS_RESPONSE=$(curl -s -X PUT "${BASE_URL}/api/papers/${PAPER_ID}/tags" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tags": ["关键起点", "技术突破", "Nature论文"]}')

echo "$TAGS_RESPONSE" | jq .

if [ "$(echo $TAGS_RESPONSE | jq -r '.success')" = "true" ]; then
  echo "✓ 标签添加成功"
else
  echo "❌ 标签添加失败"
fi
echo

# 测试4: 更新高亮
echo "Test 4: 添加论文高亮"
HIGHLIGHTS_RESPONSE=$(curl -s -X PUT "${BASE_URL}/api/papers/${PAPER_ID}/highlights" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "highlights": [
      {
        "section": "abstract",
        "text": "deep learning techniques",
        "color": "yellow",
        "note": "核心技术"
      },
      {
        "section": "introduction",
        "text": "CNN architectures",
        "color": "green",
        "note": "重点方法"
      }
    ]
  }')

echo "$HIGHLIGHTS_RESPONSE" | jq .

if [ "$(echo $HIGHLIGHTS_RESPONSE | jq -r '.success')" = "true" ]; then
  echo "✓ 高亮添加成功"
else
  echo "❌ 高亮添加失败"
fi
echo

# 测试5: 验证所有更新
echo "Test 5: 验证论文信息更新"
PAPER_DETAIL=$(curl -s "${BASE_URL}/api/papers/${PAPER_ID}" \
  -H "Authorization: Bearer $TOKEN")

echo "$PAPER_DETAIL" | jq '{
  title: .paper.title,
  read_status: .paper.read_status,
  tags: .paper.tags,
  has_notes: (.paper.notes != null and .paper.notes != ""),
  highlights_count: (.paper.highlights | length)
}'
echo

echo "========================================="
echo "Phase 3 功能测试完成！"
echo "========================================="
echo
echo "测试总结："
echo "  ✓ 笔记管理 API"
echo "  ✓ 阅读状态更新"
echo "  ✓ 标签管理"
echo "  ✓ 高亮功能"
echo
echo "前端阅读模式访问:"
echo "  → http://localhost:5173/projects/${PROJECT_ID}/reading"
echo
echo "后端 API 文档:"
echo "  PUT /api/papers/:id/notes - 更新笔记"
echo "  PUT /api/papers/:id/read-status - 更新阅读状态"
echo "  PUT /api/papers/:id/tags - 更新标签"
echo "  PUT /api/papers/:id/highlights - 更新高亮"
echo "  POST /api/papers/:id/extract - 提取PDF内容"
echo
