#!/bin/bash
# quick-test.sh — Run a quick smoke test of the server
# Useful to run each morning to verify everything works

BASE="http://localhost:5000"
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

pass=0; fail=0

check() {
    local desc=$1
    local expected=$2
    local actual=$3
    if [ "$actual" == "$expected" ]; then
        echo -e "${GREEN}✓${NC} $desc"
        ((pass++))
    else
        echo -e "${RED}✗${NC} $desc (expected $expected, got $actual)"
        ((fail++))
    fi
}

echo "🔍 REST API Mastery — Smoke Tests"
echo "=================================="

# Health check
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE/health)
check "Health endpoint" "200" "$STATUS"

# Products list
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE/api/v1/products)
check "Products list" "200" "$STATUS"

# Single product
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE/api/v1/products/1)
check "Single product" "200" "$STATUS"

# 404 for missing product
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE/api/v1/products/99999)
check "Missing product 404" "404" "$STATUS"

# Login
TOKEN=$(curl -s -X POST $BASE/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"alice","password":"password123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)
[ -n "$TOKEN" ] && check "Login returns token" "1" "1" || check "Login returns token" "1" "0"

# Auth required
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE/api/v1/auth/me)
check "Auth required (no token)" "401" "$STATUS"

# Auth with token
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" $BASE/api/v1/auth/me)
check "Auth with token" "200" "$STATUS"

echo ""
echo "Results: ${GREEN}$pass passed${NC} | ${RED}$fail failed${NC}"
[ $fail -eq 0 ] && echo -e "${GREEN}All good! Ready to study 🚀${NC}" || echo -e "${RED}Some tests failed — check if server is running${NC}"
