# Week 5 — Automation & Testing with pytest
**Time:** 40 min/day × 5 days | **Goal:** Write a full automated test suite

---

## Day 1 — pytest Fundamentals (40 min)

### Setup
```bash
cd rest-api-mastery
source server/venv/bin/activate
pip install pytest pytest-cov faker
```

### Theory (10 min)
```
pytest test discovery:
  - Files named test_*.py or *_test.py
  - Functions named test_*
  - Classes named Test*

Test structure — AAA pattern:
  Arrange  → set up test data/state
  Act      → call the code under test
  Assert   → verify the result
```

### Hands-on (30 min)
```python
# exercises/week5/test_products.py
import pytest
import requests

BASE = "http://localhost:5000"


@pytest.fixture(scope="session")
def admin_token():
    """Get admin JWT token once for the whole test session"""
    r = requests.post(f"{BASE}/api/v1/auth/login",
                      json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    return r.json()['data']['access_token']


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def new_product(admin_headers):
    """Create a product, yield it for the test, then clean up"""
    r = requests.post(f"{BASE}/api/v1/products",
                      json={"name": "Test Widget", "price": 9.99, "category": "test", "stock": 50},
                      headers=admin_headers)
    assert r.status_code == 201
    product_id = r.json()['data']['id']
    yield product_id
    # Teardown — delete after test
    requests.delete(f"{BASE}/api/v1/products/{product_id}", headers=admin_headers)


class TestProductsEndpoint:

    def test_list_products_returns_200(self):
        r = requests.get(f"{BASE}/api/v1/products")
        assert r.status_code == 200

    def test_list_products_has_pagination_meta(self):
        r = requests.get(f"{BASE}/api/v1/products")
        data = r.json()
        assert 'meta' in data
        assert 'pagination' in data['meta']
        assert 'page' in data['meta']['pagination']
        assert 'total' in data['meta']['pagination']

    def test_list_products_pagination(self):
        r = requests.get(f"{BASE}/api/v1/products", params={"per_page": 3})
        data = r.json()
        assert len(data['data']) <= 3

    def test_get_existing_product(self):
        r = requests.get(f"{BASE}/api/v1/products/1")
        assert r.status_code == 200
        product = r.json()['data']
        assert 'id' in product
        assert 'name' in product
        assert 'price' in product

    def test_get_nonexistent_product_returns_404(self):
        r = requests.get(f"{BASE}/api/v1/products/99999")
        assert r.status_code == 404
        assert r.json()['success'] is False

    def test_create_product_requires_auth(self):
        r = requests.post(f"{BASE}/api/v1/products",
                          json={"name": "X", "price": 1.0})
        assert r.status_code == 401

    def test_create_product_as_admin(self, admin_headers, new_product):
        r = requests.get(f"{BASE}/api/v1/products/{new_product}")
        assert r.status_code == 200
        assert r.json()['data']['name'] == 'Test Widget'

    def test_filter_by_category(self):
        r = requests.get(f"{BASE}/api/v1/products", params={"category": "electronics"})
        for product in r.json()['data']:
            assert product['category'] == 'electronics'

    def test_filter_by_price_range(self):
        r = requests.get(f"{BASE}/api/v1/products", params={"min_price": 20, "max_price": 50})
        for product in r.json()['data']:
            assert 20 <= product['price'] <= 50

    @pytest.mark.parametrize("missing_field", [
        {"price": 9.99},                    # missing name
        {"name": "X"},                      # missing price
        {},                                 # missing all
    ])
    def test_create_product_missing_fields(self, admin_headers, missing_field):
        r = requests.post(f"{BASE}/api/v1/products", json=missing_field, headers=admin_headers)
        assert r.status_code == 400

    def test_patch_product(self, admin_headers, new_product):
        r = requests.patch(f"{BASE}/api/v1/products/{new_product}",
                           json={"price": 19.99}, headers=admin_headers)
        assert r.status_code == 200
        # Verify the update took effect
        r2 = requests.get(f"{BASE}/api/v1/products/{new_product}")
        assert r2.json()['data']['price'] == 19.99
```

