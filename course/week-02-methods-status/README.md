# Week 2 — HTTP Methods, Status Codes & Headers
**Time:** 40 min/day × 5 days | **Goal:** Handle any HTTP scenario correctly

---

## Day 1 — HTTP Methods Deep Dive (40 min)

### Theory (15 min)

| Method  | Purpose            | Has Body | Idempotent | Safe |
|---------|--------------------|----------|------------|------|
| GET     | Read resource      | No       | ✅          | ✅   |
| POST    | Create resource    | Yes      | ❌          | ❌   |
| PUT     | Full replace       | Yes      | ✅          | ❌   |
| PATCH   | Partial update     | Yes      | ✅*         | ❌   |
| DELETE  | Remove resource    | No       | ✅          | ❌   |
| HEAD    | GET without body   | No       | ✅          | ✅   |
| OPTIONS | What is supported? | No       | ✅          | ✅   |

**Idempotent** = Calling it N times has the same effect as calling it once.
**Safe** = Doesn't modify server state.

**PUT vs PATCH — Critical Interview Topic:**
```python
# PUT — Full replacement (must send ALL fields)
PUT /api/v1/products/1
{
  "name": "Updated Headphones",
  "description": "...",   # required
  "price": 89.99,          # required
  "category": "electronics", # required
  "stock": 45              # required
}
# Missing fields → reset to defaults or error

# PATCH — Partial update (send only what changes)
PATCH /api/v1/products/1
{
  "price": 89.99           # only update price
}
# Everything else stays the same
```

### Hands-on (25 min)
```python
# exercises/week2/day1_methods.py
import requests, json

BASE = "http://localhost:5000"

def login(username="admin", password="admin123"):
    r = requests.post(f"{BASE}/api/v1/auth/login", json={"username": username, "password": password})
    return {"Authorization": f"Bearer {r.json()['data']['access_token']}"}

headers = login()

# 1. POST — Create a product
new_product = {"name": "Test Widget", "price": 9.99, "category": "test", "stock": 100}
r = requests.post(f"{BASE}/api/v1/products", json=new_product, headers=headers)
print(f"POST → {r.status_code}: {r.json()}")
product_id = r.json()['data']['id']

# 2. GET — Read it back
r = requests.get(f"{BASE}/api/v1/products/{product_id}")
print(f"\nGET → {r.status_code}: {r.json()['data']['name']}")

# 3. PATCH — Update only price
r = requests.patch(f"{BASE}/api/v1/products/{product_id}", json={"price": 19.99}, headers=headers)
print(f"\nPATCH → {r.status_code}: {r.json()}")

# 4. PUT — Full replacement
r = requests.put(f"{BASE}/api/v1/products/{product_id}",
                  json={"name": "Test Widget v2", "price": 14.99, "category": "test", "stock": 50, "description": "Updated"},
                  headers=headers)
print(f"\nPUT → {r.status_code}: {r.json()}")

# 5. DELETE — Remove it
r = requests.delete(f"{BASE}/api/v1/products/{product_id}", headers=headers)
print(f"\nDELETE → {r.status_code}: {r.json()}")

# 6. Try to GET it after delete — should 404
r = requests.get(f"{BASE}/api/v1/products/{product_id}")
print(f"\nGET after DELETE → {r.status_code}: {r.json()}")
```

---

## Day 2 — Status Codes Mastery (40 min)

### Theory (15 min)

**2xx Success**
| Code | Name | When to use |
|------|------|-------------|
| 200 | OK | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE (no body returned) |

**3xx Redirection**
| Code | Name | When to use |
|------|------|-------------|
| 301 | Moved Permanently | Resource URL has changed forever |
| 304 | Not Modified | Cached response is still valid |

**4xx Client Errors**
| Code | Name | When to use |
|------|------|-------------|
| 400 | Bad Request | Malformed JSON, missing required fields |
| 401 | Unauthorized | Not authenticated (no/expired token) |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate (e.g., email already registered) |
| 422 | Unprocessable Entity | Business logic violation |
| 429 | Too Many Requests | Rate limit exceeded |

**5xx Server Errors**
| Code | Name | When to use |
|------|------|-------------|
| 500 | Internal Server Error | Unhandled exception |
| 502 | Bad Gateway | Upstream service failed |
| 503 | Service Unavailable | Server overloaded/maintenance |

### Hands-on (25 min)
```python
# exercises/week2/day2_status_codes.py
import requests

BASE = "http://localhost:5000"

def check(description, r):
    emoji = "✅" if r.status_code < 400 else "❌"
    print(f"{emoji} {description}: {r.status_code}")
    if r.status_code >= 400:
        print(f"   Error: {r.json().get('error', 'unknown')}")

# Trigger different status codes
check("Valid product",          requests.get(f"{BASE}/api/v1/products/1"))
check("Non-existent product",   requests.get(f"{BASE}/api/v1/products/99999"))
check("Bad login",              requests.post(f"{BASE}/api/v1/auth/login", json={"username":"x","password":"y"}))
check("No auth token",          requests.get(f"{BASE}/api/v1/auth/me"))
check("Bad JSON",               requests.post(f"{BASE}/api/v1/auth/login", data="not json", headers={"Content-Type":"application/json"}))
check("Duplicate registration", requests.post(f"{BASE}/api/v1/auth/register", json={"username":"admin","email":"admin@example.com","password":"x"}))
```

---

## Day 3 — Headers Deep Dive (40 min)

### Theory (15 min)

