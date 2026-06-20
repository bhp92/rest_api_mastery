## Day 2 — REST Principles (40 min)

### Theory (20 min)
REST = **RE**presentational **S**tate **T**ransfer — an architectural style (not a protocol).

- REST is an architectural style, not a protocol. It'set of 6 constraints that HTTP happens to satisfy well. A senior engineer evaluates any API design against these contraints, not against "does it return JSON"

**6 REST Constraints:**

| Constraint | What it means | Example |
|-----------|--------------|---------|
| **Client-Server** | UI and data are separate | React frontend + Flask API |
| **Stateless** | Each request is self-contained | No server-side sessions |
| **Cacheable** | Responses declare if they can be cached | `Cache-Control` header |
| **Uniform Interface** | Consistent resource naming | `/api/v1/users/{id}` |
| **Layered System** | Client doesn't know about intermediaries | Load balancers, CDNs |
| **Code on Demand** | Server can send executable code (optional) | JavaScript delivery |

- Uniform Interface is the constraint that does the heav lifting. Resources are nouns (/product/5), HTTP methods are the verbs, and filtering/sorting/pagition live in query strings, never in new endpoints (/getProdcutsByCategory is a design smell)

**Resources vs. Actions:**
```
❌ Non-RESTful (action-based):
  /getUser?id=5
  /createNewProduct
  /deleteOrderById?id=3

✅ RESTful (resource-based):
  GET    /users/5
  POST   /products
  DELETE /orders/3
```

**Resource Naming Rules:**
```
✅ Use nouns, not verbs:   /products  not  /getProducts
✅ Use plural nouns:        /users     not  /user
✅ Use lowercase + hyphens: /order-items  not  /orderItems
✅ Nest related resources:  /users/5/orders
✅ Query strings for filters: /products?category=books&page=2
```

- Statelessness is a scalability decision, not justa style rule. Because no request depends on server-side session memory, you can load-balance across N idetical server instances with zero sticky-session logic. It's why REST APIs horizontally scane so easily compared to stateful protocols

### Hands-on (20 min)
```bash
# Look at how the practice server follows REST principles
curl http://localhost:5000/api/v1/products
curl http://localhost:5000/api/v1/products?category=books
curl http://localhost:5000/api/v1/products?page=1&per_page=3

# Notice: /products is the resource, filtering is in query params
# Notice: response includes pagination metadata
```

### Real World Analogy
A restaurant eu with item number. You don't need to know how the kitchen works (layered system) you just say "I'll have #14" (resource + identifier). The waiter doesn't remember your previous order when taking the next one (stateless), every order ticket has everything needed on it. And the menu format is the same wheather you're a regular or a first timer (uniform interface).