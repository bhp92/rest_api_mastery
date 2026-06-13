"""routes/health.py"""
from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint('health', __name__)

START_TIME = datetime.utcnow()

@health_bp.route('/health')
def health():
    uptime = (datetime.utcnow() - START_TIME).seconds
    return jsonify({
        'status': 'ok',
        'message': 'REST API Mastery Server is running!',
        'timestamp': datetime.utcnow().isoformat(),
        'uptime_seconds': uptime,
        'version': '1.0.0'
    }), 200
