# Week 3 — Authentication & Security
**Time:** 40 min/day × 5 days | **Goal:** Implement and understand all auth patterns

---

## Day 1 — API Keys & Basic Auth (40 min)

### Theory (15 min)

**Three main auth approaches:**

| Method | How it works | Best for |
|--------|-------------|----------|
| API Key | `?api_key=xxx` or header | Server-to-server, simple |
| Basic Auth | Base64(user:pass) in header | Simple, internal APIs |
| JWT Bearer | Signed token in header | User auth, stateless |
| OAuth2 | Delegated access via 3rd party | "Login with Google" |

**API Key patterns:**
```
# In header (preferred — not logged in URLs)
X-API-Key: sk-abc123xyz

# In query param (avoid — gets logged)
GET /api?api_key=sk-abc123xyz

# In Authorization header
Authorization: ApiKey sk-abc123xyz
```

**Basic Auth:**
```
Authorization: Basic dXNlcjpwYXNz
# "dXNlcjpwYXNz" = base64("user:pass")
```

### Hands-on (25 min)
```python
# exercises/week3/day1_auth_patterns.py
import requests
import base64

BASE = "http://localhost:5000"

# 1. Simulate API Key auth pattern
def make_api_key_client(api_key):
    s = requests.Session()
    s.headers['X-API-Key'] = api_key
    return s

# 2. Simulate Basic Auth
def basic_auth_header(username, password):
    creds = f"{username}:{password}".encode('utf-8')
    b64 = base64.b64encode(creds).decode('utf-8')
    return {"Authorization": f"Basic {b64}"}

print("Basic auth header:", basic_auth_header("alice", "password123"))

# 3. JWT — inspect token payload
import json, base64

def decode_jwt_payload(token):
    """Decode JWT payload WITHOUT verifying signature (client-side inspection)"""
    parts = token.split('.')
    payload_b64 = parts[1]
    # Add padding
    payload_b64 += '=' * (4 - len(payload_b64) % 4)
    payload = json.loads(base64.b64decode(payload_b64))
    return payload

r = requests.post(f"{BASE}/api/v1/auth/login", json={"username":"alice","password":"password123"})
token = r.json()['data']['access_token']
payload = decode_jwt_payload(token)
print("\nJWT payload:", json.dumps(payload, indent=2))
print(f"Token expires at: {payload['exp']} (unix timestamp)")

import time
expires_in = payload['exp'] - time.time()
print(f"Expires in: {expires_in:.0f} seconds")
```

---

## Day 2 — JWT Deep Dive (40 min)

### Theory (20 min)

**JWT Structure:**
```
Header.Payload.Signature

Header:  {"alg": "HS256", "typ": "JWT"}
Payload: {"user_id": 1, "role": "admin", "exp": 1234567890}
Signature: HMAC-SHA256(header + "." + payload, secret_key)
```

**Why JWT is stateless:**
```
Traditional session auth:
  Login → server creates session → stores in DB → sends session_id cookie
  Each request → server looks up session_id in DB → gets user
  ❌ Requires DB lookup on every request
  ❌ Hard to scale horizontally

JWT auth:
  Login → server creates JWT → signs with secret → sends JWT
  Each request → server validates signature → extracts user from token
  ✅ No DB lookup needed (just crypto verification)
  ✅ Scales horizontally (any server knows the secret)
  ❌ Can't invalidate before expiry (use short expiry + refresh tokens)
```

**Access Token + Refresh Token pattern:**
```
Access Token:   expires in 30 minutes — used for API calls
Refresh Token:  expires in 7 days — used only to get new access token

Flow:
1. Login → get both tokens
2. Use access token for API calls
3. Access token expires
4. Use refresh token → get new access token
5. Refresh token expires → must login again
```

### Hands-on (20 min)
```python
# exercises/week3/day2_jwt.py
import requests, time, json

BASE = "http://localhost:5000"

class JWTSession:
    def __init__(self, base_url):
        self.base = base_url
        self.access_token = None
        self.refresh_token = None

    def login(self, username, password):
        r = requests.post(f"{self.base}/api/v1/auth/login",
                          json={"username": username, "password": password})
        data = r.json()['data']
        self.access_token  = data['access_token']
        self.refresh_token = data['refresh_token']
        print(f"✅ Logged in as {username}")
        return self

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def refresh(self):
        r = requests.post(f"{self.base}/api/v1/auth/refresh",
                          json={"refresh_token": self.refresh_token})
        if r.status_code == 200:
            self.access_token = r.json()['data']['access_token']
            print("✅ Token refreshed")
        else:
            print("❌ Refresh failed — must re-login")
        return self

    def get(self, path):
        r = requests.get(f"{self.base}{path}", headers=self._headers())
        if r.status_code == 401:
            print("⚠️  Token expired, refreshing...")
            self.refresh()
            r = requests.get(f"{self.base}{path}", headers=self._headers())
        return r

session = JWTSession(BASE).login("alice", "password123")
print(session.get("/api/v1/auth/me").json()['data'])
```

---

## Day 3 — Role-Based Access Control (40 min)

### Theory (15 min)
```
RBAC: assign permissions to ROLES, assign roles to USERS

Our server roles:
  user  → can read, create their own resources
  admin → can do everything including delete others' resources

Practice server access matrix:
┌───────────────────────────┬──────┬───────┐
│ Endpoint                  │ user │ admin │
├───────────────────────────┼──────┼───────┤
│ GET /products             │ ✅   │ ✅    │
│ POST /products            │ ❌   │ ✅    │
│ DELETE /products/{id}     │ ❌   │ ✅    │
│ GET /users                │ ✅   │ ✅    │
│ DELETE /users/{id}        │ ❌   │ ✅    │
│ GET /orders (own)         │ ✅   │ ✅    │
│ GET /orders (all)         │ ❌   │ ✅    │
│ PATCH /users/{id} (own)   │ ✅   │ ✅    │
│ PATCH /users/{id} (other) │ ❌   │ ✅    │
└───────────────────────────┴──────┴───────┘
```

### Hands-on (25 min)
```python
# exercises/week3/day3_rbac.py
import requests

BASE = "http://localhost:5000"

def get_headers(username, password):
    r = requests.post(f"{BASE}/api/v1/auth/login", json={"username":username,"password":password})
    return {"Authorization": f"Bearer {r.json()['data']['access_token']}"}

admin_headers = get_headers("admin", "admin123")
user_headers  = get_headers("alice", "password123")

def test(desc, r):
    icon = "✅" if r.status_code < 400 else "❌"
    print(f"{icon} {desc}: {r.status_code}")

# Test RBAC
test("admin creates product",   requests.post(f"{BASE}/api/v1/products", json={"name":"Test","price":9.99}, headers=admin_headers))
test("user creates product",    requests.post(f"{BASE}/api/v1/products", json={"name":"Test","price":9.99}, headers=user_headers))
test("user reads products",     requests.get(f"{BASE}/api/v1/products", headers=user_headers))
test("admin lists all users",   requests.get(f"{BASE}/api/v1/users", headers=admin_headers))
test("user lists users",        requests.get(f"{BASE}/api/v1/users", headers=user_headers))

# Test ownership
alice_user = requests.get(f"{BASE}/api/v1/auth/me", headers=user_headers).json()['data']
alice_id = alice_user['id']

test("alice patches own profile",     requests.patch(f"{BASE}/api/v1/users/{alice_id}", json={"first_name":"Updated"}, headers=user_headers))
test("alice deletes own account",     requests.delete(f"{BASE}/api/v1/users/{alice_id}", headers=user_headers))  # 403 (not admin)
test("admin can delete any user",     requests.delete(f"{BASE}/api/v1/users/99999", headers=admin_headers))  # 200 or 404
```

---

## Day 4 — Security Best Practices (40 min)

### Theory (20 min)

**Top API Security Threats (OWASP API Top 10):**

1. **Broken Object Level Authorization (BOLA)** — Can user A access user B's data?
   ```
   ❌ Vulnerable: GET /api/orders/5  (any authenticated user)
   ✅ Secure:     GET /api/orders/5  (check order.user_id == current_user.id)
   ```

