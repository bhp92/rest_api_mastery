## Day 3 — JSON & Request/Response Structure (40 min)

### Theory (15 min)
JSON is the universal language of REST APIs.

- **JSON is a serialization contract, not your data model.** The server returns a stable envelope - `{success, data, meta}` - so any client can parse predictably accross any endpoint. `data` is payload, `meta` carries cross cutting info like pagination. The `Content-Type: application/json` header is what actually tells both sides "read this body as JSON." The shape is a promise you consume and validate.

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

### Real-world analogy

A JSON response is a shipping package from a warehouse. The contents are data (what you actually ordered). The packing slip taped on top is meta (tracking number, "item 1 of 100", page count). And Content-Type: application/json is the customs label declaring what's inside — if the label says "electronics" but the box is full of glass, you'd want to know before you reach in. A good warehouse ships every box with the same internal layout, so you always know exactly where the packing slip is. That consistent layout is the response envelope.

### Questions

#### Q1 — json= vs data= in the requests library

Q: When you POST a body with requests.post(url, json=payload) instead of data=payload, what two things does json= do for you? And if you used data= by mistake against a JSON-only endpoint, what comes back?

A:

json= does two things:
Serializes the Python dict into a JSON string via json.dumps().
Sets the Content-Type: application/json header automatically.
Direction mnemonic (the easy one to flip):
json.dumps() → dump to a string = outbound / serialize. This is what json= uses.
json.loads() → load from a string = inbound / parse. This is what r.json() uses.
data= with a dict does not just "force values to strings." It form-encodes the dict into key=value&key2=value2 and sets Content-Type: application/x-www-form-urlencoded.
Failure prediction: a JSON-only endpoint receives a form body with a form content-type. The precise status is 415 Unsupported Media Type — the code that literally means "I don't accept that Content-Type." (If a server instead tries to parse the body and finds no JSON where it expected some, you can also see 400 Bad Request.)

- One-liner: json= = json.dumps() + Content-Type: application/json; data= = form-encoding; the mismatch → 415.

#### Q2 — When does .json() throw, and can you assume the status was 400?

Q: Your code calls r.json() and it raises. What caused it — and is the status code necessarily 400?

A:

.json() throws because the body isn't valid JSON. That is independent of the status code.
Classic trap: the server hits an unhandled exception and returns a 500 with an HTML stack-trace page (Content-Type: text/html). You got a response, but r.json() raises JSONDecodeError, and the status is 500, not 400.
Two separate axes — keep them apart:
status_code → what happened (success / error).
Content-Type → how to read the body.
A 400 can carry perfectly valid JSON (its error envelope), and a 200 can occasionally hand you something unparseable. Never infer body format from the status code.
Guard it: check Content-Type first, or wrap .json() in a try/except.

- One-liner: status code = what happened; Content-Type = how to read the body. Guard .json() — don't trust the status.

#### Vocabulary to keep crisp

| Term | Direction | Used by |
|------|-----------|---------|
| json.dumps() | Python → JSON string (serialize, outbound) | requests json= kwarg |
| json.loads() | JSON string → Python (parse, inbound) | r.json() |
| application/json | body is JSON | correct header for a JSON API |
| application/x-www-form-urlencoded | body is a form | what data=<dict> sends |
| 415 Unsupported Media Type | "I don't accept that Content-Type" | wrong body format sent |
| 400 Bad Request | "your body/params are malformed" | valid type, bad content |