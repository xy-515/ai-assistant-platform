"""Test the three async paper API endpoints"""
import requests

BASE = "http://localhost:8001"

# 1. Login (or register if new)
print("1. Login...")
r = requests.post(f"{BASE}/api/auth/login/", json={
    "username": "testuser", "password": "test1234"
})
if r.status_code != 200:
    print("   Registering new user...")
    r = requests.post(f"{BASE}/api/auth/register/", json={
        "username": "testuser", "email": "t@t.com", "password": "test1234"
    })
token = r.json()["token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"   Token: {token[:30]}... OK")

# 2. Test Outline
print("\n2. POST /api/paper/outline")
r = requests.post(f"{BASE}/api/paper/outline", headers=headers, json={
    "title": "基于深度学习的智能代码测试生成平台设计与实现"
})
d = r.json()
print(f"   Status: {r.status_code}")
print(f"   ID: {d.get('id')}")
print(f"   Outline preview: {d.get('outline', '')[:120]}...")
assert r.status_code == 200, f"Expected 200, got {r.status_code}"
assert "id" in d and "outline" in d, "Missing fields"

# 3. Test Polish (academic)
print("\n3. POST /api/paper/polish (academic)")
r = requests.post(f"{BASE}/api/paper/polish", headers=headers, json={
    "text": "本文实现了一个代码测试工具，可以自动生成测试用例并运行。",
    "mode": "academic"
})
d = r.json()
print(f"   Status: {r.status_code}")
print(f"   ID: {d.get('id')}, mode: {d.get('mode')}")
print(f"   Polished preview: {d.get('polished', '')[:120]}...")
assert r.status_code == 200

# 4. Test Polish (concise)
print("\n4. POST /api/paper/polish (concise)")
r = requests.post(f"{BASE}/api/paper/polish", headers=headers, json={
    "text": "在当前的学术研究和工程实践中，深度学习技术正在被越来越广泛地应用于各种各样的不同领域中。",
    "mode": "concise"
})
d = r.json()
print(f"   Status: {r.status_code}, mode: {d.get('mode')}")
assert r.status_code == 200

# 5. Test Polish (deweight)
print("\n5. POST /api/paper/polish (deweight)")
r = requests.post(f"{BASE}/api/paper/polish", headers=headers, json={
    "text": "随着人工智能技术的快速发展，深度学习在各个领域都取得了显著的成果。",
    "mode": "deweight"
})
d = r.json()
print(f"   Status: {r.status_code}, mode: {d.get('mode')}")
assert r.status_code == 200

# 6. Test Feedback
print("\n6. POST /api/paper/feedback")
r = requests.post(f"{BASE}/api/paper/feedback", headers=headers, json={
    "fragment": (
        "2.1 系统架构\n"
        "本系统采用微服务架构，包括用户管理、任务调度、测试生成、"
        "沙箱执行等模块。前端使用React框架，后端使用Spring Boot。"
    )
})
d = r.json()
print(f"   Status: {r.status_code}")
print(f"   ID: {d.get('id')}")
print(f"   Feedback preview: {d.get('feedback', '')[:120]}...")
assert r.status_code == 200

# 7. Test auth (no token)
print("\n7. No auth test...")
r = requests.post(f"{BASE}/api/paper/outline", json={"title": "test"})
print(f"   Status: {r.status_code} (expected 401)")
assert r.status_code == 401

# 8. Test invalid mode
print("\n8. Invalid mode test...")
r = requests.post(f"{BASE}/api/paper/polish", headers=headers, json={
    "text": "test", "mode": "invalid"
})
print(f"   Status: {r.status_code} (expected 400)")
assert r.status_code == 400

# 9. Verify history saved
print("\n9. Check history...")
r = requests.get(f"{BASE}/api/history/paper/?page=1", headers=headers)
d = r.json()
print(f"   Records saved: {d['count']}")
assert d['count'] >= 5, f"Expected >=5 records, got {d['count']}"

print("\n" + "=" * 50)
print("ALL 9 TESTS PASSED")
