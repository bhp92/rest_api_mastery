"""
solutions/week1/challenge.py — Week 1 challenge solution
"""
import requests
import uuid

BASE = "http://localhost:5000"


def main():
    # 1. Register a new unique user
    unique_id = uuid.uuid4().hex[:8]
    new_user = {
        "username":   f"learner_{unique_id}",
        "email":      f"learner_{unique_id}@example.com",
        "password":   "studypass123",
        "first_name": "Study",
        "last_name":  "Learner"
    }
    r = requests.post(f"{BASE}/api/v1/auth/register", json=new_user)
    assert r.status_code == 201, f"Registration failed: {r.json()}"
    print(f"✅ Registered: {new_user['username']}")

    # 2. Login as that user
    r = requests.post(f"{BASE}/api/v1/auth/login",
                      json={"username": new_user['username'], "password": new_user['password']})
    assert r.status_code == 200
    token = r.json()['data']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Logged in, token starts with: {token[:20]}...")

    # 3. Get all products filtered by category 'books'
    r = requests.get(f"{BASE}/api/v1/products", params={"category": "books"})
    assert r.status_code == 200
    books = r.json()['data']
    print(f"\n📚 Books available:")
    for book in books:
        print(f"   {book['name']:40} ${book['price']:.2f}")

    # 4. Get current user's profile
    r = requests.get(f"{BASE}/api/v1/auth/me", headers=headers)
    assert r.status_code == 200
    profile = r.json()['data']
    print(f"\n👤 My profile: {profile['first_name']} {profile['last_name']} ({profile['email']})")

    # 5. Logout
    r = requests.post(f"{BASE}/api/v1/auth/logout", headers=headers)
    assert r.status_code == 200
    print("\n✅ Logged out successfully")

    # Verify token is no longer valid
    r = requests.get(f"{BASE}/api/v1/auth/me", headers=headers)
    print(f"   Using old token after logout: {r.status_code} (expected 401)")


if __name__ == '__main__':
    main()
