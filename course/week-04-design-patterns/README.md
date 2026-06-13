# Week 4 — API Design Patterns & Best Practices
**Time:** 40 min/day × 5 days | **Goal:** Design APIs that developers love

---

## Day 1 — Resource Design & URL Patterns (40 min)

### Theory (20 min)

**Resource hierarchy & nesting:**
```
Shallow nesting (preferred — max 2 levels deep):
  /users/{id}
  /users/{id}/orders          ← user's orders
  /users/{id}/posts           ← user's posts
  /orders/{id}/items          ← items in an order

Avoid deep nesting:
  ❌ /users/{id}/orders/{id}/items/{id}/reviews  (too deep)
  ✅ /order-items/{id}/reviews                   (flatten it)
```

**Consistent response envelope:**
```json
{
  "success": true,
  "data": { ... },       ← the actual payload
  "meta": {              ← pagination, versions, etc
    "pagination": {...}
  },
  "error": null          ← present only on failure
}

Error response:
{
  "success": false,
  "error": "User not found",
  "errors": ["field1 is required", "field2 too long"],
  "hint": "Check the user ID in the URL"
}
```

**Filtering, Sorting, Searching pattern:**
```
Collection:    GET /products
Filter:        GET /products?category=books&active=true
Search:        GET /products?search=python
Sort:          GET /products?sort_by=price&order=desc
Paginate:      GET /products?page=2&per_page=20
Combine:       GET /products?category=books&sort_by=price&order=asc&page=1&per_page=10
```

### Hands-on (20 min)
```bash
# Explore the practice server's design patterns

# 1. Filtering
curl "http://localhost:5000/api/v1/products?category=electronics"
curl "http://localhost:5000/api/v1/products?min_price=20&max_price=100"

# 2. Sorting
curl "http://localhost:5000/api/v1/products?sort_by=price&order=desc"

# 3. Search
curl "http://localhost:5000/api/v1/products?search=headphones"

# 4. Pagination
curl "http://localhost:5000/api/v1/products?page=1&per_page=3"
curl "http://localhost:5000/api/v1/products?page=2&per_page=3"

# 5. Observe the HATEOAS links in v2
curl "http://localhost:5000/api/v2/products" | python3 -m json.tool
```

---

## Day 2 — Versioning Strategies (40 min)

### Theory (20 min)

**3 ways to version an API:**

1. **URL Path Versioning** (most common, easiest)
   ```
   /api/v1/products
   /api/v2/products
   ```
   ✅ Obvious, easy to test in browser, easy to route
   ❌ "Unclean" URLs per REST purists

2. **Header Versioning**
   ```
   GET /api/products
   Accept: application/vnd.myapp.v2+json
   ```
   ✅ Clean URLs
   ❌ Harder to test, not visible in browser

3. **Query Parameter Versioning**
   ```
   GET /api/products?version=2
   ```
   ✅ Easy to see
   ❌ Not standard, easy to forget

**When to version:**
- Breaking changes: remove a field, change a field type, change behavior
- Non-breaking: add new fields, add new endpoints (no version needed)

**Sunset policy:**
```
X-API-Deprecation: true
X-API-Sunset-Date: 2025-12-31
X-API-See-Also: https://docs.myapi.com/migration/v1-to-v2
```

### Hands-on (20 min)
```python
# exercises/week4/day2_versioning.py
import requests

BASE = "http://localhost:5000"

# Compare v1 and v2 responses
v1 = requests.get(f"{BASE}/api/v1/products?per_page=2").json()
v2 = requests.get(f"{BASE}/api/v2/products?per_page=2").json()

print("=== V1 Product ===")
import json
print(json.dumps(v1['data'][0], indent=2))

print("\n=== V2 Product (note: _links, in_stock, price_formatted) ===")
print(json.dumps(v2['data'][0], indent=2))

# v2 improvements:
# - HATEOAS _links for discoverability
# - in_stock computed field
# - price_formatted for display
# - Enhanced pagination meta
```

---

## Day 3 — HATEOAS & Discoverability (40 min)

### Theory (15 min)

**HATEOAS** = Hypermedia As The Engine Of Application State

