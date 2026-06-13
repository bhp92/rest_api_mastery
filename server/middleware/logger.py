"""middleware/logger.py — Request/response logger"""
import logging
import time
from flask import request, g


def setup_logger(app):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    logger = logging.getLogger('api')

    @app.before_request
    def before():
        g.start_time = time.time()

    @app.after_request
    def after(response):
        duration = round((time.time() - g.get('start_time', time.time())) * 1000, 2)
        logger.info(
            f"{request.method:6} {request.path:40} → {response.status_code}  ({duration}ms)"
        )
        response.headers['X-Response-Time'] = f"{duration}ms"
        response.headers['X-API-Version'] = '1.0.0'
        return response
