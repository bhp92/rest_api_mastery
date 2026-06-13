#!/usr/bin/env python3
"""
seed.py — Populate the practice database with realistic data
Run: python seed.py
"""
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random, json

DB = 'practice.db'

USERS = [
    ('admin',   'admin@example.com',   'admin123',   'admin', 'Admin',   'User'),
    ('alice',   'alice@example.com',   'password123','user',  'Alice',   'Smith'),
    ('bob',     'bob@example.com',     'password123','user',  'Bob',     'Jones'),
    ('charlie', 'charlie@example.com', 'password123','user',  'Charlie', 'Brown'),
    ('diana',   'diana@example.com',   'password123','user',  'Diana',   'Prince'),
]

PRODUCTS = [
    ('Wireless Headphones',    'Premium noise-cancelling headphones',  79.99,  'electronics', 50,  'SKU-ELEC-001'),
    ('Mechanical Keyboard',    'RGB backlit, Cherry MX switches',     129.99, 'electronics', 30,  'SKU-ELEC-002'),
    ('USB-C Hub',              '7-in-1 multiport adapter',             39.99,  'electronics', 100, 'SKU-ELEC-003'),
    ('Python Programming Book','Learn Python the Hard Way, 5th Ed',    34.99,  'books',       200, 'SKU-BOOK-001'),
    ('Clean Code',             'A Handbook of Agile Software',         44.99,  'books',       150, 'SKU-BOOK-002'),
    ('REST API Design Rulebook','Designing consistent RESTful APIs',   29.99,  'books',       120, 'SKU-BOOK-003'),
    ('Desk Lamp',              'LED adjustable brightness',             24.99,  'office',      75,  'SKU-OFFC-001'),
    ('Ergonomic Mouse Pad',    'Extra large with wrist support',       19.99,  'office',      200, 'SKU-OFFC-002'),
    ('Standing Desk Mat',      'Anti-fatigue mat, 3/4 inch thick',     59.99,  'office',      40,  'SKU-OFFC-003'),
    ('Coffee Mug 500ml',       'Ceramic, keeps coffee hot for 2hrs',    14.99,  'kitchen',     300, 'SKU-KTCH-001'),
    ('Water Bottle 1L',        'BPA-free, stainless steel',             24.99,  'kitchen',     250, 'SKU-KTCH-002'),
    ('Laptop Stand',           'Adjustable aluminium laptop riser',    49.99,  'electronics', 80,  'SKU-ELEC-004'),
    ('Blue Light Glasses',     'Anti-fatigue screen glasses',           22.99,  'accessories', 60,  'SKU-ACCR-001'),
    ('Webcam 1080p',           'Full HD with built-in microphone',     69.99,  'electronics', 45,  'SKU-ELEC-005'),
    ('Sticky Notes 500pk',     'Assorted colours, 76x76mm',             8.99,   'office',      500, 'SKU-OFFC-004'),
]

POSTS = [
    (2, 'Getting Started with REST APIs',          'REST stands for Representational State Transfer...', ['rest', 'api', 'beginners'], 1),
    (2, 'JWT Authentication Deep Dive',             'JSON Web Tokens are a compact way to securely transmit...', ['jwt', 'auth', 'security'], 1),
    (3, 'Pagination Best Practices',               'When your API returns large datasets...', ['api', 'pagination', 'design'], 1),
    (3, 'HTTP Status Codes Cheat Sheet',           'Knowing the right status code is important...', ['http', 'status-codes'], 1),
    (4, 'Python requests Library Tutorial',        'The requests library makes HTTP calls simple...', ['python', 'requests', 'tutorial'], 1),
    (4, 'API Testing with pytest',                 'Automated testing gives you confidence...', ['testing', 'pytest', 'automation'], 1),
    (5, 'Rate Limiting: Why and How',              'Rate limiting protects your API from abuse...', ['rate-limiting', 'security'], 1),
    (5, 'API Versioning Strategies',               'As your API evolves, versioning keeps things stable...', ['versioning', 'api', 'design'], 0),
]


def seed():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    # Init schema
    conn.executescript(open('database.py').read().split('db.executescript("""')[1].split('""")')[0])

    print("🌱 Seeding users...")
    for username, email, pw, role, first, last in USERS:
        try:
            conn.execute(
                "INSERT INTO users (username,email,password,role,first_name,last_name) VALUES (?,?,?,?,?,?)",
                (username, email, generate_password_hash(pw), role, first, last)
            )
        except Exception:
            pass

    print("🌱 Seeding products...")
    for name, desc, price, cat, stock, sku in PRODUCTS:
        try:
            conn.execute(
                "INSERT INTO products (name,description,price,category,stock,sku) VALUES (?,?,?,?,?,?)",
                (name, desc, price, cat, stock, sku)
            )
        except Exception:
            pass

    print("🌱 Seeding posts...")
    for user_id, title, content, tags, published in POSTS:
        try:
            conn.execute(
                "INSERT INTO posts (user_id,title,content,tags,published) VALUES (?,?,?,?,?)",
                (user_id, title, content, json.dumps(tags), published)
            )
        except Exception:
            pass

    print("🌱 Seeding orders...")
    statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered']
    for user_id in [2, 3, 4]:
        for _ in range(3):
            status = random.choice(statuses)
            conn.execute(
                "INSERT INTO orders (user_id, status, total) VALUES (?,?,?)",
                (user_id, status, round(random.uniform(20, 300), 2))
            )
            order_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            product_id = random.randint(1, len(PRODUCTS))
            qty = random.randint(1, 3)
            price = random.uniform(10, 100)
            conn.execute(
                "INSERT INTO order_items (order_id,product_id,quantity,price) VALUES (?,?,?,?)",
                (order_id, product_id, qty, round(price, 2))
            )

    conn.commit()
    conn.close()

    print("\n✅ Database seeded!")
    print("\n🔑 Test credentials:")
    print("   admin / admin123   (role: admin)")
    print("   alice / password123 (role: user)")
    print("   bob   / password123 (role: user)")


if __name__ == '__main__':
    seed()
