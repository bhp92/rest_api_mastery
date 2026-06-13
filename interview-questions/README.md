# 🎯 REST API Interview Questions — Complete Bank
**100+ questions from Junior to Architect level**

---

## 🟢 Junior Level (1-2 years)

### Q1: What is REST?
**Answer:** REST (Representational State Transfer) is an architectural style for building web APIs. It uses HTTP as the transport protocol and defines 6 constraints: Client-Server separation, Statelessness, Cacheability, Uniform Interface, Layered System, and Code on Demand (optional). A "RESTful" API follows these principles. The key idea is that resources are identified by URLs, and you interact with them using standard HTTP methods (GET, POST, PUT, PATCH, DELETE).

**Follow-up:** What's the difference between REST and SOAP?
> REST uses JSON/HTTP, is stateless, simpler. SOAP uses XML, has strict contracts (WSDL), built-in error handling. REST is preferred today for its simplicity and performance.

---

### Q2: What are the HTTP methods and when do you use each?
**Answer:**
- **GET** — Read a resource. Safe and idempotent. No body.
- **POST** — Create a new resource. Not idempotent (calling twice creates two).
- **PUT** — Full replacement of a resource. Idempotent. Requires all fields.
- **PATCH** — Partial update. Send only fields you want to change.
- **DELETE** — Remove a resource. Idempotent.
- **HEAD** — Like GET but no response body. Used to check existence.
- **OPTIONS** — What methods does this endpoint support? Used in CORS preflight.

---

### Q3: What is the difference between 401 and 403?
**Answer:**
- **401 Unauthorized** — The request lacks valid authentication credentials. You're not logged in, your token expired, or no token was provided. The name is misleading — it really means "unauthenticated."
- **403 Forbidden** — You ARE authenticated (we know who you are), but you don't have permission to access this resource. You're logged in as a regular user trying to access admin endpoints.

**Analogy:** 401 = you don't have an ID card. 403 = you have an ID card but you're not on the guest list.

---

### Q4: What is the difference between PUT and PATCH?
**Answer:** Both update a resource, but:
- **PUT** is a full replacement. You must send ALL fields. Any field you omit may be reset to null/default. Use when you want to replace the entire resource.
- **PATCH** is a partial update. You send only the fields you want to change. Everything else stays the same. More efficient, less data over the wire.

```python
# PUT — must send everything
PUT /products/1
{"name": "Headphones", "price": 99.99, "category": "electronics", "stock": 50}

# PATCH — just what changed
PATCH /products/1
{"price": 89.99}
```

---

### Q5: What status code do you return when creating a resource?
**Answer:** **201 Created**. Also include a `Location` header pointing to the new resource:
```
HTTP/1.1 201 Created
Location: /api/v1/products/42
{"data": {"id": 42, "name": "New Product"}}
```

---

### Q6: What is an idempotent operation?
**Answer:** An operation is idempotent if performing it multiple times has the same effect as performing it once. GET, PUT, DELETE, HEAD are idempotent. POST is not — POSTing twice creates two resources.

**Why it matters:** If a network request fails, you can safely retry idempotent operations without side effects.

---

### Q7: What is JSON and how do Python types map to it?
**Answer:**
```
Python dict  → JSON object   {}
Python list  → JSON array    []
Python str   → JSON string   ""
Python int   → JSON number   42
Python float → JSON number   3.14
Python True  → JSON true
Python False → JSON false
Python None  → JSON null
```

---

### Q8: What is pagination and why is it important?
**Answer:** Pagination limits the number of results returned per request and provides navigation to other pages. It's important because:
1. Performance — returning 100,000 records at once would be slow
2. Memory — client and server would need to hold huge amounts of data
3. UX — users can't process thousands of results at once

Common implementations:
- **Offset pagination**: `?page=2&per_page=20` — simple, familiar, has drift issues
- **Cursor pagination**: `?cursor=abc123&limit=20` — stable, no drift, better for real-time data

---

## 🟡 Mid Level (3-4 years)

### Q9: Explain JWT and how it works
**Answer:** JWT (JSON Web Token) is a compact, self-contained way to transmit information securely between parties as a JSON object. Structure: `Header.Payload.Signature`

