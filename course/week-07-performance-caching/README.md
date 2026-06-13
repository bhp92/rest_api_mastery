# Week 7 — Performance & Optimization
**Time:** 40 min/day × 5 days

---

## Key Topics & Exercises

### Day 1 — Profiling API calls
```python
# exercises/week7/day1_profiling.py
import requests, time, statistics

BASE = "http://localhost:5000"

def benchmark(name, func, runs=20):
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        func()
        times.append((time.perf_counter()-start)*1000)
    print(f"{name:40} avg={statistics.mean(times):.1f}ms  p95={sorted(times)[int(runs*0.95)]:.1f}ms  max={max(times):.1f}ms")

# Compare endpoints
benchmark("GET /products (no filter)",  lambda: requests.get(f"{BASE}/api/v1/products"))
benchmark("GET /products (category)",   lambda: requests.get(f"{BASE}/api/v1/products?category=electronics"))
benchmark("GET /products (search)",     lambda: requests.get(f"{BASE}/api/v1/products?search=headphones"))
benchmark("GET /products/1",            lambda: requests.get(f"{BASE}/api/v1/products/1"))
benchmark("GET /health",                lambda: requests.get(f"{BASE}/health"))
```

### Day 2 — Response size optimization
```python
# exercises/week7/day2_optimization.py
"""
Techniques to reduce response size:
1. Pagination (already covered)
2. Sparse fieldsets — only return requested fields
3. Compression — gzip
"""
import requests, gzip

BASE = "http://localhost:5000"

# 1. Measure uncompressed size
r = requests.get(f"{BASE}/api/v1/products")
print(f"Uncompressed: {len(r.content)} bytes, {len(r.json()['data'])} items")

# 2. Request compressed response
r = requests.get(f"{BASE}/api/v1/products",
                  headers={"Accept-Encoding": "gzip"})
print(f"Gzip requested: {len(r.content)} bytes (requests auto-decompresses)")

# 3. Pagination impact on size
for per_page in [5, 10, 20, 50]:
    r = requests.get(f"{BASE}/api/v1/products", params={"per_page": per_page})
    print(f"per_page={per_page}: {len(r.content)} bytes")
```

### Day 3 — Connection pooling & sessions
```python
# exercises/week7/day3_connection_pooling.py
import requests, time

BASE = "http://localhost:5000"
N = 30

# Without session (new connection each time)
start = time.time()
for _ in range(N):
    requests.get(f"{BASE}/api/v1/products/1")
print(f"No session:   {(time.time()-start):.2f}s for {N} requests")

# With session (connection reuse)
session = requests.Session()
start = time.time()
for _ in range(N):
    session.get(f"{BASE}/api/v1/products/1")
print(f"With session: {(time.time()-start):.2f}s for {N} requests")
# Sessions reuse TCP connections — faster for many requests to same host
```

### Day 4 — N+1 Query Problem
```python
# exercises/week7/day4_n_plus_1.py
"""
N+1 problem: fetching N items then making 1 extra call per item
Common in naive API clients

Example: Get orders AND fetch each order's details
"""
import requests, time

BASE = "http://localhost:5000"

def get_headers():
    r = requests.post(f"{BASE}/api/v1/auth/login", json={"username":"alice","password":"password123"})
    return {"Authorization": f"Bearer {r.json()['data']['access_token']}"}

headers = get_headers()

# ❌ N+1 — bad: 1 request for list + N requests for details
start = time.time()
orders = requests.get(f"{BASE}/api/v1/orders", headers=headers).json()['data']
for order in orders:
    detail = requests.get(f"{BASE}/api/v1/orders/{order['id']}", headers=headers).json()
n_plus_1_time = time.time() - start
print(f"N+1 approach: {n_plus_1_time:.2f}s ({len(orders)+1} requests)")

# ✅ Better: use the details endpoint which includes items
# In a well-designed API, GET /orders/{id} returns items inline
# Even better: implement batch endpoint GET /orders?ids=1,2,3
start = time.time()
all_orders = requests.get(f"{BASE}/api/v1/orders?per_page=100", headers=headers).json()
single_request_time = time.time() - start
print(f"Single request: {single_request_time:.2f}s (1 request)")
```

### Day 5 — Stress Testing
```python
# exercises/week7/day5_stress_test.py
import asyncio
import httpx
import time
import statistics

BASE = "http://localhost:5000"

async def make_requests(client, count=100):
    tasks = [client.get(f"{BASE}/api/v1/products") for _ in range(count)]
    start = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.time() - start

    successes = sum(1 for r in results if hasattr(r, 'status_code') and r.status_code == 200)
    rate_limited = sum(1 for r in results if hasattr(r, 'status_code') and r.status_code == 429)

    print(f"Sent: {count} | Success: {successes} | Rate-limited: {rate_limited} | Time: {elapsed:.2f}s")
    print(f"Throughput: {count/elapsed:.0f} req/s")

async def main():
    async with httpx.AsyncClient() as client:
        print("Stress test — 50 concurrent requests:")
        await make_requests(client, 50)
        print("\nStress test — 120 concurrent requests (should hit rate limit):")
        await make_requests(client, 120)

asyncio.run(main())
```

