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

- HTTP is a stateless, text-based request/response protocol built on TCP. Each request is fully self-contained — the server holds no memory of previous requests unless you explicitly carry state via tokens, cookies, or session IDs. This is why REST APIs need auth headers on every call instead of "logging in once."

- Every HTTP exchange has the same anatomy:
    - **a request line**: method + path + version.
    - **headers**: metadata about the request/response - content type, auth, caching.
    - **[Optional] body (the payload)**: Understanding this anatomy is what let's you debug any API issue by inspectig raw headers/status instead of guessing.

- The status code is a contract, not a suggestion:
    - **2xx**: success
    - **3xx**: redirect
    - **4xx**: client's fault
    - **5xx**: server's fault

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

### Real World Analogy
HTTP is like a ordering at a restaurant counter. You (the client) walk up and state a clear request: "One burger,no onions" (method+resource+parameters). The cashier doesn't remember you from yesterday, hence each order is independent (stateless). They hand back recipt with a status: "Order confirmed" (200), "We're out of buns" (404 - resource not found) or "Kitchen's on fire" (500 - Server error). The recipt (headers) tells you extra info like wait time, while the food iteself (body) is the actual payload you came for.