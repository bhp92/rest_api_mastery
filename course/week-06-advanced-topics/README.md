# Week 6 — Advanced Topics: Async, Caching, Background Jobs
**Time:** 40 min/day × 5 days | **Goal:** Build production-grade patterns

---

## Day 1 — Async HTTP with httpx (40 min)

### Theory (10 min)
When your API needs to call OTHER APIs, use async to avoid blocking:
```
Sync (blocking):
  Call API 1 → wait 200ms → Call API 2 → wait 200ms → Total: 400ms

Async (non-blocking):
  Call API 1 and API 2 simultaneously → wait for both → Total: ~200ms
```

### Hands-on (30 min)
```python
# exercises/week6/day1_async.py
import asyncio
import httpx
import time

BASE = "http://localhost:5000"


async def fetch_product(client, product_id):
    r = await client.get(f"{BASE}/api/v1/products/{product_id}")
    return r.json()


async def fetch_all_products_async():
    """Fetch products 1-10 all at once"""
    async with httpx.AsyncClient() as client:
        tasks = [fetch_product(client, i) for i in range(1, 11)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception) and r.get('success')]


async def paginate_all(client, path, params=None):
    """Async pagination — fetch all pages"""
    params = params or {}
    params['page'] = 1
    params['per_page'] = 5
    all_items = []

    while True:
        r = await client.get(f"{BASE}{path}", params=params)
        data = r.json()
        all_items.extend(data['data'])

        pagination = data['meta']['pagination']
        if pagination['page'] >= pagination['total_pages']:
            break
        params['page'] += 1

    return all_items


async def main():
    # 1. Async parallel fetch
    start = time.time()
    products = await fetch_all_products_async()
    elapsed = time.time() - start
    print(f"Fetched {len(products)} products in {elapsed:.2f}s (async)")

    # 2. Async pagination
    async with httpx.AsyncClient() as client:
        all_products = await paginate_all(client, '/api/v1/products')
        print(f"Total products via async pagination: {len(all_products)}")

    # 3. Compare with sync
    start = time.time()
    import requests
    for i in range(1, 11):
        requests.get(f"{BASE}/api/v1/products/{i}")
    print(f"Sync sequential: {time.time()-start:.2f}s")


if __name__ == '__main__':
    asyncio.run(main())
```

---

## Day 2 — Caching Strategies (40 min)

### Theory (20 min)

**HTTP Caching headers:**
```
Response: Cache-Control: max-age=3600    ← cache for 1 hour
Response: ETag: "abc123"                 ← version identifier
Response: Last-Modified: Mon, 1 Jan 2024

Next request (conditional GET):
  If-None-Match: "abc123"
  → 304 Not Modified (no body, just confirms still valid)
  → or 200 OK with new data + new ETag
```

**Cache levels:**
```
Browser cache → CDN/Reverse proxy → App cache (Redis) → Database
```

**Cache-Control values:**
```
max-age=3600          ← cache for 3600 seconds
no-cache              ← always revalidate (check if still fresh)
no-store              ← never cache (sensitive data)
private               ← only browser cache (not CDN)
public                ← CDNs can cache too
must-revalidate       ← once expired, must revalidate before use
```

### Hands-on (20 min)
```python
# exercises/week6/day2_caching.py
import requests
import time

BASE = "http://localhost:5000"

# 1. Simulate client-side ETag caching
class CachingClient:
    def __init__(self):
        self.session = requests.Session()
        self.cache = {}  # url -> (etag, data)

    def get(self, url):
        cached = self.cache.get(url)
        headers = {}
        if cached:
            headers['If-None-Match'] = cached[0]

        r = self.session.get(url, headers=headers)

        if r.status_code == 304:
            print(f"  Cache HIT (304): {url}")
            return cached[1]
        elif r.status_code == 200:
            etag = r.headers.get('ETag', '')
            self.cache[url] = (etag, r.json())
            print(f"  Cache MISS (200): {url}, ETag: {etag}")
            return r.json()

client = CachingClient()

# First call — cache miss
products1 = client.get(f"{BASE}/api/v1/products")
# Second call — should be cache hit if server supports ETags
products2 = client.get(f"{BASE}/api/v1/products")

# 2. Measure performance benefit of caching
import time

# Without cache
times_no_cache = []
for _ in range(5):
    start = time.time()
    requests.get(f"{BASE}/api/v1/products")
    times_no_cache.append((time.time()-start)*1000)

print(f"\nAvg without cache: {sum(times_no_cache)/len(times_no_cache):.1f}ms")

# With simple in-memory cache
cache = {}
times_with_cache = []
for _ in range(5):
    start = time.time()
    if '/products' not in cache:
        r = requests.get(f"{BASE}/api/v1/products")
        cache['/products'] = r.json()
    result = cache['/products']
    times_with_cache.append((time.time()-start)*1000)

print(f"Avg with cache:    {sum(times_with_cache)/len(times_with_cache):.3f}ms")
```

---

## Day 3 — Request Retries & Resilience (40 min)

```python
# exercises/week6/day3_resilience.py
import requests
import time
import random
from functools import wraps

BASE = "http://localhost:5000"


def retry_with_backoff(max_retries=3, backoff_base=1.0, retry_on=(429, 500, 502, 503)):
    """Decorator: retry on specified status codes with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    # If it's a response object, check status
                    if hasattr(result, 'status_code') and result.status_code in retry_on:
                        if attempt < max_retries:
                            sleep_time = backoff_base * (2 ** attempt) + random.uniform(0, 0.5)
                            print(f"  ⚠️  Got {result.status_code}, retry {attempt+1}/{max_retries} in {sleep_time:.1f}s")
                            time.sleep(sleep_time)
                            continue
                    return result
                except requests.exceptions.ConnectionError:
                    if attempt < max_retries:
                        sleep_time = backoff_base * (2 ** attempt)
                        print(f"  ⚠️  Connection error, retry {attempt+1} in {sleep_time:.1f}s")
                        time.sleep(sleep_time)
                    else:
                        raise
            return result
        return wrapper
    return decorator


@retry_with_backoff(max_retries=3)
def get_products():
    return requests.get(f"{BASE}/api/v1/products", timeout=5)


class CircuitBreaker:
    """Opens after N failures, half-opens after timeout"""
    def __init__(self, failure_threshold=3, recovery_timeout=30):
        self.failure_count = 0
        self.threshold = failure_threshold
        self.timeout = recovery_timeout
        self.state = 'closed'  # closed=normal, open=blocking, half-open=testing
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half-open'
                print("Circuit half-open — testing...")
            else:
                raise Exception("Circuit OPEN — failing fast")

        try:
            result = func(*args, **kwargs)
            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
                print("Circuit closed again ✅")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.threshold:
                self.state = 'open'
                print(f"Circuit OPENED after {self.failure_count} failures ❌")
            raise


# Test retry
print("Testing retry with backoff:")
result = get_products()
print(f"Got {len(result.json()['data'])} products")
```

---

## Day 4 — Background Jobs Pattern (40 min)

