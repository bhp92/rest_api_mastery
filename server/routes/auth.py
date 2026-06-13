"""routes/auth.py — Authentication endpoints"""
from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from utils.auth import generate_tokens, decode_token, require_auth
from utils.responses import success, error
from utils.validators import validate_email, validate_required
import jwt

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """POST /api/v1/auth/register — Create a new account"""
    data = request.get_json()
    if not data:
        return error("Request body must be JSON")

    missing = validate_required(data, ['username', 'email', 'password'])
    if missing:
        return error(f"Missing required fields: {missing}")

    if not validate_email(data['email']):
        return error("Invalid email format")

    if len(data['password']) < 6:
        return error("Password must be at least 6 characters")

    db = get_db()
    existing = db.execute(
        "SELECT id FROM users WHERE username=? OR email=?",
        (data['username'], data['email'])
    ).fetchone()
    if existing:
        return error("Username or email already exists", 409)

    hashed_pw = generate_password_hash(data['password'])
    cursor = db.execute(
        "INSERT INTO users (username, email, password, first_name, last_name, role) VALUES (?,?,?,?,?,?)",
        (data['username'], data['email'], hashed_pw,
         data.get('first_name', ''), data.get('last_name', ''), 'user')
    )
    db.commit()
    user_id = cursor.lastrowid

    tokens = generate_tokens(user_id, 'user')
    return success({'user_id': user_id, 'username': data['username'], **tokens}, "Account created", 201)


@auth_bp.route('/login', methods=['POST'])
def login():
    """POST /api/v1/auth/login — Get access + refresh tokens"""
    data = request.get_json()
    if not data:
        return error("Request body must be JSON")

    missing = validate_required(data, ['username', 'password'])
    if missing:
        return error(f"Missing required fields: {missing}")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=? AND active=1", (data['username'],)
    ).fetchone()

    if not user or not check_password_hash(user['password'], data['password']):
        return error("Invalid username or password", 401)

    tokens = generate_tokens(user['id'], user['role'])

    # Store refresh token
    import jwt as pyjwt
    payload = pyjwt.decode(tokens['refresh_token'], options={"verify_signature": False})
    from datetime import datetime
    expires = datetime.utcfromtimestamp(payload['exp']).isoformat()
    db.execute(
        "INSERT OR REPLACE INTO refresh_tokens (user_id, token, expires_at) VALUES (?,?,?)",
        (user['id'], tokens['refresh_token'], expires)
    )
    db.commit()

    return success({
        'user': {'id': user['id'], 'username': user['username'], 'role': user['role']},
        **tokens
    }, "Login successful")


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """POST /api/v1/auth/refresh — Get new access token using refresh token"""
    data = request.get_json()
    if not data or 'refresh_token' not in data:
        return error("refresh_token required")

    try:
        from flask import current_app
        payload = decode_token(data['refresh_token'])
        if payload.get('type') != 'refresh':
            return error("Invalid token type", 401)
    except Exception as e:
        return error(f"Invalid refresh token: {str(e)}", 401)

    db = get_db()
    stored = db.execute(
        "SELECT * FROM refresh_tokens WHERE token=? AND user_id=?",
        (data['refresh_token'], payload['user_id'])
    ).fetchone()
    if not stored:
        return error("Refresh token not recognized or already used", 401)

    user = db.execute("SELECT * FROM users WHERE id=?", (payload['user_id'],)).fetchone()
    tokens = generate_tokens(user['id'], user['role'])
    return success(tokens, "Token refreshed")


@auth_bp.route('/me', methods=['GET'])
@require_auth
def me():
    """GET /api/v1/auth/me — Get current user profile"""
    db = get_db()
    user = db.execute(
        "SELECT id, username, email, role, first_name, last_name, created_at FROM users WHERE id=?",
        (request.current_user['user_id'],)
    ).fetchone()
    if not user:
        return error("User not found", 404)
    return success(dict(user))


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """POST /api/v1/auth/logout — Invalidate refresh token"""
    data = request.get_json() or {}
    if 'refresh_token' in data:
        db = get_db()
        db.execute("DELETE FROM refresh_tokens WHERE token=?", (data['refresh_token'],))
        db.commit()
    return success(message="Logged out successfully")
