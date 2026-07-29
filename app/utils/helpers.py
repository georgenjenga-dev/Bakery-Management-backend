from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..models.models import Admin

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            admin_id = get_jwt_identity()
            admin = Admin.query.get(admin_id)
            if not admin:
                return jsonify({'error': 'Admin not found'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper