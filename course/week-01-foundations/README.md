# Week 1 — HTTP Fundamentals & REST Principles
**Time:** 40 min/day × 5 days | **Goal:** Understand what REST is and why it matters

---

## Day 1 — What is HTTP? (40 min)

### Theory (15 min)
HTTP (HyperText Transfer Protocol) is the foundation of all REST APIs.
Every API call is an HTTP request → HTTP response cycle.

```
Client                              Server
  |                                    |
  |  GET /api/v1/products HTTP/1.1     |
  |  Host: localhost:5000              |
  |  Authorization: Bearer abc123      |
  | ─────────────────────────────────► |
  |                                    |  (processes request)
  |  HTTP/1.1 200 OK                   |
  |  Content-Type: application/json    |
  |  X-Response-Time: 12ms             |
  |  {"data": [...]}                   |
  | ◄───────────────────────────────── |
```

### Key Concepts
- **URL anatomy**: `https://api.example.com:443/v1/products?category=books#section`
  - Protocol: `https`
  - Host: `api.example.com`
  - Port: `443`
  - Path: `/v1/products`
  - Query string: `?category=books`
  - Fragment: `#section` (not sent to server)

- **Headers**: Metadata sent with every request/response
  - `Content-Type: application/json` — body format
  - `Authorization: Bearer <token>` — auth credential
  - `Accept: application/json` — what client wants back
  - `Cache-Control: no-cache` — caching directive

- **Body**: Data payload (only in POST, PUT, PATCH)

### Hands-on (25 min)
```bash
# Start the server first
cd server && source venv/bin/activate && python app.py

# Exercise 1: Make your first API call
curl http://localhost:5000/health

# Exercise 2: See the headers
curl -v http://localhost:5000/health

# Exercise 3: Explore the docs
curl http://localhost:5000/docs | python3 -m json.tool

# Exercise 4: Use Python requests
python3 -c "
import requests
r = requests.get('http://localhost:5000/health')
print('Status:', r.status_code)
print('Headers:', dict(r.headers))
print('Body:', r.json())
"
```

---

## Day 2 — REST Principles (40 min)

### Theory (20 min)
REST = **RE**presentational **S**tate **T**ransfer — an architectural style (not a protocol).

**6 REST Constraints:**

| Constraint | What it means | Example |
|-----------|--------------|---------|
| **Client-Server** | UI and data are separate | React frontend + Flask API |
| **Stateless** | Each request is self-contained | No server-side sessions |
| **Cacheable** | Responses declare if they can be cached | `Cache-Control` header |
| **Uniform Interface** | Consistent resource naming | `/api/v1/users/{id}` |
| **Layered System** | Client doesn't know about intermediaries | Load balancers, CDNs |
| **Code on Demand** | Server can send executable code (optional) | JavaScript delivery |

**Resources vs. Actions:**
```
❌ Non-RESTful (action-based):
  /getUser?id=5
  /createNewProduct
  /deleteOrderById?id=3

✅ RESTful (resource-based):
  GET    /users/5
  POST   /products
  DELETE /orders/3
```

**Resource Naming Rules:**
```
✅ Use nouns, not verbs:   /products  not  /getProducts
✅ Use plural nouns:        /users     not  /user
✅ Use lowercase + hyphens: /order-items  not  /orderItems
✅ Nest related resources:  /users/5/orders
✅ Query strings for filters: /products?category=books&page=2
```

### Hands-on (20 min)
```bash
# Look at how the practice server follows REST principles
curl http://localhost:5000/api/v1/products
curl http://localhost:5000/api/v1/products?category=books
curl http://localhost:5000/api/v1/products?page=1&per_page=3

# Notice: /products is the resource, filtering is in query params
# Notice: response includes pagination metadata
```

---

## Day 3 — JSON & Request/Response Structure (40 min)

### Theory (15 min)
JSON is the universal language of REST APIs.

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Alice Smith",
    "email": "alice@example.com",
    "role": "user",
    "created_at": "2024-01-15T10:30:00"
  },
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 100,
      "total_pages": 10
    }
  }
}
```

**Python ↔ JSON mapping:**
```python
Python dict   → JSON object   {"key": "value"}
Python list   → JSON array    [1, 2, 3]
Python str    → JSON string   "hello"
Python int    → JSON number   42
Python float  → JSON number   3.14
Python True   → JSON true
Python False  → JSON false
Python None   → JSON null
```

### Hands-on (25 min)
```python
# exercises/week1/day3_json.py
import requests
import json