**Request Headers:**
```
Authorization: Bearer eyJ...        # Authentication
Content-Type: application/json      # Body format being sent
Accept: application/json            # Format client wants back
Accept-Language: en-US              # Preferred language
User-Agent: MyApp/1.0               # Client identification
X-Request-ID: abc-123               # Trace ID for debugging
If-None-Match: "abc123"             # Conditional GET (ETag)
If-Modified-Since: Mon, 1 Jan 2024  # Conditional GET (date)
```

**Response Headers:**
```
Content-Type: application/json      # Body format being returned
X-Response-Time: 12ms               # Performance metric
X-Rate-Limit-Remaining: 95          # How many requests left
X-API-Version: 1.0.0                # API version
ETag: "abc123"                      # Resource version identifier
Cache-Control: max-age=3600         # Caching instructions
Location: /api/v1/users/42          # Where new resource was created
```

### Hands-on (25 min)
```python
# exercises/week2/day3_headers.py
import requests

BASE = "http://localhost:5000"

# 1. Inspect response headers
r = requests.get(f"{BASE}/api/v1/products")
print("Response Headers:")
for key, val in r.headers.items():
    print(f"  {key}: {val}")

# 2. Send custom request headers
headers = {
    "Accept": "application/json",
    "X-Request-ID": "my-trace-id-12345",
    "User-Agent": "MyStudyApp/1.0"
}
r = requests.get(f"{BASE}/api/v1/products", headers=headers)
print(f"\nStatus with custom headers: {r.status_code}")

# 3. Try wrong Content-Type
r = requests.post(f"{BASE}/api/v1/auth/login",
                   data='{"username":"alice","password":"password123"}',
                   headers={"Content-Type": "text/plain"})
print(f"\nWrong Content-Type: {r.status_code} - {r.json()}")

# 4. Check rate limiting
import time
for i in range(5):
    r = requests.get(f"{BASE}/api/v1/products")
    print(f"Request {i+1}: {r.status_code} | X-Response-Time: {r.headers.get('X-Response-Time')}")
```

---

## Day 4 — Error Handling in Client Code (40 min)

### Theory (10 min)
Never blindly trust API responses. Always handle errors gracefully.

### Hands-on (30 min)
```python
# exercises/week2/day4_error_handling.py
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

BASE = "http://localhost:5000"

class APIClient:
    def __init__(self, base_url, timeout=10):
        self.base = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def login(self, username, password):
        r = self._request('POST', '/api/v1/auth/login',
                           json={"username": username, "password": password})
        if r and r.get('success'):
            token = r['data']['access_token']
            self.session.headers['Authorization'] = f"Bearer {token}"
        return r

    def _request(self, method, path, **kwargs):
        url = f"{self.base}{path}"
        try:
            r = self.session.request(method, url, timeout=self.timeout, **kwargs)

            # Raise for 4xx/5xx
            if r.status_code == 401:
                print("❌ Unauthorized — check your token")
                return None
            elif r.status_code == 403:
                print("❌ Forbidden — insufficient permissions")
                return None
            elif r.status_code == 404:
                print(f"❌ Not found: {path}")
                return None
            elif r.status_code == 429:
                print("⚠️  Rate limited — slow down!")
                return None
            elif r.status_code >= 500:
                print(f"❌ Server error {r.status_code}")
                return None

            return r.json()

        except ConnectionError:
            print("❌ Cannot connect to server — is it running?")
        except Timeout:
            print(f"❌ Request timed out after {self.timeout}s")
        except RequestException as e:
            print(f"❌ Request failed: {e}")
        return None

    def get_products(self, **params):
        return self._request('GET', '/api/v1/products', params=params)


# Test the client
client = APIClient(BASE)
client.login("alice", "password123")
result = client.get_products(category="books", page=1, per_page=3)
if result:
    for p in result['data']:
        print(f"  {p['name']}: ${p['price']}")
```

---

## Day 5 — Content Negotiation & Week Review (40 min)

### Content Negotiation (15 min)
```python
# exercises/week2/day5_content_negotiation.py
import requests

BASE = "http://localhost:5000"

# The server always returns JSON, but let's see how Accept headers work
r = requests.get(f"{BASE}/api/v1/products", headers={"Accept": "application/json"})
print(f"JSON accepted: {r.status_code}, type: {r.headers['Content-Type']}")

# Query params vs path params — when to use each
# Path params: identify a specific resource
# GET /products/42 — the product with ID 42

# Query params: filter, sort, paginate a collection
# GET /products?category=books&page=2&sort_by=price&order=desc

r = requests.get(f"{BASE}/api/v1/products", params={
    "category": "electronics",
    "min_price": 20,
    "max_price": 100,
    "sort_by": "price",
    "order": "desc",
    "page": 1,
    "per_page": 5
})
print("\nFiltered products:")
for p in r.json()['data']:
    print(f"  {p['name']:30} ${p['price']:.2f}")
```

### Week 2 Challenge (25 min)
Write a Python script that:
1. Logs in as admin
2. Creates 3 new products in the `gadgets` category
3. Gets all `gadgets` products with pagination
4. Updates the price of the cheapest one by +10%
5. Deletes the most expensive one
6. Handles all errors gracefully

---

## 📋 Week 2 Checklist
- [ ] Know all HTTP methods and when to use each
- [ ] Can explain PUT vs PATCH difference
- [ ] Know all major status codes (2xx, 4xx, 5xx)
- [ ] Understand the difference between 401 and 403
- [ ] Can read and set request/response headers
- [ ] Built a reusable API client with error handling
- [ ] Completed week challenge
