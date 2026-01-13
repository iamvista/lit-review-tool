#!/usr/bin/env python3
"""
測試 Phase 4 網絡分析功能
"""

import requests
import json

BASE_URL = "http://localhost:5001"

# 測試用的 BibTeX 數據
TEST_BIBTEX = """
@article{lecun1998,
  title={Gradient-based learning applied to document recognition},
  author={LeCun, Yann and Bottou, Leon and Bengio, Yoshua and Haffner, Patrick},
  journal={Proceedings of the IEEE},
  year={1998}
}

@article{krizhevsky2012,
  title={Imagenet classification with deep convolutional neural networks},
  author={Krizhevsky, Alex and Sutskever, Ilya and Hinton, Geoffrey E},
  journal={Advances in neural information processing systems},
  year={2012}
}

@article{simonyan2014,
  title={Very deep convolutional networks for large-scale image recognition},
  author={Simonyan, Karen and Zisserman, Andrew},
  journal={arXiv preprint arXiv:1409.1556},
  year={2014}
}

@article{he2016,
  title={Deep residual learning for image recognition},
  author={He, Kaiming and Zhang, Xiangyu and Ren, Shaoqing and Sun, Jian},
  journal={Proceedings of the IEEE conference on computer vision and pattern recognition},
  year={2016}
}

@article{hinton2012,
  title={Improving neural networks by preventing co-adaptation of feature detectors},
  author={Hinton, Geoffrey E and Srivastava, Nitish and Krizhevsky, Alex and Sutskever, Ilya and Salakhutdinov, Ruslan R},
  journal={arXiv preprint arXiv:1207.0580},
  year={2012}
}
"""

def test_phase4():
    print("=" * 60)
    print("Phase 4 網絡分析功能測試")
    print("=" * 60)

    # 1. 登入
    print("\n[1] 登入...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }

    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)

    if response.status_code == 200:
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("✓ 登入成功")
    else:
        print("✗ 登入失敗，請先創建測試用戶")
        print("  可以執行: curl -X POST http://localhost:5001/api/auth/register \\")
        print("            -H 'Content-Type: application/json' \\")
        print("            -d '{\"username\":\"test\",\"email\":\"test@example.com\",\"password\":\"password123\"}'")
        return

    # 2. 獲取或創建專案
    print("\n[2] 獲取專案列表...")
    response = requests.get(f"{BASE_URL}/api/projects", headers=headers)
    projects = response.json()['projects']

    if len(projects) > 0:
        project_id = projects[0]['id']
        print(f"✓ 使用現有專案 (ID: {project_id})")
    else:
        print("  創建新專案...")
        project_data = {
            "name": "深度學習網絡分析測試",
            "description": "測試作者網絡分析功能",
            "domain": "deep_learning"
        }
        response = requests.post(f"{BASE_URL}/api/projects", json=project_data, headers=headers)
        project_id = response.json()['project']['id']
        print(f"✓ 專案創建成功 (ID: {project_id})")

    # 3. 導入 BibTeX 論文
    print("\n[3] 導入 BibTeX 論文...")
    import_data = {
        "project_id": project_id,
        "bibtex_content": TEST_BIBTEX
    }
    response = requests.post(f"{BASE_URL}/api/papers/import/bibtex", json=import_data, headers=headers)

    if response.status_code == 201:
        count = response.json()['count']
        print(f"✓ 成功導入 {count} 篇論文")
    else:
        print(f"✗ 導入失敗: {response.json().get('error', 'Unknown error')}")
        return

    # 4. 執行網絡分析
    print("\n[4] 執行網絡分析...")
    response = requests.post(f"{BASE_URL}/api/network/projects/{project_id}/analyze", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"✓ 網絡分析完成")
        print(f"  - 總作者數: {data['total_authors']}")
        print(f"  - 關鍵人物數: {data['key_people_count']}")
        print(f"  - 網絡統計: {json.dumps(data['statistics'], indent=2, ensure_ascii=False)}")
    else:
        print(f"✗ 網絡分析失敗: {response.json().get('error', 'Unknown error')}")
        return

    # 5. 獲取關鍵人物列表
    print("\n[5] 獲取關鍵人物列表...")
    response = requests.get(f"{BASE_URL}/api/network/projects/{project_id}/key-people", headers=headers)

    if response.status_code == 200:
        key_people = response.json()['key_people']
        print(f"✓ 獲取 {len(key_people)} 位關鍵人物")
        print("\n關鍵人物 Top 5:")
        for i, person in enumerate(key_people[:5], 1):
            print(f"  {i}. {person['name']}")
            print(f"     - 論文數: {person.get('papers_in_project', 0)}")
            print(f"     - 影響力分數: {person.get('influence_score', 0):.2f}")
            print(f"     - 是否關鍵人物: {'是' if person.get('is_key_person') else '否'}")
    else:
        print(f"✗ 獲取關鍵人物失敗: {response.json().get('error', 'Unknown error')}")
        return

    # 6. 獲取網絡數據（用於可視化）
    print("\n[6] 獲取網絡可視化數據...")
    response = requests.get(f"{BASE_URL}/api/network/projects/{project_id}/network", headers=headers)

    if response.status_code == 200:
        network_data = response.json()['network']
        print(f"✓ 網絡數據獲取成功")
        print(f"  - 節點數: {len(network_data['nodes'])}")
        print(f"  - 連線數: {len(network_data['links'])}")
    else:
        print(f"✗ 獲取網絡數據失敗: {response.json().get('error', 'Unknown error')}")
        return

    # 7. 測試作者詳情
    print("\n[7] 測試作者詳情 API...")
    if len(key_people) > 0:
        author_id = key_people[0]['id']
        response = requests.get(f"{BASE_URL}/api/network/authors/{author_id}", headers=headers)

        if response.status_code == 200:
            author_data = response.json()
            print(f"✓ 作者詳情獲取成功")
            print(f"  - 作者名稱: {author_data['author']['name']}")
            print(f"  - 論文數: {len(author_data['papers'])}")
            print(f"  - 合作者數: {len(author_data['collaborators'])}")
        else:
            print(f"✗ 獲取作者詳情失敗: {response.json().get('error', 'Unknown error')}")

    print("\n" + "=" * 60)
    print("Phase 4 功能測試完成！")
    print("=" * 60)
    print(f"\n✨ 您可以訪問以下 URL 查看網絡可視化:")
    print(f"   http://localhost:5173/projects/{project_id}/network")
    print("=" * 60)

if __name__ == "__main__":
    test_phase4()
