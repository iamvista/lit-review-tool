#!/bin/bash

# Phase 4 網絡分析功能測試腳本

echo "==========================================================="
echo "Phase 4 網絡分析功能測試"
echo "==========================================================="

BASE_URL="http://localhost:5001"

# 1. 登入
echo ""
echo "[1] 登入..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"phase4@test.com","password":"test1234"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "✗ 登入失敗"
  echo "請先創建測試用戶:"
  echo "  curl -X POST $BASE_URL/api/auth/register \\"
  echo "    -H 'Content-Type: application/json' \\"
  echo "    -d '{\"username\":\"test\",\"email\":\"test@example.com\",\"password\":\"password123\"}'"
  exit 1
fi

echo "✓ 登入成功"

# 2. 獲取專案
echo ""
echo "[2] 獲取專案..."
PROJECTS=$(curl -s -X GET "$BASE_URL/api/projects" \
  -H "Authorization: Bearer $TOKEN")

PROJECT_ID=$(echo $PROJECTS | python3 -c "import sys, json; projects = json.load(sys.stdin).get('projects', []); print(projects[0]['id'] if projects else '')" 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
  echo "  創建新專案..."
  CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/projects" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"深度學習網絡測試","description":"測試網絡分析","domain":"deep_learning"}')

  PROJECT_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['project']['id'])" 2>/dev/null)
  echo "✓ 專案創建成功 (ID: $PROJECT_ID)"
else
  echo "✓ 使用現有專案 (ID: $PROJECT_ID)"
fi

# 3. 導入 BibTeX
echo ""
echo "[3] 導入 BibTeX 論文..."
BIBTEX_CONTENT='@article{lecun1998,title={Gradient-based learning},author={LeCun, Yann and Bottou, Leon and Bengio, Yoshua},journal={Proceedings of the IEEE},year={1998}}
@article{hinton2012,title={Improving neural networks},author={Hinton, Geoffrey E and Krizhevsky, Alex and Sutskever, Ilya},journal={arXiv preprint},year={2012}}
@article{krizhevsky2012,title={Imagenet classification},author={Krizhevsky, Alex and Sutskever, Ilya and Hinton, Geoffrey E},journal={NeurIPS},year={2012}}
@article{he2016,title={Deep residual learning},author={He, Kaiming and Zhang, Xiangyu and Ren, Shaoqing},journal={CVPR},year={2016}}'

IMPORT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/papers/import/bibtex" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\":$PROJECT_ID,\"bibtex_content\":\"$BIBTEX_CONTENT\"}")

echo "$IMPORT_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"✓ 成功導入 {data.get('count', 0)} 篇論文\")" 2>/dev/null || echo "✗ 導入可能失敗"

# 4. 執行網絡分析
echo ""
echo "[4] 執行網絡分析..."
ANALYZE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/network/projects/$PROJECT_ID/analyze" \
  -H "Authorization: Bearer $TOKEN")

echo "$ANALYZE_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('success'):
    print('✓ 網絡分析完成')
    print(f\"  - 總作者數: {data.get('total_authors', 0)}\")
    print(f\"  - 關鍵人物數: {data.get('key_people_count', 0)}\")
    stats = data.get('statistics', {})
    print(f\"  - 合作關係: {stats.get('total_collaborations', 0)}\")
    print(f\"  - 網絡密度: {stats.get('network_density', 0):.4f}\")
else:
    print('✗ 網絡分析失敗:', data.get('error', 'Unknown'))
" 2>/dev/null || echo "✗ 網絡分析失敗"

# 5. 獲取關鍵人物
echo ""
echo "[5] 獲取關鍵人物列表..."
KEY_PEOPLE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/network/projects/$PROJECT_ID/key-people" \
  -H "Authorization: Bearer $TOKEN")

echo "$KEY_PEOPLE_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
key_people = data.get('key_people', [])
print(f'✓ 獲取 {len(key_people)} 位關鍵人物')
print('')
print('關鍵人物 Top 5:')
for i, person in enumerate(key_people[:5], 1):
    print(f\"  {i}. {person['name']}\")
    print(f\"     - 論文數: {person.get('papers_in_project', 0)}\")
    print(f\"     - 影響力分數: {person.get('influence_score', 0):.2f}\")
" 2>/dev/null || echo "✗ 獲取關鍵人物失敗"

# 6. 獲取網絡數據
echo ""
echo "[6] 獲取網絡可視化數據..."
NETWORK_RESPONSE=$(curl -s -X GET "$BASE_URL/api/network/projects/$PROJECT_ID/network" \
  -H "Authorization: Bearer $TOKEN")

echo "$NETWORK_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
network = data.get('network', {})
nodes = network.get('nodes', [])
links = network.get('links', [])
print(f'✓ 網絡數據獲取成功')
print(f'  - 節點數: {len(nodes)}')
print(f'  - 連線數: {len(links)}')
" 2>/dev/null || echo "✗ 獲取網絡數據失敗"

echo ""
echo "==========================================================="
echo "Phase 4 功能測試完成！"
echo "==========================================================="
echo ""
echo "✨ 您可以訪問以下 URL 查看網絡可視化:"
echo "   http://localhost:5173/projects/$PROJECT_ID/network"
echo "==========================================================="