Run it:
```bash
cd exercises/week5
pytest test_products.py -v
```

---

## Day 2 — Auth & Security Tests (40 min)

```python
# exercises/week5/test_auth.py
import pytest
import requests
import uuid

BASE = "http://localhost:5000"


@pytest.fixture
def unique_user():
    uid = uuid.uuid4().hex[:8]
    return {
        "username": f"testuser_{uid}",
        "email":    f"test_{uid}@example.com",
        "password": "testpass123"
    }


class TestAuthEndpoints:

    def test_register_new_user(self, unique_user):
        r = requests.post(f"{BASE}/api/v1/auth/register", json=unique_user)
        assert r.status_code == 201
        data = r.json()['data']
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_register_duplicate_username(self, unique_user):
        requests.post(f"{BASE}/api/v1/auth/register", json=unique_user)
        r = requests.post(f"{BASE}/api/v1/auth/register", json=unique_user)
        assert r.status_code == 409

    def test_register_invalid_email(self, unique_user):
        unique_user['email'] = "not-an-email"
        r = requests.post(f"{BASE}/api/v1/auth/register", json=unique_user)
        assert r.status_code == 400

    def test_login_success(self):
        r = requests.post(f"{BASE}/api/v1/auth/login",
                          json={"username": "alice", "password": "password123"})
        assert r.status_code == 200
        assert 'access_token' in r.json()['data']

    def test_login_wrong_password(self):
        r = requests.post(f"{BASE}/api/v1/auth/login",
                          json={"username": "alice", "password": "wrongpass"})
        assert r.status_code == 401

    def test_me_with_valid_token(self):
        r = requests.post(f"{BASE}/api/v1/auth/login",
                          json={"username": "alice", "password": "password123"})
        token = r.json()['data']['access_token']
        r2 = requests.get(f"{BASE}/api/v1/auth/me",
                          headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 200
        assert r2.json()['data']['username'] == 'alice'

    def test_me_without_token(self):
        r = requests.get(f"{BASE}/api/v1/auth/me")
        assert r.status_code == 401

    def test_me_with_garbage_token(self):
        r = requests.get(f"{BASE}/api/v1/auth/me",
                         headers={"Authorization": "Bearer garbage123"})
        assert r.status_code == 401

    def test_token_not_in_response_body(self):
        """Security test: no sensitive data exposed in error responses"""
        r = requests.post(f"{BASE}/api/v1/auth/login",
                          json={"username": "alice", "password": "wrong"})
        body = r.text
        assert 'password' not in body.lower() or 'wrong' not in body
```

---

## Day 3 — Integration Tests & Fixtures (40 min)

```python
# exercises/week5/test_orders_integration.py
import pytest
import requests

BASE = "http://localhost:5000"


@pytest.fixture(scope="module")
def user_session():
    """Full user login session"""
    r = requests.post(f"{BASE}/api/v1/auth/login",
                      json={"username": "bob", "password": "password123"})
    token = r.json()['data']['access_token']
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": r.json()['data']['user']['id']
    }


@pytest.fixture(scope="module")
def available_product():
    """Get a product that has stock"""
    r = requests.get(f"{BASE}/api/v1/products", params={"per_page": 1})
    products = [p for p in r.json()['data'] if p['stock'] > 0]
    assert products, "No products with stock available"
    return products[0]


class TestOrderWorkflow:
    """Integration test: full order lifecycle"""

    def test_create_order(self, user_session, available_product):
        r = requests.post(f"{BASE}/api/v1/orders",
            json={"items": [{"product_id": available_product['id'], "quantity": 1}]},
            headers=user_session['headers']
        )
        assert r.status_code == 201
        order = r.json()['data']
        assert order['status'] == 'pending'
        assert order['total'] > 0
        # Store order_id for next tests
        TestOrderWorkflow.order_id = order['id']

    def test_order_appears_in_list(self, user_session):
        r = requests.get(f"{BASE}/api/v1/orders", headers=user_session['headers'])
        assert r.status_code == 200
        order_ids = [o['id'] for o in r.json()['data']]
        assert TestOrderWorkflow.order_id in order_ids

    def test_valid_status_transition(self, user_session):
        admin_r = requests.post(f"{BASE}/api/v1/auth/login",
                                json={"username":"admin","password":"admin123"})
        admin_h = {"Authorization": f"Bearer {admin_r.json()['data']['access_token']}"}

        r = requests.patch(f"{BASE}/api/v1/orders/{TestOrderWorkflow.order_id}/status",
                           json={"status": "confirmed"}, headers=admin_h)
        assert r.status_code == 200

    def test_invalid_status_transition(self, user_session):
        admin_r = requests.post(f"{BASE}/api/v1/auth/login",
                                json={"username":"admin","password":"admin123"})
        admin_h = {"Authorization": f"Bearer {admin_r.json()['data']['access_token']}"}

        # Can't go from confirmed → delivered (must go confirmed→processing→shipped→delivered)
        r = requests.patch(f"{BASE}/api/v1/orders/{TestOrderWorkflow.order_id}/status",
                           json={"status": "delivered"}, headers=admin_h)
        assert r.status_code == 422
```

