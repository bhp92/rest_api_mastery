"""routes/users.py — Users CRUD with search, filtering, pagination"""
from flask import Blueprint, request
from werkzeug.security import generate_password_hash
from database import get_db
from utils.auth import require_auth, require_role
from utils.responses import success, error, paginate
from utils.validators import validate_email, validate_required, get_pagination_params

users_bp = Blueprint('users', __name__)


def _user_dict(row):
    d = dict(row)
    d.pop('password', None)
    return d


@users_bp.route('', methods=['GET'])
@require_auth
def list_users():
    """GET /api/v1/users — List users with search, filter, pagination"""
    db = get_db()
    page, per_page = get_pagination_params(request)
    search = request.args.get('search', '')
    role   = request.args.get('role', '')

    conditions, params = ['active=1'], []
    if search:
        conditions.append("(username LIKE ? OR email LIKE ? OR first_name LIKE ? OR last_name LIKE ?)")
        params.extend([f'%{search}%'] * 4)
    if role:
        conditions.append("role=?")
        params.append(role)

    where = ' AND '.join(conditions)
    total = db.execute(f"SELECT COUNT(*) FROM users WHERE {where}", params).fetchone()[0]
    rows  = db.execute(
        f"SELECT id,username,email,role,first_name,last_name,active,created_at FROM users WHERE {where} LIMIT ? OFFSET ?",
        params + [per_page, (page - 1) * per_page]
    ).fetchall()

    return paginate([_user_dict(r) for r in rows], page, per_page, total, '/api/v1/users')


@users_bp.route('/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    db = get_db()
    row = db.execute(
        "SELECT id,username,email,role,first_name,last_name,active,created_at FROM users WHERE id=? AND active=1",
        (user_id,)
    ).fetchone()
    if not row:
        return error("User not found", 404)
    return success(_user_dict(row))


@users_bp.route('', methods=['POST'])
@require_auth
@require_role('admin')
def create_user():
    data = request.get_json()
    if not data:
        return error("JSON body required")
    missing = validate_required(data, ['username', 'email', 'password'])
    if missing:
        return error(f"Missing fields: {missing}")
    if not validate_email(data['email']):
        return error("Invalid email format")

    db = get_db()
    if db.execute("SELECT id FROM users WHERE username=? OR email=?", (data['username'], data['email'])).fetchone():
        return error("Username or email already exists", 409)

    cursor = db.execute(
        "INSERT INTO users (username,email,password,role,first_name,last_name) VALUES (?,?,?,?,?,?)",
        (data['username'], data['email'], generate_password_hash(data['password']),
         data.get('role','user'), data.get('first_name',''), data.get('last_name',''))
    )
    db.commit()
    return success({'id': cursor.lastrowid, 'username': data['username']}, "User created", 201)


@users_bp.route('/<int:user_id>', methods=['PUT'])
@require_auth
def update_user(user_id):
    """Full update — all fields required"""
    if request.current_user['user_id'] != user_id and request.current_user['role'] != 'admin':
        return error("Forbidden", 403)
    data = request.get_json()
    if not data:
        return error("JSON body required")
    missing = validate_required(data, ['username', 'email', 'first_name', 'last_name'])
    if missing:
        return error(f"Missing fields for full update: {missing}")

    db = get_db()
    db.execute(
        "UPDATE users SET username=?,email=?,first_name=?,last_name=?,updated_at=datetime('now') WHERE id=?",
        (data['username'], data['email'], data['first_name'], data['last_name'], user_id)
    )
    db.commit()
    return success({'id': user_id}, "User updated")


@users_bp.route('/<int:user_id>', methods=['PATCH'])
@require_auth
def patch_user(user_id):
    """Partial update — only send fields you want to change"""
    if request.current_user['user_id'] != user_id and request.current_user['role'] != 'admin':
        return error("Forbidden", 403)
    data = request.get_json()
    if not data:
        return error("JSON body required")

    allowed = {'username', 'email', 'first_name', 'last_name'}
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return error(f"No valid fields to update. Allowed: {allowed}")

    set_clause = ', '.join(f"{k}=?" for k in updates)
    db = get_db()
    db.execute(
        f"UPDATE users SET {set_clause}, updated_at=datetime('now') WHERE id=?",
        list(updates.values()) + [user_id]
    )
    db.commit()
    return success({'id': user_id, 'updated_fields': list(updates.keys())}, "User patched")


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@require_auth
@require_role('admin')
def delete_user(user_id):
    """Soft delete"""
    db = get_db()
    db.execute("UPDATE users SET active=0, updated_at=datetime('now') WHERE id=?", (user_id,))
    db.commit()
    return success(message="User deleted"), 200
