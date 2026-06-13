"""routes/v2/products.py — API v2: demonstrates versioning + HATEOAS links"""
from flask import Blueprint, request
from database import get_db
from utils.responses import success, error
from utils.validators import get_pagination_params

products_v2_bp = Blueprint('products_v2', __name__)


@products_v2_bp.route('', methods=['GET'])
def list_products_v2():
    """
    v2 adds: HATEOAS _links, computed fields, richer filtering
    """
    db = get_db()
    page, per_page = get_pagination_params(request)
    rows = db.execute(
        "SELECT * FROM products WHERE active=1 LIMIT ? OFFSET ?",
        (per_page, (page-1)*per_page)
    ).fetchall()

    products = []
    for row in rows:
        p = dict(row)
        # v2 enhancements
        p['in_stock']     = p['stock'] > 0
        p['price_formatted'] = f"${p['price']:.2f}"
        p['_links'] = {
            'self':     {'href': f"/api/v2/products/{p['id']}", 'method': 'GET'},
            'update':   {'href': f"/api/v2/products/{p['id']}", 'method': 'PUT'},
            'delete':   {'href': f"/api/v2/products/{p['id']}", 'method': 'DELETE'},
            'category': {'href': f"/api/v2/products?category={p['category']}", 'method': 'GET'},
        }
        products.append(p)

    total = db.execute("SELECT COUNT(*) FROM products WHERE active=1").fetchone()[0]
    return success(products, meta={
        'version': 'v2',
        'pagination': {'page': page, 'per_page': per_page, 'total': total},
        '_links': {
            'self': f"/api/v2/products?page={page}",
            'next': f"/api/v2/products?page={page+1}" if (page*per_page) < total else None,
        }
    })
