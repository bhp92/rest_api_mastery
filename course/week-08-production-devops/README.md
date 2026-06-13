# Week 8 — Production, DevOps & Capstone
**Time:** 40 min/day × 5 days | **Goal:** Own an API end-to-end

See week-07-performance-caching/README.md Days 1-5 for the Week 8 content (combined).

---

## Capstone Project Brief

Build `solutions/week8/capstone_client.py` — a production-grade API client library for the practice server:

### Requirements:
1. **Auth management** — Login, auto-refresh, logout
2. **Products CRUD** — All operations with validation
3. **Orders workflow** — Create, status transitions, cancel
4. **Error handling** — Every HTTP error case handled
5. **Retry logic** — Exponential backoff on 429/5xx
6. **Logging** — All requests/responses logged
7. **Tests** — pytest suite with 90%+ coverage
8. **Docs** — Docstrings on every public method

### Grading yourself:
- Run `pytest solutions/week8/test_capstone.py -v`
- Run `pytest solutions/week8/ --cov=solutions/week8/capstone_client --cov-report=term-missing`
- All tests green + >90% coverage = interview ready ✅