- **Header**: `{"alg": "HS256", "typ": "JWT"}` — base64 encoded
- **Payload**: `{"user_id": 1, "role": "admin", "exp": 1234567890}` — base64 encoded
- **Signature**: `HMAC-SHA256(header + "." + payload, secret_key)` — prevents tampering

**Why stateless?** The server doesn't need to look up a session in the database. It just validates the signature using the secret key and reads the user info from the payload.

**Limitation:** Can't invalidate before expiry. Solution: short expiry (30 min) + refresh tokens.

---

### Q10: Explain the access token + refresh token pattern
**Answer:**
- **Access token**: Short-lived (15-30 min). Used for every API call. If stolen, attacker has limited window.
- **Refresh token**: Long-lived (7-30 days). Stored securely. Used ONLY to get a new access token.

**Flow:**
1. Login → get both tokens
2. Use access token for API calls
3. Access token expires
4. Send refresh token to `/auth/refresh` → get new access token
5. Refresh token expires → must login again

**Security benefit:** Even if an access token is intercepted, it expires quickly. The refresh token is only sent once in a while (not with every request), reducing exposure.

---

### Q11: What is CORS and how does it work?
**Answer:** CORS (Cross-Origin Resource Sharing) is a browser security mechanism that prevents JavaScript from making requests to a different origin than the page it loaded from.

**Origin** = protocol + domain + port. `https://app.com` ≠ `https://api.app.com`

**How it works:**
1. Browser sends preflight OPTIONS request with `Origin` header
2. Server responds with `Access-Control-Allow-Origin: https://app.com`
3. If allowed, browser makes the actual request

**In Flask:**
```python
from flask_cors import CORS
CORS(app, origins=["https://myapp.com"])
```

**Simple requests** (GET/POST with simple headers) skip the preflight.

---

### Q12: How do you handle API versioning?
**Answer:** Three strategies:
1. **URL path**: `/api/v1/products` — most common, explicit, easy to test
2. **Header**: `Accept: application/vnd.myapi.v2+json` — clean URLs, harder to test
3. **Query param**: `/products?version=2` — simple but non-standard

**Best practices:**
- Never break v1 when releasing v2
- Maintain old versions for at least 6-12 months
- Send deprecation headers: `X-API-Sunset-Date: 2025-12-31`
- Breaking changes = new version. Adding fields = backward compatible.

---

### Q13: What is rate limiting and how do you implement it?
**Answer:** Rate limiting restricts how many requests a client can make in a time window. Protects against:
- DDoS attacks
- Scraping
- Runaway client bugs
- Cost overruns

**Common strategies:**
- **Fixed window**: 100 requests per minute, counter resets at minute boundary
- **Sliding window**: Rolling 60-second window — smoother, no burst at reset
- **Token bucket**: Tokens replenish at fixed rate, burst allowed up to bucket size

**Response headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 37
X-RateLimit-Reset: 1234567890
Retry-After: 23
```
Return **429 Too Many Requests** when exceeded.

---

### Q14: What is BOLA and how do you prevent it?
**Answer:** BOLA (Broken Object Level Authorization) = IDOR (Insecure Direct Object Reference). It's when a user can access another user's resources by guessing/changing an ID in the URL.

**Vulnerable:**
```python
# Any authenticated user can access any order
@app.route('/orders/<int:id>')
@require_auth
def get_order(id):
    return Order.get(id)  # No ownership check!
```

**Secure:**
```python
@app.route('/orders/<int:id>')
@require_auth
def get_order(id):
    order = Order.get(id)
    if order.user_id != current_user.id and current_user.role != 'admin':
        return error("Forbidden", 403)
    return success(order)
