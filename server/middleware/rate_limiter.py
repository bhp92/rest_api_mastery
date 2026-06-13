"""middleware/rate_limiter.py — Simple in-memory rate limiter"""
from flask import request, jsonify
from collections import defaultdict
from datetime import datetime, timedelta
import threading


class RateLimiter:
    def __init__(self, app, limit=100, window=60):
        self.limit = limit        # requests allowed
        self.window = window      # per this many seconds
        self.requests = defaultdict(list)
        self.lock = threading.Lock()
        app.before_request(self._check)

    def _check(self):
        # Skip rate limiting for docs and health
        if request.path in ['/docs', '/health']:
            return None

        ip = request.remote_addr
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window)

        with self.lock:
            self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]
            if len(self.requests[ip]) >= self.limit:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'limit': self.limit,
                    'window_seconds': self.window,
                    'retry_after': self.window
                }), 429
            self.requests[ip].append(now)
            return None