2. **Broken Authentication** — Weak tokens, no expiry
   ```
   ❌ Weak: No token expiry, secrets in URLs
   ✅ Strong: Short-lived JWTs, refresh tokens, HTTPS only
   ```

3. **Excessive Data Exposure** — Returning too much
   ```
   ❌ Returning: {"id":1, "email":"x", "password_hash":"...", "ssn":"..."}
   ✅ Returning: {"id":1, "email":"x", "name":"Alice"}
   ```

4. **Lack of Rate Limiting** — No throttling
   ```
   ✅ Return 429 with Retry-After header
   ✅ Rate limit per IP, per user, per endpoint
   ```

5. **Security Misconfiguration**
   ```
   ✅ HTTPS in production
   ✅ CORS configured properly
   ✅ No debug info in error messages
   ✅ No sensitive data in logs
   ```

### Hands-on (20 min)
```python
# exercises/week3/day4_security.py
import requests

BASE = "http://localhost:5000"

# 1. Test BOLA — can Alice see Bob's orders?
def get_headers(username, password):
    r = requests.post(f"{BASE}/api/v1/auth/login", json={"username":username,"password":password})
    return {"Authorization": f"Bearer {r.json()['data']['access_token']}"}

alice_h = get_headers("alice", "password123")
bob_h   = get_headers("bob",   "password123")

# Get Alice's orders
alice_orders = requests.get(f"{BASE}/api/v1/orders", headers=alice_h).json()

# Try to access as Bob
if alice_orders.get('data'):
    order_id = alice_orders['data'][0]['id']
    r = requests.get(f"{BASE}/api/v1/orders/{order_id}", headers=bob_h)
    print(f"Bob accessing Alice's order: {r.status_code}")
    # Should be 403 Forbidden

# 2. Test rate limiting
import time
print("\nTesting rate limiting...")
for i in range(5):
    r = requests.get(f"{BASE}/api/v1/products")
    print(f"  Request {i+1}: {r.status_code}")

# 3. Verify no sensitive data exposure
r = requests.get(f"{BASE}/api/v1/users/1", headers=alice_h)
user_data = r.json().get('data', {})
print(f"\nUser fields returned: {list(user_data.keys())}")
assert 'password' not in user_data, "❌ PASSWORD EXPOSED!"
print("✅ No password in response")
```

---

## Day 5 — OAuth2 Concepts & Week Review (40 min)

### Theory (20 min)

**OAuth2 Flow (Authorization Code):**
```
User: "I want to use MyApp to access my Google Drive"

1. MyApp redirects to Google:
   GET https://accounts.google.com/oauth/authorize
       ?client_id=myapp123
       &redirect_uri=https://myapp.com/callback
       &scope=drive.readonly
       &response_type=code

2. User logs into Google, approves

3. Google redirects back:
   GET https://myapp.com/callback?code=xyz789

4. MyApp exchanges code for tokens:
   POST https://oauth2.googleapis.com/token
   {"code":"xyz789","client_secret":"..."}
   → {"access_token":"...", "refresh_token":"..."}

5. MyApp uses token to access Drive API:
   GET https://www.googleapis.com/drive/v3/files
   Authorization: Bearer <access_token>
```

**OAuth2 Grant Types:**
- `authorization_code` — Web apps with redirect (most common)
- `client_credentials` — Server-to-server (no user involved)
- `refresh_token` — Get new access token
- `implicit` — Deprecated (don't use)

### Week 3 Challenge (20 min)
Build a complete authenticated API client class:
1. Handles login + token storage
2. Auto-refreshes expired tokens
3. Raises appropriate exceptions for 401, 403, 404
4. Has methods for all CRUD operations on products
5. Demonstrates RBAC by testing as both user and admin

---

## 📋 Week 3 Checklist
- [ ] Can explain JWT structure and why it's stateless
- [ ] Understand access token vs refresh token
- [ ] Can implement RBAC checks
- [ ] Know OWASP API Top 5 threats
- [ ] Can explain OAuth2 authorization code flow
- [ ] Built a complete authenticated API client
- [ ] Completed week challenge
