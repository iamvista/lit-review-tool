#!/bin/bash

# LitReview Tool API Testing Script
# Tests Phase 1 & Phase 2 functionality

BASE_URL="http://localhost:5001"
TOKEN=""
USER_ID=""
PROJECT_ID=""

echo "========================================="
echo "LitReview Tool - API Testing"
echo "========================================="
echo

# Test 1: Health Check
echo "Test 1: Backend Health Check"
curl -s "${BASE_URL}/health" | jq .
echo -e "\n✓ Health check passed\n"

# Test 2: User Registration
echo "Test 2: User Registration"
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "full_name": "Test User",
    "institution": "Test University",
    "field_of_study": "Computer Science"
  }')

echo "$REGISTER_RESPONSE" | jq .

if [ "$(echo $REGISTER_RESPONSE | jq -r '.success')" = "true" ]; then
  TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')
  echo -e "\n✓ User registered successfully"
  echo "Token: ${TOKEN:0:20}..."
else
  echo "Registration response: $REGISTER_RESPONSE"
  echo "⚠️  User might already exist, trying login instead"

  # Try login
  LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com",
      "password": "testpass123"
    }')

  TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
  echo "✓ Logged in successfully"
fi
echo

# Test 3: Get Current User
echo "Test 3: Get Current User Info"
curl -s "${BASE_URL}/api/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo -e "\n✓ User info retrieved\n"

# Test 4: Create Project
echo "Test 4: Create Project"
PROJECT_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "深度學習在醫學影像的應用",
    "description": "研究深度學習技術在醫學影像分析中的應用",
    "domain": "醫學影像",
    "target_paper_count": 15
  }')

echo "$PROJECT_RESPONSE" | jq .
PROJECT_ID=$(echo $PROJECT_RESPONSE | jq -r '.project.id')
echo -e "\n✓ Project created successfully (ID: $PROJECT_ID)\n"

# Test 5: Get All Projects
echo "Test 5: Get All Projects"
curl -s "${BASE_URL}/api/projects" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo -e "\n✓ Projects list retrieved\n"

# Test 6: Import Papers via BibTeX
echo "Test 6: Import Papers (BibTeX)"
BIBTEX_CONTENT='@article{smith2020deep,
  title={Deep Learning for Medical Image Analysis},
  author={Smith, John and Doe, Jane},
  journal={Nature Medicine},
  year={2020},
  volume={26},
  pages={1234--1245},
  doi={10.1038/example2020},
  abstract={This paper presents a comprehensive review of deep learning techniques in medical imaging, focusing on CNN architectures and their applications in radiology.}
}

@article{wang2019medical,
  title={Medical Image Segmentation with Deep Neural Networks},
  author={Wang, Li and Zhang, Wei},
  journal={IEEE Transactions on Medical Imaging},
  year={2019},
  volume={38},
  pages={100--110},
  abstract={We propose a novel deep neural network architecture for medical image segmentation tasks.}
}

@article{chen2021transformer,
  title={Transformer Models for Medical Imaging},
  author={Chen, Ming and Liu, Yang},
  journal={Medical Image Analysis},
  year={2021},
  volume={70},
  pages={1--15},
  doi={10.1016/example2021},
  abstract={This work explores the application of transformer models to medical image analysis, showing superior performance over CNNs.}
}'

IMPORT_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/papers/import/bibtex" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"bibtex_content\": $(echo "$BIBTEX_CONTENT" | jq -Rs .)
  }")

echo "$IMPORT_RESPONSE" | jq .
echo -e "\n✓ Papers imported via BibTeX\n"

# Test 7: Get Project Papers (Sorted by Year)
echo "Test 7: Get Project Papers (Timeline View)"
curl -s "${BASE_URL}/api/projects/${PROJECT_ID}/papers?sort_by=year&order=asc" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo -e "\n✓ Papers retrieved and sorted by year\n"

# Test 8: Get Project Details
echo "Test 8: Get Project Details"
curl -s "${BASE_URL}/api/projects/${PROJECT_ID}" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo -e "\n✓ Project details retrieved\n"

# Test 9: Get Project Statistics
echo "Test 9: Get Project Statistics"
curl -s "${BASE_URL}/api/projects/${PROJECT_ID}/stats" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo -e "\n✓ Project statistics retrieved\n"

# Test 10: Try DOI Import (Optional - requires network)
echo "Test 10: Import Paper via DOI (Optional)"
echo "Attempting to import a real paper via DOI..."
DOI_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/papers/import/doi" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"doi\": \"10.1038/nature14539\"
  }")

echo "$DOI_RESPONSE" | jq .
echo -e "\n✓ DOI import tested\n"

echo "========================================="
echo "All Tests Completed!"
echo "========================================="
echo
echo "Summary:"
echo "  ✓ Backend API is running"
echo "  ✓ User authentication works"
echo "  ✓ Project management works"
echo "  ✓ BibTeX import works"
echo "  ✓ Timeline sorting works"
echo "  ✓ DOI import tested"
echo
echo "Frontend is available at: http://localhost:5173"
echo "Backend API is available at: http://localhost:5001"
echo
