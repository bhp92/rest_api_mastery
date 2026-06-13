"""routes/orders.py — Orders with items, status transitions"""
from flask import Blueprint, request
from database import get_db
from utils.auth import require_auth, require_role
from utils.responses import success, error, paginate
from utils.validators import validate_required, get_pagination_params

orders_bp = Blueprint('orders', __name__)

VALID_STATUSES = ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')
STATUS_TRANSITIONS = {
    'pending':    ['confirmed', 'cancelled'],
    'confirmed':  ['processing', 'cancelled'],
    'processing': ['shipped', 'cancelled'],
    'shipped':    ['delivered'],
    'delivered':  [],
    'cancelled':  [],
}


@orders_bp.route('', methods=['GET'])
@require_auth
def list_orders():
    db = get_db()
    page, per_page = get_pagination_params(request)
    user_id = request.current_user['user_id']
    role    = request.current_user['role']
    status  = request.args.get('status', '')

    conditions = [] if role == 'admin' else ['o.user_id=?']
    params     = [] if role == 'admin' else [user_id]
    if status:
        conditions.append("o.status=?"); params.append(status)

    where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''
    total = db.execute(f"SELECT COUNT(*) FROM orders o {where}", params).fetchone()[0]
    rows  = db.execute(
        f"SELECT o.*, u.username FROM orders o LEFT JOIN users u ON o.user_id=u.id {where} ORDER BY o.created_at DESC LIMIT ? OFFSET ?",
        params + [per_page, (page-1)*per_page]
    ).fetchall()
    return paginate([dict(r) for r in rows], page, per_page, total, '/api/v1/orders')


@orders_bp.route('/<int:order_id>', methods=['GET'])
@require_auth
def get_order(order_id):
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not order:
        return error("Order not found", 404)
    if order['user_id'] != request.current_user['user_id'] and request.current_user['role'] != 'admin':
        return error("Forbidden", 403)

    items = db.execute(
        "SELECT oi.*, p.name as product_name FROM order_items oi JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?",
        (order_id,)
    ).fetchall()
    result = dict(order)
    result['items'] = [dict(i) for i in items]
    return success(result)


@orders_bp.route('', methods=['POST'])
@require_auth
def create_order():
    """
    POST /api/v1/orders
    Body: { "items": [{"product_id": 1, "quantity": 2}], "notes": "..." }
    """
    data = request.get_json()
    if not data or 'items' not in data or not data['items']:
        return error("items array required (e.g. [{product_id: 1, quantity: 2}])")

    db = get_db()
    total = 0
    validated_items = []
    for item in data['items']:
        if 'product_id' not in item or 'quantity' not in item:
            return error("Each item needs product_id and quantity")
        product = db.execute("SELECT * FROM products WHERE id=? AND active=1", (item['product_id'],)).fetchone()
        if not product:
            return error(f"Product {item['product_id']} not found", 404)
        qty = int(item['quantity'])
        if qty < 1:
            return error("Quantity must be at least 1")
        if product['stock'] < qty:
            return error(f"Insufficient stock for '{product['name']}'. Available: {product['stock']}")
        item_total = product['price'] * qty
        total += item_total
        validated_items.append({'product': product, 'quantity': qty, 'price': product['price']})

    # Create order
    cursor = db.execute(
        "INSERT INTO orders (user_id, status, total, notes) VALUES (?,?,?,?)",
        (request.current_user['user_id'], 'pending', total, data.get('notes', ''))
    )
    order_id = cursor.lastrowid

    for item in validated_items:
        db.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?,?,?,?)",
            (order_id, item['product']['id'], item['quantity'], item['price'])
        )
        db.execute("UPDATE products SET stock=stock-? WHERE id=?", (item['quantity'], item['product']['id']))

    db.commit()
    return success({'id': order_id, 'total': total, 'status': 'pending'}, "Order created", 201)


@orders_bp.route('/<int:order_id>/status', methods=['PATCH'])
@require_auth
def update_status(order_id):
    """PATCH /api/v1/orders/{id}/status — Enforces valid status transitions"""
    data = request.get_json()
    if not data or 'status' not in data:
        return error("status field required")

    new_status = data['status']
    if new_status not in VALID_STATUSES:
        return error(f"Invalid status. Valid: {VALID_STATUSES}")

    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not order:
        return error("Order not found", 404)

    current_status = order['status']
    if new_status not in STATUS_TRANSITIONS[current_status]:
        return error(
            f"Invalid transition: {current_status} → {new_status}",
            422,
            hint=f"From '{current_status}', allowed transitions: {STATUS_TRANSITIONS[current_status]}"
        )

    db.execute("UPDATE orders SET status=?, updated_at=datetime('now') WHERE id=?", (new_status, order_id))
    db.commit()
    return success({'id': order_id, 'status': new_status}, f"Order status → {new_status}")


@orders_bp.route('/<int:order_id>', methods=['DELETE'])
@require_auth
def cancel_order(order_id):
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not order:
        return error("Order not found", 404)
    if order['user_id'] != request.current_user['user_id'] and request.current_user['role'] != 'admin':
        return error("Forbidden", 403)
    if order['status'] not in STATUS_TRANSITIONS or 'cancelled' not in STATUS_TRANSITIONS[order['status']]:
        return error(f"Cannot cancel order in '{order['status']}' status", 422)

    db.execute("UPDATE orders SET status='cancelled', updated_at=datetime('now') WHERE id=?", (order_id,))
    db.commit()
    return success(message="Order cancelled")
