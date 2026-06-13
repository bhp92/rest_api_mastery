"""
REST API Mastery — Practice Server
===================================
A fully-featured dummy REST API server for hands-on learning.
Covers: CRUD, Auth, Pagination, Rate Limiting, Versioning, File Upload, WebHooks, and more.

Run:
    cd server
    source venv/bin/activate
    python app.py

Base URL: http://localhost:5000
API v1:   http://localhost:5000/api/v1
API v2:   http://localhost:5000/api/v2
Docs:     http://localhost:5000/docs
"""

from flask import Flask
from flask_cors import CORS
from database import init_db
from routes.health import health_bp
from routes.users import users_bp
from routes.products import products_bp
from routes.orders import orders_bp
from routes.auth import auth_bp
from routes.posts import posts_bp
from routes.files import files_bp
from routes.webhooks import webhooks_bp
from routes.v2.products import products_v2_bp
from middleware.rate_limiter import RateLimiter
from middleware.logger import setup_logger
import os

app = Flask(__name__)
CORS(app)

# ── Config ────────────────────────────────────────────────────
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod-abc123')
app.config['DATABASE'] = os.environ.get('DATABASE', 'practice.db')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ── Middleware ────────────────────────────────────────────────
setup_logger(app)
rate_limiter = RateLimiter(app)

# ── Database ──────────────────────────────────────────────────
with app.app_context():
    init_db()

# ── Routes ────────────────────────────────────────────────────
app.register_blueprint(health_bp)
app.register_blueprint(auth_bp,     url_prefix='/api/v1/auth')
app.register_blueprint(users_bp,    url_prefix='/api/v1/users')
app.register_blueprint(products_bp, url_prefix='/api/v1/products')
app.register_blueprint(orders_bp,   url_prefix='/api/v1/orders')
app.register_blueprint(posts_bp,    url_prefix='/api/v1/posts')
app.register_blueprint(files_bp,    url_prefix='/api/v1/files')
app.register_blueprint(webhooks_bp, url_prefix='/api/v1/webhooks')

# API v2 — demonstrates versioning
app.register_blueprint(products_v2_bp, url_prefix='/api/v2/products')

# ── Docs endpoint ─────────────────────────────────────────────
@app.route('/docs')
def docs():
    return {
        "name": "REST API Mastery Practice Server",
        "version": "1.0.0",
        "description": "Your hands-on REST API learning playground",
        "endpoints": {
            "health":    "GET  /health",
            "auth": {
                "register": "POST /api/v1/auth/register",
                "login":    "POST /api/v1/auth/login",
                "refresh":  "POST /api/v1/auth/refresh",
                "logout":   "POST /api/v1/auth/logout",
                "me":       "GET  /api/v1/auth/me",
            },
            "users": {
                "list":    "GET    /api/v1/users",
                "get":     "GET    /api/v1/users/{id}",
                "create":  "POST   /api/v1/users",
                "update":  "PUT    /api/v1/users/{id}",
                "patch":   "PATCH  /api/v1/users/{id}",
                "delete":  "DELETE /api/v1/users/{id}",
                "search":  "GET    /api/v1/users?search=name&role=admin",
            },
            "products": {
                "list":     "GET    /api/v1/products",
                "get":      "GET    /api/v1/products/{id}",
                "create":   "POST   /api/v1/products",
                "update":   "PUT    /api/v1/products/{id}",
                "delete":   "DELETE /api/v1/products/{id}",
                "search":   "GET    /api/v1/products?category=electronics&min_price=10",
                "paginate": "GET    /api/v1/products?page=1&per_page=10",
            },
            "orders": {
                "list":   "GET    /api/v1/orders",
                "get":    "GET    /api/v1/orders/{id}",
                "create": "POST   /api/v1/orders",
                "status": "PATCH  /api/v1/orders/{id}/status",
                "cancel": "DELETE /api/v1/orders/{id}",
            },
            "posts":  "GET|POST|PUT|PATCH|DELETE /api/v1/posts",
            "files": {
                "upload":   "POST /api/v1/files/upload",
                "download": "GET  /api/v1/files/{filename}",
            },
            "webhooks": {
                "register": "POST /api/v1/webhooks",
                "list":     "GET  /api/v1/webhooks",
                "test":     "POST /api/v1/webhooks/{id}/test",
                "delete":   "DELETE /api/v1/webhooks/{id}",
            },
            "v2_products": {
                "list": "GET /api/v2/products  (with enhanced filtering & HATEOAS links)",
            }
        },
        "auth_note": "Protected endpoints require: Authorization: Bearer <token>",
        "rate_limit": "100 requests per minute per IP",
        "pagination": "Use ?page=N&per_page=N (default: page=1, per_page=10)",
    }


if __name__ == '__main__':
    print("\n" + "="*50)
    print("  REST API Mastery Server Starting...")
    print("  Docs:   http://localhost:5000/docs")
    print("  Health: http://localhost:5000/health")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
