from functools import wraps

from flask import jsonify

from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity,
)

from ..models.models import Admin
from ..extensions import db


def admin_required():
    """
    Protect admin routes using JWT.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()

            admin_id = int(get_jwt_identity())

            admin = db.session.get(Admin, admin_id)

            if not admin:
                return jsonify({
                    "success": False,
                    "message": "Admin not found"
                }), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper


def success_response(
    data=None,
    message="Success",
    status_code=200,
):
    """
    Standard success response.
    """

    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), status_code


def error_response(
    message,
    status_code=400,
):
    """
    Standard error response.
    """

    return jsonify({
        "success": False,
        "message": message
    }), status_code