The idea: responses include links to what you can do next. The client doesn't need to hard-code URLs.

```json
{
  "data": {
    "id": 1,
    "name": "Headphones",
    "status": "pending",
    "_links": {
      "self":     {"href": "/orders/1", "method": "GET"},
      "confirm":  {"href": "/orders/1/status", "method": "PATCH"},
      "cancel":   {"href": "/orders/1", "method": "DELETE"},
      "items":    {"href": "/orders/1/items", "method": "GET"},
      "customer": {"href": "/users/5", "method": "GET"}
    }
  }
}
```

Benefits: API is self-documenting, clients don't break when URLs change.

### Hands-on (25 min)
```python
# exercises/week4/day3_hateoas.py
import requests

BASE = "http://localhost:5000"

# Explore v2 HATEOAS links
r = requests.get(f"{BASE}/api/v2/products")
data = r.json()

for product in data['data'][:2]:
    print(f"\nProduct: {product['name']}")
    print("Available actions:")
    for action, link in product.get('_links', {}).items():
        print(f"  {action}: {link['method']} {link['href']}")

# The collection-level links enable pagination without hard-coding URLs
print("\nCollection links:")
for name, href in data.get('meta', {}).get('_links', {}).items():
    if href:
        print(f"  {name}: {href}")
```

---

## Day 4 — Request Validation & Error Design (40 min)

### Theory (15 min)

**Good error responses give clients everything they need to fix the problem:**

```json
// Bad error ❌
{"error": "Bad request"}

// Good error ✅
{
  "success": false,
  "error": "Validation failed",
  "errors": [
    {"field": "email", "message": "Invalid email format"},
    {"field": "price", "message": "Must be a positive number"},
    {"field": "name",  "message": "Required field missing"}
  ],
  "hint": "Check the API docs at /docs for field requirements"
}
```

### Hands-on (25 min)
```python
# exercises/week4/day4_validation.py
import requests

BASE = "http://localhost:5000"

def get_admin_headers():
    r = requests.post(f"{BASE}/api/v1/auth/login", json={"username":"admin","password":"admin123"})
    return {"Authorization": f"Bearer {r.json()['data']['access_token']}"}

headers = get_admin_headers()

test_cases = [
    ("Missing required fields",   {}),
    ("Invalid price type",         {"name": "X", "price": "not-a-number"}),
    ("Negative price",             {"name": "X", "price": -5}),
    ("Valid product",              {"name": "Widget", "price": 9.99, "category": "test", "stock": 10}),
]

for desc, payload in test_cases:
    r = requests.post(f"{BASE}/api/v1/products", json=payload, headers=headers)
    status = r.status_code
    error  = r.json().get('error', 'none')
    icon   = "✅" if status < 400 else "❌"
    print(f"{icon} {desc}: {status} — {error}")
```

---

## Day 5 — Idempotency & Week Review (40 min)

### Theory (15 min)

**Idempotency in practice:**
```
GET    → always idempotent (reading doesn't change state)
DELETE → idempotent (deleting twice = same result as deleting once)
PUT    → idempotent (replacing with same data = same result)
POST   → NOT idempotent (calling twice creates two resources)

Idempotency key pattern (for POST):
  POST /api/v1/orders
  Idempotency-Key: my-unique-request-id-abc123

If server already processed this key → return original response
This prevents duplicate orders on network retry.
```

### Week 4 Challenge (25 min)
Design (on paper or in a README) a REST API for a library system:
1. Define all resources (books, members, loans, reservations)
2. Define URL structure with proper nesting
3. Define all endpoints with HTTP methods
4. Define request/response schemas for 3 key endpoints
5. Define versioning strategy
6. Define error response format

Compare with `solutions/week4/library_api_design.md`

---

## 📋 Week 4 Checklist
- [ ] Know URL nesting best practices
- [ ] Can design consistent response envelopes
- [ ] Understand 3 versioning strategies and tradeoffs
- [ ] Know what HATEOAS is and when to use it
- [ ] Can design good error responses
- [ ] Understand idempotency and why it matters
- [ ] Completed library API design challenge