```

It's the #1 API vulnerability (OWASP API Top 10).

---

### Q15: How do you design pagination for a large dataset?
**Answer:**

**Offset pagination** (simple):
```
GET /products?page=2&per_page=20
SQL: SELECT * FROM products LIMIT 20 OFFSET 20
```
Problem: If a new record is inserted on page 1 while browsing, page 2 shifts and you get duplicates.

**Cursor pagination** (robust):
```
GET /products?cursor=eyJpZCI6MjB9&limit=20
SQL: SELECT * FROM products WHERE id > 20 LIMIT 20
Response includes: {"next_cursor": "eyJpZCI6NDB9"}
```
Benefits: Stable (no drift), efficient (uses index), works with real-time data.

**Use cursor pagination for:** Social feeds, real-time data, large datasets.
**Use offset pagination for:** Admin panels, static data, when users need to jump to page N.

---

## 🔴 Senior Level (5-6 years)

### Q16: Design a REST API for a ride-sharing application
**Answer:** Key resources:

```
Riders:   GET/POST/PATCH /riders/{id}
Drivers:  GET/POST/PATCH /drivers/{id}
Rides:    GET/POST /rides
          GET /rides/{id}
          PATCH /rides/{id}/status   ← status machine: requested→accepted→in_progress→completed
          DELETE /rides/{id}         ← cancel
Locations: POST /drivers/{id}/location  ← driver location updates
Ratings:   POST /rides/{id}/ratings
Payments:  GET /rides/{id}/payment
           POST /rides/{id}/payment/retry

Design decisions:
- Rides use a state machine with valid transitions
- Driver location updates are frequent — consider WebSocket or SSE instead of polling
- Payments are separate from rides (different domain, compliance)
- Use cursor pagination for ride history
- Rate limit location update endpoint heavily
- Idempotency keys on payment endpoints
```

---

### Q17: How do you handle long-running operations in a REST API?
**Answer:** For operations that take more than a few seconds (video processing, report generation, bulk imports):

**Async job pattern:**
```
1. Client POSTs request:
   POST /reports/generate
   {"type": "monthly", "year": 2024}
   → 202 Accepted
   {"job_id": "job-abc123", "status_url": "/jobs/job-abc123"}

2. Client polls for status:
   GET /jobs/job-abc123
   → {"status": "processing", "progress": 45}
   → {"status": "completed", "result_url": "/reports/monthly-2024.pdf"}

3. Client downloads result:
   GET /reports/monthly-2024.pdf
```

**Alternatives:**
- **Webhooks**: Server calls your URL when done — no polling needed
- **WebSocket**: Real-time bidirectional — for interactive operations
- **SSE (Server-Sent Events)**: Server pushes updates — simpler than WebSocket

---

### Q18: What are your strategies for API backwards compatibility?
**Answer:**
1. **Additive changes only**: New fields, new endpoints — never remove/rename existing ones
2. **Strict semantic versioning**: Breaking change = major version bump
3. **Deprecation period**: Announce removal 6-12 months ahead with `Sunset` header
4. **Tolerant reader pattern**: Clients ignore unknown fields (don't break if server adds fields)
5. **API changelog**: Document all changes — make it easy for clients to upgrade
6. **Integration tests against old contract**: Before releasing, run tests that verify v1 still works

**Breaking changes that require versioning:**
- Remove a field or endpoint
- Change a field's type (string → number)
- Change authentication method
- Change error response format

---

### Q19: How would you implement webhook delivery reliably?
**Answer:**
```
Challenges:
- Delivery failures (client server is down)
- Ordering guarantees
- Security (is this really from us?)
- At-least-once vs exactly-once delivery

Reliable implementation:
1. Persist webhook events to DB before delivering
2. Sign payload: X-Webhook-Signature: HMAC-SHA256(payload, secret)
3. Retry with exponential backoff: 1s, 5s, 30s, 5min, 30min, 2h
4. Mark as failed after N retries
5. Allow client to replay failed events
6. Include event_id for idempotency — client deduplicates

Client verifies:
def verify_signature(payload, signature, secret):
    expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

### Q20: How do you design for high availability and performance?
**Answer:**
```
Caching layers:
  Client → CDN → Load Balancer → App Servers → Cache (Redis) → Database

API-level optimizations:
- Cache GET responses with ETags or Last-Modified headers
- Redis for session/token storage instead of DB
- Database query optimization (indexes on filtered fields)
- Connection pooling
- Async endpoints for I/O-bound operations (httpx, asyncio)

Horizontal scaling:
- Stateless design (JWT not sessions) allows any server to handle any request
- Database read replicas for GET-heavy workloads
- Rate limiting at the load balancer level

Response optimization:
- Sparse fieldsets: GET /products?fields=id,name,price (return only needed fields)
- Compression: Accept-Encoding: gzip
- Pagination to limit response size
- Lazy loading related resources
```

