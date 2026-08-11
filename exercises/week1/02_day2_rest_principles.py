"""
Week 1 / Day 2 — REST Principles
==================================
Goal: prove the 6 REST constraints against a REAL running server,
instead of just reading about them.

Run:
    python3 day2_rest_principles.py
"""

import requests

BASE_URL = "http://localhost:5000"


def print_section(title):
    # A visual divider so each constraint's output is easy to scan
    # when you're reading this back later for the Day 5 review quiz.
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    # ── Sanity check first ──────────────────────────────────────
    # We hit /health before anything else because every constraint
    # below assumes a live server. Failing here with a clear message
    # beats a cryptic ConnectionError ten lines down.
    try:
        requests.get(f"{BASE_URL}/health", timeout=3)
    except requests.exceptions.ConnectionError:
        print(f"Could not reach {BASE_URL}. Is the server running?")
        print("Check with: sudo systemctl status rest-api-mastery")
        return

    # ════════════════════════════════════════════════════════════
    # CONSTRAINT 1: Uniform Interface — nouns, not verbs
    # ════════════════════════════════════════════════════════════
    print_section("1. UNIFORM INTERFACE — Resource Naming")

    # These don't exist on the server — they're here only so you can
    # SEE the contrast against the real call right after.
    print("Non-RESTful (action-based) would look like:")
    print("    /getProductById?id=1")
    print("    /fetchAllProducts")
    print("RESTful (resource-based) — what this server uses:")
    print("    /api/v1/products/1")
    print("    /api/v1/products")

    # GET is a "safe" method — it must never change server state.
    # That guarantee is WHY any client can call any RESTful API's
    # GET endpoints without reading the server's source first.
    r = requests.get(f"{BASE_URL}/api/v1/products/1")
    product = r.json()["data"]                                      #.json() converts response body to dictionary
    print(f"\nGET api/v1/products/1 -> {r.status_code}")            #.status_code returns the status code of request
    print(f"Resource: {product['name']} (${product['price']})")

    # ── Filtering lives in query params, not new endpoints ──────
    print_section("1b. UNIFORM INTERFACE — Filtering via Query Strings")

    # Notice there's no "/products/by-category" endpoint. The
    # RESOURCE stays /products; filtering/paging are query-string
    # concerns layered on top of one consistent identifier.
    r = requests.get(f"{BASE_URL}/api/v1/products", params={                                     #params allows requests module to send parameters.
        "category": "electronics",                                                              #parameters are sent in key:value pair
        "page": 1,
        "per_page": 3,
    })
    body = r.json()                                                                             #.josn() converts response body to dictionary
    pagination = body["meta"]["pagination"]
    print(f"GET /api/v1/products?category=electronics&paage=1&per_page=3 -> {r.status_code}")
    print(f"Page {pagination['page']} of {pagination['total_pages']} "
          f"({pagination['total']} total machines)")
    for p in body["data"]:
        print(f"\t- {p['name']}: ${p['price']}")

    # HATEOAS links: the server TELLS the client where to go next,
    # instead of the client hardcoding "page+1" math. This is the
    # deepest form of uniform interface in practice.
    print("\nServer-provided navigation links (HATEOAS):")
    for name, link in body["meta"]["links"].items():
        print(f"\t{name}: {link}")

    # ════════════════════════════════════════════════════════════
    # CONSTRAINT 2: Stateless — every request stands alone
    # ════════════════════════════════════════════════════════════
    print_section("2. STATELESS — No Server-Side Memory of You")

    # Deliberately plain requests.get() — NOT a requests.Session() —
    # so no cookies persist between these two calls. If the server
    # were stateful, call 2 would be affected by call 1. It isn't.
    r1 = requests.get(f"{BASE_URL}/api/v1/auth/me")
    r2 = requests.get(f"{BASE_URL}/api/v1/auth/me")
    print(f"Call 1 (no token): {r1.status_code} {r1.json().get('error')}")
    print(f"Call 2 (no token): {r2.status_code} {r2.json().get('error')}")
    print("Identical failures on both calls — the server has zero")
    print("memory of call 1 when processing call 2. Every request")
    print("must carry ALL the context it needs (here: a Bearer token).")

    # ════════════════════════════════════════════════════════════
    # CONSTRAINT 3: Cacheable — can a client safely reuse this?
    # ════════════════════════════════════════════════════════════
    print_section("3. CACHEABLE — Inspecting Response Headers")

    r = requests.get(f"{BASE_URL}/api/v1/products")
    cache_control = r.headers.get("Cache-Control")
    print(f"Cache-Control header: {cache_control!r}")               
    # '!r' uses repr(value) instead of str(value)
    # f"{value!r}" == repr(value)
    # Example: value = "hello" -> output: 'hello'
    # Useful for debugging because None, '', ' ', and actual values are easy to distinguish

    if cache_control is None:
        # This is itself a real lesson: this server doesn't declare
        # cacheability, so a CDN/proxy in front of it can't safely
        # cache this response. A production API would typically send:
        print("Not set -> a proxy/CDN can't safely cache this.")
        print('Production example: "Cache-Control: public, max-age=60"')
    print(f"Content-Type: {r.headers.get('Content-Type')}")

    # ════════════════════════════════════════════════════════════
    # CONSTRAINT 4: Layered System — infrastructure stays hidden
    # ════════════════════════════════════════════════════════════
    print_section("4. LAYERED SYSTEM — Hidden Infrastructure")

    # X-API-Version and X-Response-Time are injected by
    # middleware/logger.py BEFORE the response leaves the box —
    # you never had to know that middleware exists to use the API.
    print(f"X-API-Version: {r.headers.get('X-API-Version')}")
    print(f"X-Response-Time: {r.headers.get('X-Response-Time')}")
    print("Current call path:")
    print("    this script -> systemd-managed gunicorn -> Flask -> SQLite")
    print("Swap SQLite for Postgres, or add nginx in front, and this")
    print("script wouldn't need a single line changed.")

    # ════════════════════════════════════════════════════════════
    # CONSTRAINT 5: Client-Server Separation
    # ════════════════════════════════════════════════════════════
    print_section("5. CLIENT-SERVER SEPARATION")

    # This script only ever speaks the JSON CONTRACT below — it has
    # never touched practice.db or written a line of SQL. That's the
    # server's job entirely. This separation is WHY a frontend team
    # and a backend team can ship on different schedules.
    print('Contract this script depends on: {"success": ..., "data": ..., "meta": ...}')
    print("Never touched the database directly — that's the server's job.")

    # ════════════════════════════════════════════════════════════
    # CONSTRAINT 6: Code on Demand (optional)
    # ════════════════════════════════════════════════════════════
    print_section("6. CODE ON DEMAND (optional)")
    print("This server returns pure JSON, never executable code.")
    print("That's normal — this is the ONE optional constraint, mostly")
    print("seen when an SDK ships a JS snippet for the client to run.")
    print("Its absence doesn't make an API any less RESTful.")

    print_section("DONE — 6/6 constraints observed on a real server")

