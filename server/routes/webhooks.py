"""routes/webhooks.py — Webhook registration and testing"""
from flask import Blueprint, request
from database import get_db
from utils.auth import require_auth
from utils.responses import success, error
import requests as req
import json, hmac, hashlib, uuid

webhooks_bp = Blueprint('webhooks', __name__)
VALID_EVENTS = ['order.created', 'order.status_changed', 'user.registered', 'product.created']


@webhooks_bp.route('', methods=['GET'])
@require_auth
def list_webhooks():
    db = get_db()
    rows = db.execute("SELECT id,url,events,active,created_at FROM webhooks").fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d['events'] = json.loads(d['events'])
        result.append(d)
    return success(result)


@webhooks_bp.route('', methods=['POST'])
@require_auth
def register_webhook():
    data = request.get_json()
    if not data or 'url' not in data or 'events' not in data:
        return error("url and events required")
    for event in data['events']:
        if event not in VALID_EVENTS:
            return error(f"Invalid event '{event}'. Valid: {VALID_EVENTS}")
    secret = data.get('secret') or uuid.uuid4().hex
    db = get_db()
    cursor = db.execute(
        "INSERT INTO webhooks (url, events, secret) VALUES (?,?,?)",
        (data['url'], json.dumps(data['events']), secret)
    )
    db.commit()
    return success({'id': cursor.lastrowid, 'secret': secret, 'hint': 'Store the secret — it signs webhook payloads'}, "Webhook registered", 201)


@webhooks_bp.route('/<int:webhook_id>/test', methods=['POST'])
@require_auth
def test_webhook(webhook_id):
    """Send a test payload to the registered webhook URL"""
    db = get_db()
    webhook = db.execute("SELECT * FROM webhooks WHERE id=?", (webhook_id,)).fetchone()
    if not webhook:
        return error("Webhook not found", 404)

    payload = {
        'event': 'webhook.test',
        'webhook_id': webhook_id,
        'data': {'message': 'This is a test event from REST API Mastery'}
    }
    body = json.dumps(payload)
    sig = hmac.new(webhook['secret'].encode(), body.encode(), hashlib.sha256).hexdigest()

    try:
        resp = req.post(
            webhook['url'],
            data=body,
            headers={'Content-Type': 'application/json', 'X-Webhook-Signature': sig},
            timeout=5
        )
        return success({'status_code': resp.status_code, 'response': resp.text[:500]}, "Test delivered")
    except Exception as e:
        return error(f"Delivery failed: {str(e)}", 502)


@webhooks_bp.route('/<int:webhook_id>', methods=['DELETE'])
@require_auth
def delete_webhook(webhook_id):
    db = get_db()
    db.execute("DELETE FROM webhooks WHERE id=?", (webhook_id,))
    db.commit()
    return success(message="Webhook deleted")