---

### Q21: Explain the CAP theorem and how it affects API design
**Answer:** CAP theorem states a distributed system can guarantee at most 2 of:
- **Consistency**: All nodes see the same data at the same time
- **Availability**: Every request gets a response (may not be latest data)
- **Partition tolerance**: System works despite network failures

**Practical API implications:**
- Most systems choose AP (available + partition tolerant) — return potentially stale data rather than error
- Bank APIs choose CP — better to be unavailable than show wrong balance
- Social feeds choose AP — a few seconds of staleness is fine

**For REST APIs:**
- Return cached/stale data with `X-Cache: HIT` header rather than fail
- Eventual consistency: `202 Accepted` + background sync + webhook when done
- Conflict resolution: use ETags + conditional PUT to detect concurrent updates

---

### Q22: How do you handle concurrency issues in REST APIs?
**Answer:**

**Optimistic locking with ETags:**
```
1. GET /products/1
   Response: ETag: "abc123", {"name": "Headphones", "price": 99}

2. Another user also GETs and starts editing

3. User A PUTs:
   PUT /products/1
   If-Match: "abc123"
   {"name": "Headphones", "price": 89}
   → 200 OK (version matched, update applied)

4. User B tries to PUT with old ETag:
   PUT /products/1
   If-Match: "abc123"
   {"name": "Headphones", "price": 79}
   → 412 Precondition Failed (someone else modified it)
   → Client must re-fetch and re-apply their change
```

**Pessimistic locking:** Acquire a lock before updating. Simpler but creates bottlenecks.

---

## 📋 Rapid-fire Questions (expect these in interviews)

| Question | Expected 1-line answer |
|----------|----------------------|
| What's the difference between authentication and authorization? | Auth = who are you; Authz = what can you do |
| What is an API gateway? | Reverse proxy that handles auth, rate limiting, routing for multiple services |
| What is GraphQL vs REST? | GraphQL: single endpoint, client specifies fields. REST: multiple endpoints, server specifies response |
| What status code for rate limiting? | 429 Too Many Requests |
| What header carries auth? | Authorization: Bearer \<token\> |
| What is a soft delete? | Set active=0 instead of DELETE from DB |
| When to use WebSocket vs REST? | WebSocket for real-time bidirectional (chat, games). REST for request-response |
| What is the OPTIONS method used for? | CORS preflight — asks server what methods are allowed |
| What is content negotiation? | Client and server agree on data format via Accept/Content-Type headers |
| What is an idempotency key? | Unique ID sent with POST to prevent duplicate operations on retry |
| What does 204 mean? | No Content — success but no body (common for DELETE) |
| What is HATEOAS? | API responses include links to what you can do next |
| What is the difference between HTTP and HTTPS? | HTTPS = HTTP + TLS encryption |
| What is a microservice? | Small, independently deployable service that does one thing |
| What is service discovery? | How microservices find each other's addresses (Consul, Kubernetes DNS) |

---

## 🧪 Coding Challenges (given in technical screens)

### Challenge 1: Build a rate limiter
```python
# Implement a class that rate-limits to N requests per window
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        ...

    def is_allowed(self, user_id: str) -> bool:
        """Return True if the request should proceed, False if rate limited"""
        ...
```

### Challenge 2: Retry with exponential backoff
```python
import requests, time

def call_with_retry(url: str, max_retries: int = 3) -> dict:
    """Call URL, retry on 5xx with exponential backoff"""
    ...
```

### Challenge 3: Paginate through all results
```python
def get_all_products(base_url: str) -> list:
    """Paginate through all pages of /products and return all items"""
    ...
```

### Challenge 4: Validate JWT without library
```python
import base64, hmac, hashlib, json

def validate_jwt(token: str, secret: str) -> dict:
    """Validate JWT signature and return payload, raise if invalid"""
    ...
```

---

## 💬 Behavioral Questions

- "Tell me about a complex API you designed. What tradeoffs did you make?"
- "Describe a time when an API change broke a client. How did you handle it?"
- "How do you document APIs? What tools have you used?"
- "How do you approach testing an API you didn't write?"
- "What's your process when designing a new endpoint?"
- "Tell me about a performance issue in an API you worked on. How did you diagnose and fix it?"