---

## Day 4 — Test Coverage & Reporting (40 min)

```bash
# Run tests with coverage report
pytest exercises/week5/ -v --cov=. --cov-report=html --cov-report=term

# Run specific test class
pytest exercises/week5/test_products.py::TestProductsEndpoint -v

# Run parametrized tests only
pytest exercises/week5/ -k "parametrize" -v

# Run and stop on first failure
pytest exercises/week5/ -x

# Run and show print output
pytest exercises/week5/ -s -v
```

**Good test coverage targets:**
- Happy path (success cases): 100%
- Error cases (4xx responses): 100%  
- Edge cases (empty data, boundaries): 80%+
- Security tests (auth, permissions): 100%

---

## Day 5 — Automation Scripts (40 min)

```python
# exercises/week5/automation.py — Bulk operations and data generation
import requests
import random
from faker import Faker

BASE = "http://localhost:5000"
fake = Faker()


def bulk_create_users(count=10):
    """Automate creating many test users"""
    admin_r = requests.post(f"{BASE}/api/v1/auth/login", json={"username":"admin","password":"admin123"})
    headers = {"Authorization": f"Bearer {admin_r.json()['data']['access_token']}"}

    created = []
    for i in range(count):
        user = {
            "username":   fake.user_name() + str(random.randint(100, 999)),
            "email":      fake.email(),
            "password":   "testpass123",
            "first_name": fake.first_name(),
            "last_name":  fake.last_name(),
        }
        r = requests.post(f"{BASE}/api/v1/auth/register", json=user)
        if r.status_code == 201:
            created.append(user)
            print(f"✅ Created: {user['username']}")
        else:
            print(f"❌ Failed: {r.json().get('error')}")

    print(f"\nCreated {len(created)}/{count} users")
    return created


def load_test(endpoint, requests_count=50):
    """Simple load test"""
    import time
    times = []
    for i in range(requests_count):
        start = time.time()
        r = requests.get(f"{BASE}{endpoint}")
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        if i % 10 == 0:
            print(f"  Request {i}: {elapsed:.1f}ms (status: {r.status_code})")

    print(f"\nLoad test results for {endpoint}:")
    print(f"  Avg: {sum(times)/len(times):.1f}ms")
    print(f"  Min: {min(times):.1f}ms")
    print(f"  Max: {max(times):.1f}ms")
    print(f"  P95: {sorted(times)[int(len(times)*0.95)]:.1f}ms")


if __name__ == '__main__':
    bulk_create_users(5)
    load_test("/api/v1/products", 20)
```

---

## 📋 Week 5 Checklist
- [ ] Know pytest fixtures (scope: function, module, session)
- [ ] Can write parametrized tests
- [ ] Understand AAA test pattern
- [ ] Can measure test coverage
- [ ] Built integration tests with proper setup/teardown
- [ ] Written automation scripts for bulk operations
- [ ] Completed week challenge
