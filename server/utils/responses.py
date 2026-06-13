"""utils/responses.py — Consistent API response helpers"""
from flask import jsonify
from math import ceil


def success(data=None, message=None, status=200, meta=None):
    body = {'success': True}
    if message:
        body['message'] = message
    if data is not None:
        body['data'] = data
    if meta:
        body['meta'] = meta
    return jsonify(body), status


def error(message, status=400, errors=None, hint=None):
    body = {'success': False, 'error': message}
    if errors:
        body['errors'] = errors
    if hint:
        body['hint'] = hint
    return jsonify(body), status


def paginate(query_results, page, per_page, total_count, base_url):
    """Build a paginated response with HATEOAS-style links"""
    total_pages = ceil(total_count / per_page) if per_page else 1
    return success(
        data=query_results,
        meta={
            'pagination': {
                'page':        page,
                'per_page':    per_page,
                'total':       total_count,
                'total_pages': total_pages,
            },
            'links': {
                'self':  f"{base_url}?page={page}&per_page={per_page}",
                'first': f"{base_url}?page=1&per_page={per_page}",
                'last':  f"{base_url}?page={total_pages}&per_page={per_page}",
                'next':  f"{base_url}?page={page+1}&per_page={per_page}" if page < total_pages else None,
                'prev':  f"{base_url}?page={page-1}&per_page={per_page}" if page > 1 else None,
            }
        }
    )
