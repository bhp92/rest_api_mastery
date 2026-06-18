"""
Week 1 - Day 1: What is HTTP
File: day1_http.py
Run with: python3 exercises/week1/day1_http.py
"""

import requests  # WHY: 'requests' is a Python HTTP client - it builds the raw
                  # HTTP request (method, headers, body) and parses the raw
                  # HTTP response for us, so we don't hand-craft TCP packets.
import time       # WHY: lets us measure round-trip latency, a real signal
                  # senior engineers check when diagnosing slow APIs.

# BASE_URL is defined once at the top so if the server moves (different port,
# different host, ngrok tunnel, etc.) we change ONE line instead of hunting
# through every request call in the file.
BASE_URL = "http://localhost:5000"


def explore_health_endpoint():
    """
    Hits /health - the simplest possible endpoint - so we can see the full
    anatomy of an HTTP exchange without auth or payloads complicating it.
    """
    print("=" * 60)
    print("STEP 1: Sending a GET request to /health")
    print("=" * 60)

    # WHY time.time() before/after: HTTP is a network call - it travels over
    # TCP, hits the server process, gunicorn worker, Flask routing, and comes
    # back. Measuring this teaches you that EVERY HTTP call has real latency,
    # not just "function call" latency.
    start = time.time()

    # WHY requests.get(): this sends an HTTP request line that literally
    # reads "GET /health HTTP/1.1" on the wire, plus default headers like
    # Host and User-Agent. GET means "give me this resource, don't change
    # anything on the server" (a core REST/HTTP convention).
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    # WHY timeout=5: without a timeout, requests will hang forever if the
    # server never responds. A senior engineer NEVER calls a network API
    # without a timeout - it's how one slow dependency takes down your whole
    # service.

    elapsed_ms = (time.time() - start) * 1000

    # WHY check status_code first: the status code is the FIRST thing that
    # tells you if the request even succeeded, before you trust anything in
    # the body. 200 means "OK, here's your data." Anything else means
    # something went wrong upstream or downstream.
    print(f"Status Code : {response.status_code}")
    print(f"Latency     : {elapsed_ms:.2f} ms")

    # WHY print headers: headers carry METADATA about the response that
    # never appears in the body - e.g. Content-Type tells the client HOW to
    # parse the body (JSON? HTML? plain text?). Senior engineers inspect
    # headers when debugging caching, content negotiation, or CORS issues.
    print("\nResponse Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")

    # WHY response.json(): the server returns the body as raw text over the
    # wire. .json() parses that raw text into a Python dict ONLY IF the
    # Content-Type and body are actually valid JSON - this is why checking
    # Content-Type above matters before blindly calling .json().
    print("\nResponse Body (parsed JSON):")
    try:
        body = response.json()
        print(f"  {body}")
    except ValueError:
        # WHY this fallback exists: not every endpoint returns JSON (e.g.
        # /docs likely returns HTML). Defensive parsing avoids a crash.
        print("  (Body was not valid JSON, showing raw text instead)")
        print(f"  {response.text[:200]}")

    return response


def explore_docs_endpoint():
    """
    Hits /docs to show that NOT every endpoint returns JSON - this proves
    HTTP is content-agnostic. The protocol doesn't care if the body is
    JSON, HTML, or a binary file; Content-Type is what tells the client
    how to interpret it.
    """
    print("\n" + "=" * 60)
    print("STEP 2: Sending a GET request to /docs")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/docs", timeout=5)

    print(f"Status Code : {response.status_code}")

    # WHY we specifically pull Content-Type here: this is the header that
    # decides whether the body should be treated as HTML, JSON, etc.
    # Comparing it against /health's Content-Type makes the difference
    # concrete instead of abstract.
    content_type = response.headers.get("Content-Type", "unknown")
    print(f"Content-Type: {content_type}")
    print(f"Body length : {len(response.text)} characters")
    print(f"First 150 chars of body:\n  {response.text[:150]!r}")


def main():
    print("\nHTTP FUNDAMENTALS - DAY 1 EXERCISE\n")

    # WHY wrap in try/except ConnectionError: if the server isn't running
    # (systemd service stopped), requests raises a ConnectionError rather
    # than returning a response. Catching it gives a clear, actionable error
    # instead of an ugly traceback - exactly how you'd want a real client
    # to fail gracefully.
    try:
        explore_health_endpoint()
        explore_docs_endpoint()
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to the server.")
        print(f"        Is it running? Check with:")
        print(f"        sudo systemctl status rest-api-mastery")
        return

    print("\n" + "=" * 60)
    print("DONE. Compare the Content-Type and body shape between")
    print("/health and /docs - that's the core lesson for today.")
    print("=" * 60)


if __name__ == "__main__":
    # WHY this guard: it lets the file be imported elsewhere later (e.g. by
    # a test suite in Week 5) without auto-running main() on import. Only
    # runs main() when the file is executed directly, as the course's
    # `python3 exercises/week1/day1_http.py` command does.
    main()