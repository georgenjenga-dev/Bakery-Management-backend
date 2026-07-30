from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies
)

from ..extensions import db
from ..models.models import Admin
from ..utils.helpers import (
    admin_required,
    super_admin_required
)
from ..services.admin_services import (
    get_all_admins,
    create_admin,
    deactivate_admin,
    activate_admin,
    reset_password
)

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


@admin_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required."
        }), 400

    admin = Admin.query.filter_by(email=email).first()

    if not admin or not admin.check_password(password):
        return jsonify({
            "error": "Invalid credentials."
        }), 401

    if not admin.is_active:
        return jsonify({
            "error": "This admin account has been deactivated."
        }), 403

    admin.last_login = datetime.utcnow()
    db.session.commit()

    access_token = create_access_token(
        identity=str(admin.id)
    )

    refresh_token = create_refresh_token(
        identity=str(admin.id)
    )

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "admin": admin.to_dict()
    }), 200


@admin_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({
        "message": "Successfully logged out."
    })

    unset_jwt_cookies(response)

    return response, 200


@admin_bp.route("/profile", methods=["GET"])
@admin_required()
def profile():
    admin_id = int(get_jwt_identity())

    admin = db.session.get(Admin, admin_id)

    if not admin:
        return jsonify({
            "error": "Admin not found."
        }), 404

    return jsonify(admin.to_dict()), 200


@admin_bp.route("/test", methods=["GET"])
@admin_required()
def test_admin():
    return jsonify({
        "message": "Admin access granted."
    }), 200


@admin_bp.route("/admins", methods=["GET"])
@admin_required()
def list_admins():
    admins = get_all_admins()
    return jsonify(admins), 200


@admin_bp.route("/admins", methods=["POST"])
@super_admin_required()
def add_admin():
    data = request.get_json()

    result = create_admin(data)

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result), 201


@admin_bp.route("/admins/<int:admin_id>/deactivate", methods=["PATCH"])
@super_admin_required()
def disable_admin(admin_id):
    result = deactivate_admin(admin_id)

    if not result["success"]:
        return jsonify(result), 404

    return jsonify(result), 200


@admin_bp.route("/admins/<int:admin_id>/activate", methods=["PATCH"])
@super_admin_required()
def enable_admin(admin_id):
    result = activate_admin(admin_id)

    if not result["success"]:
        return jsonify(result), 404

    return jsonify(result), 200


@admin_bp.route("/admins/<int:admin_id>/reset-password", methods=["PATCH"])
@super_admin_required()
def change_admin_password(admin_id):
    data = request.get_json()

    password = data.get("password")

    if not password:
        return jsonify({
            "success": False,
            "message": "Password is required."
        }), 400

    result = reset_password(
        admin_id,
        password
    )

    if not result["success"]:
        return jsonify(result), 404

    return jsonify(result), 200