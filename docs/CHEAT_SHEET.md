# 📋 REST API Quick Reference Cheat Sheet

## HTTP Methods
| Method | Use | Idempotent | Safe | Body |
|--------|-----|------------|------|------|
| GET    | Read | ✅ | ✅ | No |
| POST   | Create | ❌ | ❌ | Yes |
| PUT    | Full replace | ✅ | ❌ | Yes |
| PATCH  | Partial update | ✅ | ❌ | Yes |
| DELETE | Remove | ✅ | ❌ | No |
| HEAD   | Check exists | ✅ | ✅ | No |
| OPTIONS| CORS preflight | ✅ | ✅ | No |

## Status Codes
```
200 OK              → successful GET/PUT/PATCH/DELETE
201 Created         → successful POST (new resource)
204 No Content      → successful DELETE (no body)
301 Moved Perm      → URL changed forever
304 Not Modified    → cache still valid
400 Bad Request     → malformed request, missing fields
401 Unauthorized    → not authenticated
403 Forbidden       → authenticated but no permission
404 Not Found       → resource doesn't exist
405 Method Not Allowed → wrong HTTP method
409 Conflict        → duplicate (email already exists)
422 Unprocessable   → business logic violation
429 Too Many        → rate limit exceeded
500 Server Error    → bug in server code
502 Bad Gateway     → upstream failure
503 Unavailable     → overloaded/maintenance
```

## URL Patterns
```
Collection:   GET    /api/v1/products
Single:       GET    /api/v1/products/{id}
Create:       POST   /api/v1/products
Full update:  PUT    /api/v1/products/{id}
Partial:      PATCH  /api/v1/products/{id}
Delete:       DELETE /api/v1/products/{id}
Nested:       GET    /api/v1/users/{id}/orders
Sub-action:   PATCH  /api/v1/orders/{id}/status
Filter:       GET    /api/v1/products?category=books&min_price=10
Sort:         GET    /api/v1/products?sort_by=price&order=desc
Paginate:     GET    /api/v1/products?page=2&per_page=20
Search:       GET    /api/v1/products?search=python
```

## Key Headers
```
Authorization: Bearer <jwt>       → auth token
Content-Type: application/json    → sending JSON
Accept: application/json          → want JSON back
X-API-Key: sk-abc123              → API key auth
Cache-Control: max-age=3600       → cache for 1 hour
ETag: "abc123"                    → resource version
X-RateLimit-Remaining: 95         → requests left
Retry-After: 30                   → wait before retry
```

## JWT Cheat Sheet
```
Structure:  Header.Payload.Signature
Algorithm:  HS256 (HMAC-SHA256)
Decode:     base64url_decode(payload)
Verify:     HMAC-SHA256(header+"."+payload, secret) == signature

Payload fields:
  sub / user_id  → who this is for
  role           → user permissions
  exp            → expiry unix timestamp
  iat            → issued at timestamp
  type           → access | refresh
```

## Python Quick Reference
```python
import requests

# Session with auth
s = requests.Session()
s.headers['Authorization'] = f'Bearer {token}'

# GET with params
r = s.get('/products', params={'category': 'books', 'page': 1})

# POST with JSON
r = s.post('/products', json={'name': 'X', 'price': 9.99})

# PATCH partial update
r = s.patch('/products/1', json={'price': 19.99})

# Check response
r.status_code        # 200, 201, 404...
r.json()             # parse JSON body
r.headers            # response headers
r.raise_for_status() # raise exception if 4xx/5xx

# Pagination loop
def get_all(url, params=None):
    params = {**(params or {}), 'page': 1, 'per_page': 50}
    results = []
    while True:
        data = requests.get(url, params=params).json()
        results.extend(data['data'])
        if data['meta']['pagination']['page'] >= data['meta']['pagination']['total_pages']:
            break
        params['page'] += 1
    return results
```

## Common Mistakes & Fixes
```
❌ GET /getUser?id=5          ✅ GET /users/5
❌ POST /deleteProduct/3      ✅ DELETE /products/3
❌ Return 200 for errors      ✅ Return appropriate 4xx/5xx
❌ Return password in response ✅ Exclude sensitive fields
❌ No pagination on lists     ✅ Always paginate collections
❌ /user (singular)           ✅ /users (plural)
❌ Storing token in URL        ✅ Store token in Authorization header
❌ Long-lived access tokens   ✅ 30min access + 7day refresh
❌ No error message           ✅ {"error": "User not found", "hint": "..."}
❌ 401 for wrong role         ✅ 403 for wrong role (you're authenticated but not authorized)
```
