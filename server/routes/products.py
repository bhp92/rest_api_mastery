"""routes/products.py — Products with filtering, search, pagination"""
from flask import Blueprint, request
from database import get_db
from utils.auth import require_auth, require_role
from utils.responses import success, error, paginate
from utils.validators import validate_required, get_pagination_params
import uuid

products_bp = Blueprint('products', __name__)


def _product_dict(row):
    return dict(row)


@products_bp.route('', methods=['GET'])
def list_products():
    """
    GET /api/v1/products
    Query params: page, per_page, category, min_price, max_price, search, sort_by, order
    """
    db = get_db()
    page, per_page = get_pagination_params(request)

    category  = request.args.get('category', '')
    search    = request.args.get('search', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by   = request.args.get('sort_by', 'id')
    order     = request.args.get('order', 'asc').upper()

    if sort_by not in ('id', 'name', 'price', 'created_at'):
        sort_by = 'id'
    if order not in ('ASC', 'DESC'):
        order = 'ASC'

    conditions, params = ['active=1'], []
    if category:
        conditions.append("category=?"); params.append(category)
    if search:
        conditions.append("(name LIKE ? OR description LIKE ?)"); params.extend([f'%{search}%']*2)
    if min_price is not None:
        conditions.append("price>=?"); params.append(min_price)
    if max_price is not None:
        conditions.append("price<=?"); params.append(max_price)

    where = ' AND '.join(conditions)
    total = db.execute(f"SELECT COUNT(*) FROM products WHERE {where}", params).fetchone()[0]
    rows  = db.execute(
        f"SELECT * FROM products WHERE {where} ORDER BY {sort_by} {order} LIMIT ? OFFSET ?",
        params + [per_page, (page-1)*per_page]
    ).fetchall()

    return paginate([_product_dict(r) for r in rows], page, per_page, total, '/api/v1/products')


@products_bp.route('/categories', methods=['GET'])
def list_categories():
    db = get_db()
    rows = db.execute("SELECT DISTINCT category FROM products WHERE active=1 AND category IS NOT NULL").fetchall()
    return success([r['category'] for r in rows])


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    db = get_db()
    row = db.execute("SELECT * FROM products WHERE id=? AND active=1", (product_id,)).fetchone()
    if not row:
        return error("Product not found", 404)
    return success(_product_dict(row))


@products_bp.route('', methods=['POST'])
@require_auth
@require_role('admin')
def create_product():
    data = request.get_json()
    if not data:
        return error("JSON body required")
    missing = validate_required(data, ['name', 'price'])
    if missing:
        return error(f"Missing fields: {missing}")

    try:
        price = float(data['price'])
        if price < 0:
            return error("Price must be non-negative")
    except (ValueError, TypeError):
        return error("Price must be a number")

    sku = data.get('sku') or f"SKU-{uuid.uuid4().hex[:8].upper()}"
    db = get_db()
    cursor = db.execute(
        "INSERT INTO products (name,description,price,category,stock,sku) VALUES (?,?,?,?,?,?)",
        (data['name'], data.get('description',''), price,
         data.get('category',''), int(data.get('stock',0)), sku)
    )
    db.commit()
    return success({'id': cursor.lastrowid, 'sku': sku}, "Product created", 201)


@products_bp.route('/<int:product_id>', methods=['PUT'])
@require_auth
@require_role('admin')
def update_product(product_id):
    data = request.get_json()
    if not data:
        return error("JSON body required")
    missing = validate_required(data, ['name', 'price', 'category', 'stock'])
    if missing:
        return error(f"Missing fields for full update: {missing}")

    db = get_db()
    db.execute(
        "UPDATE products SET name=?,description=?,price=?,category=?,stock=?,updated_at=datetime('now') WHERE id=?",
        (data['name'], data.get('description',''), float(data['price']),
         data['category'], int(data['stock']), product_id)
    )
    db.commit()
    return success({'id': product_id}, "Product updated")


@products_bp.route('/<int:product_id>', methods=['PATCH'])
@require_auth
@require_role('admin')
def patch_product(product_id):
    data = request.get_json()
    if not data:
        return error("JSON body required")
    allowed = {'name', 'description', 'price', 'category', 'stock'}
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return error(f"No valid fields. Allowed: {allowed}")

    set_clause = ', '.join(f"{k}=?" for k in updates)
    db = get_db()
    db.execute(
        f"UPDATE products SET {set_clause}, updated_at=datetime('now') WHERE id=?",
        list(updates.values()) + [product_id]
    )
    db.commit()
    return success({'id': product_id}, "Product patched")


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@require_auth
@require_role('admin')
def delete_product(product_id):
    db = get_db()
    db.execute("UPDATE products SET active=0 WHERE id=?", (product_id,))
    db.commit()
    return success(message="Product deleted")
