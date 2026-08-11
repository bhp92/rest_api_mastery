#!/usr/bin/env python3
"""
Week 1 · Day 3 — JSON & Request/Response Structure
Type it out, don't paste. Fill each STEP yourself.
Run after each step:  python3 day3_json.py
"""

import requests   # HTTP client: turns (method + url) into a real request/response
import json       # lets us serialize + pretty-print JSON ourselves

BASE_URL = "http://localhost:5000"   # one source of truth so paths below stay short


# ─────────────────────────────────────────────────────────────
# STEP 1 — Parse a JSON response and walk its nested structure
# WHY: the server returns a consistent envelope {success, data, meta}.
#      Knowing the shape is what lets you reach nested values safely.
# ─────────────────────────────────────────────────────────────

# ✏️ TASK 1a: GET /api/v1/products, store the Response object in `r`.

r = requests.get(f"{BASE_URL}/api/v1/products", timeout=5)

# ✏️ TASK 1b: turn the response body into a Python object (dict/list).
#            requests has a method that runs json.loads() for you.
data = r.json()

print("STATUS:", r.status_code)              # check success FIRST, before touching the body
print("TOP-LEVEL KEYS:", list(data.keys()))  # prove the envelope shape to yourself

# ✏️ TASK 1c: pull the total product count out of meta → pagination → total
total = data['meta']['pagination']['total']
# ✏️ TASK 1d: pull the name of the FIRST product out of data[0]
first_name = data['data'][0]['name']

print("TOTAL PRODUCTS:", total)
print("FIRST PRODUCT:", first_name)


# ─────────────────────────────────────────────────────────────
# STEP 2 — Send a JSON body (create a resource)
# WHY: for POST/PUT/PATCH you push data UP to the server.
# ─────────────────────────────────────────────────────────────

new_user = {                          # a Python dict maps 1:1 to a JSON object {...}
    "username": "testuser",
    "email": "test@example.com",
    "password": "mypassword",
    "first_name": "Test",
    "last_name": "User",
}

# ✏️ TASK 2: POST new_user to /api/v1/auth/register, store it in `r2`.
#   Use the json= keyword — NOT data=.
#   WHY json=: it (1) serializes the dict to a JSON string AND
#             (2) sets Content-Type: application/json for you.
#   data= would send form-encoded bytes with the wrong header.
r2 = requests.post(f"{BASE_URL}/api/v1/auth/register", json=new_user)

print("\nREGISTER STATUS:", r2.status_code)   # 201 created? 409 exists? 400 bad body?
print(json.dumps(r2.json(), indent=2))        # pretty-print what the server echoed back


# ─────────────────────────────────────────────────────────────
# STEP 3 — Prove the contract: header + envelope
# WHY: a client uses Content-Type to decide HOW to read the body.
# ─────────────────────────────────────────────────────────────

# ✏️ TASK 3: GET /api/v1/products/1, store it in `r3`.
r3 = requests.get(f"{BASE_URL}/api/v1/products/1", timeout=5)

# WHY: the server DECLARES the format here. If this isn't application/json,
#      calling .json() would blow up — so never assume, read the label.
print("\nCONTENT-TYPE:", r3.headers.get("Content-Type"))
print("SUCCESS FLAG:", r3.json().get("success"))   # envelope tells you ok vs error


# ─────────────────────────────────────────────────────────────
# STEP 4 — Capstone: a reusable pretty-printer
# WHY: you'll inspect dozens of endpoints; wrap the boilerplate once.
# ─────────────────────────────────────────────────────────────

def api_call(method, path, **kwargs):
    # ✏️ TASK 4a: call the right requests method dynamically, store in `resp`.
    #   Hint: getattr(requests, "get") IS requests.get.
    #   WHY dynamic: one helper serves get/post/put/delete.
    resp = getattr(requests, method)(f"{BASE_URL}{path}", **kwargs)
    print(f"\n{method.upper()} {path} → {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))
    return resp   # return it so the caller can keep inspecting

# ✏️ TASK 4b: use your helper to GET /api/v1/products/2
api_call('get', '/api/v1/products/2')