```python
# exercises/week6/day4_background_jobs.py
"""
Simulates the async job pattern:
POST /jobs → 202 Accepted
GET /jobs/{id} → poll for status
"""
import requests
import time
import uuid

BASE = "http://localhost:5000"


class AsyncJobPoller:
    def __init__(self, base_url, auth_headers, max_wait=60, poll_interval=2):
        self.base = base_url
        self.headers = auth_headers
        self.max_wait = max_wait
        self.poll_interval = poll_interval

    def submit_and_wait(self, endpoint, payload):
        """Submit a job and poll until done"""
        # Submit
        r = requests.post(f"{self.base}{endpoint}", json=payload, headers=self.headers)
        if r.status_code not in (200, 201, 202):
            raise Exception(f"Job submission failed: {r.status_code} {r.json()}")

        data = r.json().get('data', {})
        job_id = data.get('job_id') or data.get('id')

        if not job_id or r.status_code != 202:
            # Sync operation — result is immediate
            return data

        # Poll for completion
        status_url = data.get('status_url', f"/jobs/{job_id}")
        start = time.time()

        while time.time() - start < self.max_wait:
            r = requests.get(f"{self.base}{status_url}", headers=self.headers)
            status_data = r.json().get('data', {})
            status = status_data.get('status', 'unknown')

            print(f"  Job {job_id}: {status} ({time.time()-start:.0f}s elapsed)")

            if status == 'completed':
                return status_data
            elif status == 'failed':
                raise Exception(f"Job failed: {status_data.get('error')}")

            time.sleep(self.poll_interval)

        raise TimeoutError(f"Job {job_id} didn't complete in {self.max_wait}s")


# Example: create an order (sync) and watch status transitions
def demo_order_workflow():
    # Login
    r = requests.post(f"{BASE}/api/v1/auth/login", json={"username":"alice","password":"password123"})
    user_headers = {"Authorization": f"Bearer {r.json()['data']['access_token']}"}

    r = requests.post(f"{BASE}/api/v1/auth/login", json={"username":"admin","password":"admin123"})
    admin_headers = {"Authorization": f"Bearer {r.json()['data']['access_token']}"}

    # Create order
    r = requests.post(f"{BASE}/api/v1/orders",
        json={"items": [{"product_id": 1, "quantity": 1}]},
        headers=user_headers
    )
    order = r.json()['data']
    print(f"\nOrder created: #{order['id']} (status: {order['status']})")

    # Walk through status transitions
    transitions = ['confirmed', 'processing', 'shipped', 'delivered']
    for new_status in transitions:
        time.sleep(0.3)
        r = requests.patch(f"{BASE}/api/v1/orders/{order['id']}/status",
                           json={"status": new_status}, headers=admin_headers)
        print(f"  → {new_status}: {r.status_code}")

    print("✅ Order completed full lifecycle!")


if __name__ == '__main__':
    demo_order_workflow()
```

---

## Day 5 — File Upload Automation & Week Review (40 min)

```python
# exercises/week6/day5_file_automation.py
import requests
import os
import io

BASE = "http://localhost:5000"

def get_headers():
    r = requests.post(f"{BASE}/api/v1/auth/login", json={"username":"alice","password":"password123"})
    return {"Authorization": f"Bearer {r.json()['data']['access_token']}"}

headers = get_headers()

# 1. Upload a file
content = b"product_id,name,price\n1,Widget,9.99\n2,Gadget,19.99"
files = {'file': ('products.csv', io.BytesIO(content), 'text/csv')}
r = requests.post(f"{BASE}/api/v1/files/upload", files=files, headers=headers)
print(f"Upload: {r.status_code}")
if r.status_code == 201:
    file_info = r.json()['data']
    print(f"  Saved as: {file_info['filename']}")
    print(f"  Size: {file_info['size_bytes']} bytes")
    print(f"  URL: {file_info['url']}")

    # 2. Download it back
    r2 = requests.get(f"{BASE}{file_info['url']}")
    print(f"\nDownload: {r2.status_code}")
    print(f"Content: {r2.text}")

# 3. Try invalid file type
bad_files = {'file': ('virus.exe', b'malware', 'application/octet-stream')}
r = requests.post(f"{BASE}/api/v1/files/upload", files=bad_files, headers=headers)
print(f"\nInvalid file type: {r.status_code} — {r.json()['error']}")

# 4. List all uploaded files
r = requests.get(f"{BASE}/api/v1/files", headers=headers)
print(f"\nAll files ({len(r.json()['data'])} total):")
for f in r.json()['data']:
    print(f"  {f['filename']:40} {f['size_bytes']} bytes")
```

---

## 📋 Week 6 Checklist
- [ ] Can make async HTTP requests with httpx
- [ ] Understand HTTP caching headers (ETag, Cache-Control)
- [ ] Can implement retry with exponential backoff
- [ ] Know the circuit breaker pattern
- [ ] Understand async job polling pattern
- [ ] Can upload and download files via API
- [ ] Completed week challenge
