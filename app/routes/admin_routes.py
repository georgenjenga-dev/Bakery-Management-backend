from datetime import datetime

from flask import Blueprint, request, jsonify
import logging
from flask import Blueprint, jsonify, request
from app import db
from app.models.order import Order, OrderItem
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
    return jsonify({'message': 'Admin access granted'}), 200




import logging
from flask import Blueprint, jsonify, request
from app import db
from app.models.order import Order, OrderItem

admin_orders_bp = Blueprint('admin_orders', __name__, url_prefix='/api/admin/orders')
logger = logging.getLogger(__name__)


@admin_orders_bp.route('/', methods=['GET'])
def get_all_orders():
    """Get all orders with optional filtering."""
    try:
        status_filter = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Order.query.order_by(Order.created_at.desc())
        
        if status_filter:
            query = query.filter_by(payment_status=status_filter)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        orders = pagination.items
        
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in orders],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to fetch orders'}), 500


@admin_orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get single order details."""
    try:
        order = Order.query.get_or_404(order_id)
        return jsonify({
            'success': True,
            'order': order.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Order not found'}), 404


@admin_orders_bp.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order payment status (admin only)."""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['Pending', 'Paid', 'Cancelled']:
            return jsonify({
                'success': False,
                'message': 'Invalid status. Use: Pending, Paid, or Cancelled'
            }), 400
        
        order = Order.query.get_or_404(order_id)
        order.payment_status = new_status
        db.session.commit()
        
        logger.info(f"Order #{order_id} status updated to {new_status}")
        
        return jsonify({
            'success': True,
            'message': 'Status updated successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating order {order_id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to update status'}), 500


@admin_orders_bp.route('/stats', methods=['GET'])
def get_order_stats():
    """Get order statistics for dashboard."""
    try:
        total_orders = Order.query.count()
        paid_orders = Order.query.filter_by(payment_status='Paid').count()
        pending_orders = Order.query.filter_by(payment_status='Pending').count()
        cancelled_orders = Order.query.filter_by(payment_status='Cancelled').count()
        
        total_revenue = db.session.query(db.func.sum(Order.total_amount))\
            .filter_by(payment_status='Paid').scalar() or 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_orders': total_orders,
                'paid_orders': paid_orders,
                'pending_orders': pending_orders,
                'cancelled_orders': cancelled_orders,
                'total_revenue': float(total_revenue)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to fetch statistics'}), 500
