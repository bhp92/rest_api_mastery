"""utils/validators.py — Input validation helpers"""
import re


def validate_email(email: str) -> bool:
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))


def validate_required(data: dict, fields: list) -> list:
    """Returns list of missing required fields"""
    return [f for f in fields if f not in data or data[f] is None or data[f] == '']


def validate_positive_number(value, field_name='value') -> tuple:
    try:
        num = float(value)
        if num < 0:
            return None, f"{field_name} must be non-negative"
        return num, None
    except (TypeError, ValueError):
        return None, f"{field_name} must be a valid number"


def get_pagination_params(request) -> tuple:
    """Extract and validate pagination params from request"""
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        page = 1
    try:
        per_page = min(100, max(1, int(request.args.get('per_page', 10))))
    except ValueError:
        per_page = 10
    return page, per_page
