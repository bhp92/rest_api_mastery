"""utils/auth.py — JWT helpers and decorators"""
import jwt
import functools
from datetime import datetime, timedelta
from flask import request, jsonify, current_app


def generate_tokens(user_id: int, role: str) -> dict:
    access_payload = {
        'user_id': user_id,
        'role': role,
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=30),
        'iat': datetime.utcnow(),
    }
    refresh_payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow(),
    }
    access_token  = jwt.encode(access_payload,  current_app.config['SECRET_KEY'], algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return {'access_token': access_token, 'refresh_token': refresh_token}


def decode_token(token: str) -> dict:
    return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])


def require_auth(f):
    """Decorator: requires valid JWT access token"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header', 'hint': 'Use: Authorization: Bearer <token>'}), 401
        token = auth_header.split(' ')[1]
        try:
            payload = decode_token(token)
            if payload.get('type') != 'access':
                return jsonify({'error': 'Invalid token type'}), 401
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired', 'hint': 'Use /api/v1/auth/refresh to get a new token'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': f'Invalid token: {str(e)}'}), 401
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    """Decorator: requires specific role(s). Must be used AFTER @require_auth"""
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            user_role = getattr(request, 'current_user', {}).get('role', '')
            if user_role not in roles:
                return jsonify({'error': f'Forbidden. Required role: {roles}', 'your_role': user_role}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