BASE = "http://localhost:5000"

# 1. Parse JSON response
r = requests.get(f"{BASE}/api/v1/products")
data = r.json()
print(f"Total products: {data['meta']['pagination']['total']}")
print(f"First product: {data['data'][0]['name']}")

# 2. Send JSON body — register a user
new_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "mypassword",
    "first_name": "Test",
    "last_name": "User"
}
r = requests.post(f"{BASE}/api/v1/auth/register", json=new_user)
print(f"\nRegister status: {r.status_code}")
print(f"Response: {json.dumps(r.json(), indent=2)}")

# 3. Pretty print any response
def api_call(method, path, **kwargs):
    r = getattr(requests, method)(f"{BASE}{path}", **kwargs)
    print(f"\n{method.upper()} {path} → {r.status_code}")
    print(json.dumps(r.json(), indent=2))
    return r

api_call('get', '/api/v1/products/1')
```

---

## Day 4 — Authentication Flow (40 min)

### Theory (15 min)
The practice server uses **JWT (JSON Web Token)** authentication.

```
1. Client sends credentials:
   POST /api/v1/auth/login
   {"username": "alice", "password": "password123"}

2. Server validates and returns tokens:
   {"access_token": "eyJ...", "refresh_token": "eyJ..."}

3. Client uses access token for protected routes:
   GET /api/v1/users
   Authorization: Bearer eyJ...

4. When access token expires (30 min), use refresh token:
   POST /api/v1/auth/refresh
   {"refresh_token": "eyJ..."}
```

**JWT Structure:**
```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.abc123
└─── Header (base64) ─┘ └── Payload (base64) ─┘ └── Signature ─┘
```

### Hands-on (25 min)
```python
# exercises/week1/day4_auth.py
import requests

BASE = "http://localhost:5000"

# Step 1: Login
r = requests.post(f"{BASE}/api/v1/auth/login", json={
    "username": "alice",
    "password": "password123"
})
tokens = r.json()['data']
access_token = tokens['access_token']
print(f"Got access token: {access_token[:30]}...")

# Step 2: Use token
headers = {"Authorization": f"Bearer {access_token}"}
me = requests.get(f"{BASE}/api/v1/auth/me", headers=headers)
print(f"\nMy profile: {me.json()['data']}")

# Step 3: Try without token — should get 401
no_auth = requests.get(f"{BASE}/api/v1/auth/me")
print(f"\nWithout token: {no_auth.status_code} {no_auth.json()['error']}")

# Step 4: Create a session helper
class APISession:
    def __init__(self, base_url):
        self.base = base_url
        self.session = requests.Session()

    def login(self, username, password):
        r = self.session.post(f"{self.base}/api/v1/auth/login",
                               json={"username": username, "password": password})
        token = r.json()['data']['access_token']
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        return self

    def get(self, path, **kwargs):
        return self.session.get(f"{self.base}{path}", **kwargs)

api = APISession(BASE).login("alice", "password123")
print(f"\nProducts via session: {api.get('/api/v1/products').json()['meta']}")
```

---

## Day 5 — Week Review & Practice (40 min)

### Review Quiz (10 min)
Answer these without looking at notes:
1. What does REST stand for?
2. What are 3 rules for naming REST resources?
3. What HTTP header carries the JWT token?
4. What's the difference between path params and query params?
5. What JSON field tells you if a response is paginated?

### Practice Challenge (30 min)
Build a Python script that:
1. Registers a new unique user
2. Logs in as that user
3. Gets all products filtered by category `books`
4. Prints only the name and price of each book
5. Gets the current user's profile
6. Logs out

Check your solution against `solutions/week1/challenge.py`

---

## 📋 Week 1 Checklist
- [ ] Can explain REST in plain English
- [ ] Know the 6 REST constraints
- [ ] Can identify good vs bad resource naming
- [ ] Can make authenticated API calls in Python
- [ ] Understand JWT token flow
- [ ] Completed all 5 day exercises
- [ ] Completed the week challenge