---

# Week 8 — Production & DevOps
**Time:** 40 min/day × 5 days

---

## Day 1 — Environment Configuration
```python
# server/config.py — Production-ready configuration
import os

class Config:
    SECRET_KEY    = os.environ.get('SECRET_KEY', 'change-in-production!')
    DATABASE      = os.environ.get('DATABASE_URL', 'practice.db')
    DEBUG         = False
    TESTING       = False
    RATE_LIMIT    = int(os.environ.get('RATE_LIMIT', '100'))
    LOG_LEVEL     = os.environ.get('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    DEBUG     = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    DEBUG  = False
    # Must set SECRET_KEY via env var in production

class TestingConfig(Config):
    TESTING  = True
    DATABASE = ':memory:'

configs = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     DevelopmentConfig,
}
```

```bash
# .env file (never commit to git!)
SECRET_KEY=super-secret-production-key-change-this
DATABASE_URL=postgresql://user:pass@localhost/mydb
RATE_LIMIT=200
LOG_LEVEL=WARNING
```

## Day 2 — Logging & Monitoring
```python
# exercises/week8/day2_monitoring.py
import requests, json, time
from datetime import datetime

BASE = "http://localhost:5000"

class APIMonitor:
    """Simple API health monitor"""
    def __init__(self, base_url, endpoints, interval=30):
        self.base = base_url
        self.endpoints = endpoints
        self.results = []

    def check(self):
        timestamp = datetime.utcnow().isoformat()
        for endpoint in self.endpoints:
            start = time.time()
            try:
                r = requests.get(f"{self.base}{endpoint}", timeout=5)
                elapsed = (time.time()-start)*1000
                self.results.append({
                    'timestamp': timestamp,
                    'endpoint':  endpoint,
                    'status':    r.status_code,
                    'latency_ms': round(elapsed, 2),
                    'healthy':   r.status_code == 200
                })
                icon = "✅" if r.status_code == 200 else "❌"
                print(f"{icon} {endpoint:40} {r.status_code}  {elapsed:.0f}ms")
            except Exception as e:
                self.results.append({
                    'timestamp': timestamp,
                    'endpoint':  endpoint,
                    'status':    0,
                    'error':     str(e),
                    'healthy':   False
                })
                print(f"❌ {endpoint}: {e}")

monitor = APIMonitor(BASE, [
    '/health',
    '/api/v1/products',
    '/api/v1/products/1',
    '/api/v1/users',
])
monitor.check()
```

## Day 3 — API Documentation
```markdown
# Writing good API docs — template for each endpoint

## Create Product
`POST /api/v1/products`

**Authentication:** Required (admin role)

**Request Body:**
| Field       | Type    | Required | Description         |
|-------------|---------|----------|---------------------|
| name        | string  | ✅        | Product name        |
| price       | number  | ✅        | Price (USD)         |
| category    | string  | ❌        | Product category    |
| stock       | integer | ❌        | Inventory count     |
| description | string  | ❌        | Product description |

**Example Request:**
```json
{
  "name": "Wireless Mouse",
  "price": 29.99,
  "category": "electronics",
  "stock": 100
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {"id": 42, "sku": "SKU-ABC123"},
  "message": "Product created"
}
```

**Error Responses:**
| Status | Reason |
|--------|--------|
| 400    | Missing required fields |
| 401    | Not authenticated |
| 403    | Not admin role |
```

## Day 4 — Docker & Deployment
```dockerfile
# server/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python seed.py

EXPOSE 5000
ENV FLASK_ENV=production

CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: ./server
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Day 5 — Capstone Project
Build a complete Python client that:
1. Authenticates with token management (auto-refresh)
2. Implements full CRUD for products and orders
3. Has 90%+ test coverage
4. Handles all error scenarios gracefully
5. Logs all API interactions
6. Has a retry mechanism for transient failures

See `solutions/week8/capstone_client.py` for reference.

---

## 📋 Weeks 7-8 Checklist
- [ ] Can profile API performance and identify bottlenecks
- [ ] Understand connection pooling benefits
- [ ] Know the N+1 problem and how to avoid it
- [ ] Can stress-test an API
- [ ] Understand 12-factor app configuration
- [ ] Can write API monitoring scripts
- [ ] Can write API documentation
- [ ] Have a working Docker setup
- [ ] Completed capstone project
