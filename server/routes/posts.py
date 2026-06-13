"""routes/posts.py — Blog posts, demonstrates tagging and publishing workflow"""
from flask import Blueprint, request
from database import get_db
from utils.auth import require_auth
from utils.responses import success, error, paginate
from utils.validators import validate_required, get_pagination_params
import json

posts_bp = Blueprint('posts', __name__)


@posts_bp.route('', methods=['GET'])
def list_posts():
    db = get_db()
    page, per_page = get_pagination_params(request)
    tag       = request.args.get('tag', '')
    search    = request.args.get('search', '')
    published = request.args.get('published', '1')

    conditions, params = ['p.published=?'], [1 if published == '1' else 0]
    if tag:
        conditions.append("p.tags LIKE ?"); params.append(f'%{tag}%')
    if search:
        conditions.append("(p.title LIKE ? OR p.content LIKE ?)"); params.extend([f'%{search}%']*2)

    where = ' AND '.join(conditions)
    total = db.execute(f"SELECT COUNT(*) FROM posts p WHERE {where}", params).fetchone()[0]
    rows  = db.execute(
        f"SELECT p.*, u.username as author FROM posts p JOIN users u ON p.user_id=u.id WHERE {where} ORDER BY p.created_at DESC LIMIT ? OFFSET ?",
        params + [per_page, (page-1)*per_page]
    ).fetchall()

    posts = []
    for row in rows:
        p = dict(row)
        p['tags'] = json.loads(p['tags']) if p.get('tags') else []
        posts.append(p)

    return paginate(posts, page, per_page, total, '/api/v1/posts')


@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    db = get_db()
    row = db.execute(
        "SELECT p.*, u.username as author FROM posts p JOIN users u ON p.user_id=u.id WHERE p.id=?",
        (post_id,)
    ).fetchone()
    if not row:
        return error("Post not found", 404)
    p = dict(row)
    p['tags'] = json.loads(p['tags']) if p.get('tags') else []
    return success(p)


@posts_bp.route('', methods=['POST'])
@require_auth
def create_post():
    data = request.get_json()
    if not data:
        return error("JSON body required")
    missing = validate_required(data, ['title', 'content'])
    if missing:
        return error(f"Missing fields: {missing}")

    tags = json.dumps(data.get('tags', []))
    db = get_db()
    cursor = db.execute(
        "INSERT INTO posts (user_id, title, content, tags, published) VALUES (?,?,?,?,?)",
        (request.current_user['user_id'], data['title'], data['content'],
         tags, 1 if data.get('published') else 0)
    )
    db.commit()
    return success({'id': cursor.lastrowid}, "Post created", 201)


@posts_bp.route('/<int:post_id>', methods=['PUT'])
@require_auth
def update_post(post_id):
    db = get_db()
    post = db.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    if not post:
        return error("Post not found", 404)
    if post['user_id'] != request.current_user['user_id'] and request.current_user['role'] != 'admin':
        return error("Forbidden", 403)

    data = request.get_json()
    missing = validate_required(data, ['title', 'content'])
    if missing:
        return error(f"Missing fields: {missing}")

    tags = json.dumps(data.get('tags', []))
    db.execute(
        "UPDATE posts SET title=?,content=?,tags=?,published=?,updated_at=datetime('now') WHERE id=?",
        (data['title'], data['content'], tags, 1 if data.get('published') else 0, post_id)
    )
    db.commit()
    return success({'id': post_id}, "Post updated")


@posts_bp.route('/<int:post_id>', methods=['PATCH'])
@require_auth
def patch_post(post_id):
    db = get_db()
    post = db.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    if not post:
        return error("Post not found", 404)
    if post['user_id'] != request.current_user['user_id'] and request.current_user['role'] != 'admin':
        return error("Forbidden", 403)

    data = request.get_json() or {}
    allowed = {'title', 'content', 'published'}
    updates = {k: v for k, v in data.items() if k in allowed}
    if 'tags' in data:
        updates['tags'] = json.dumps(data['tags'])
    if not updates:
        return error(f"No valid fields. Allowed: {allowed | {'tags'}}")

    set_clause = ', '.join(f"{k}=?" for k in updates)
    db.execute(f"UPDATE posts SET {set_clause}, updated_at=datetime('now') WHERE id=?", list(updates.values()) + [post_id])
    db.commit()
    return success({'id': post_id}, "Post patched")


@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@require_auth
def delete_post(post_id):
    db = get_db()
    post = db.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    if not post:
        return error("Post not found", 404)
    if post['user_id'] != request.current_user['user_id'] and request.current_user['role'] != 'admin':
        return error("Forbidden", 403)
    db.execute("DELETE FROM posts WHERE id=?", (post_id,))
    db.commit()
    return success(message="Post deleted")