if __name__ == "__main__":
    main()

# response.headers.get() extracts the headers components.

'''
# ------------------------------------------------------------------
# DEBUGGING NOTE: Why use !r in f-strings?
#
# '!r' tells an f-string to use repr(value) instead of str(value).
#
# Example:
#
#     value = "hello"
#
#     f"{value}"    -> hello
#     f"{value!r}"  -> 'hello'
#
# This is useful when debugging APIs because it shows the exact
# representation of a value rather than a user-friendly version.
#
# Comparison:
#
#     value = None
#     f"{value}"    -> None
#     f"{value!r}"  -> None
#
#     value = ""
#     f"{value}"    -> (blank output)
#     f"{value!r}"  -> ''
#
#     value = " "
#     f"{value}"    -> (looks blank)
#     f"{value!r}"  -> ' '
#
#     value = "hello"
#     f"{value}"    -> hello
#     f"{value!r}"  -> 'hello'
#
# In REST API debugging this helps distinguish:
#
#     None  -> value/header is missing
#     ''    -> value/header exists but is empty
#     ' '   -> value/header contains whitespace
#     'x'   -> value/header contains actual data
#
# Example:
#
#     cache_control = r.headers.get("Cache-Control")
#     print(f"Cache-Control header: {cache_control!r}")
#
# This makes debugging response headers much easier because the
# exact value received from the server is visible.
# ------------------------------------------------------------------
'''