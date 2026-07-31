from datetime import datetime

from flask import Blueprint, request, jsonify
import logging
from flask import Blueprint, jsonify, request
from app.extensions import db
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
    """
    POST /api/admin/login
    Authenticate an admin and receive JWT tokens
    ---
    tags:
      - Admin Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: "admin@bakery.com"
            password:
              type: string
              example: "securepassword123"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
            admin:
              type: object
      400:
        description: Email and password are required
      401:
        description: Invalid credentials
      403:
        description: Admin account is deactivated
    """
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
    """
    POST /api/admin/logout
    Invalidate the current JWT token
    ---
    tags:
      - Admin Auth
    security:
      - admin: []
    responses:
      200:
        description: Logout successful
    """
    response = jsonify({
        "message": "Successfully logged out."
    })

    unset_jwt_cookies(response)

    return response, 200


@admin_bp.route("/profile", methods=["GET"])
@admin_required()
def profile():
    """
    GET /api/admin/profile
    Get the current admin's profile
    ---
    tags:
      - Admin Auth
    security:
      - admin: []
    responses:
      200:
        description: Admin profile details
      401:
        description: Admin authentication required
      404:
        description: Admin not found
    """
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
    """
    GET /api/admin/test
    Test admin access
    ---
    tags:
      - Admin Auth
    security:
      - admin: []
    responses:
      200:
        description: Admin access granted
    """
    return jsonify({
        "message": "Admin access granted."
    }), 200


@admin_bp.route("/admins", methods=["GET"])
@admin_required()
def list_admins():
    """
    GET /api/admin/admins
    List all admins
    ---
    tags:
      - Admin Management
    security:
      - admin: []
    responses:
      200:
        description: List of all admins
    """
    admins = get_all_admins()
    return jsonify(admins), 200


@admin_bp.route("/admins", methods=["POST"])
@super_admin_required()
def add_admin():
    """
    POST /api/admin/admins
    Create a new admin (Super admin only)
    ---
    tags:
      - Admin Management
    security:
      - super_admin: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: "newadmin"
            email:
              type: string
              example: "newadmin@bakery.com"
            password:
              type: string
              example: "securepassword123"
            role:
              type: string
              enum: [admin, super_admin]
              example: "admin"
    responses:
      201:
        description: Admin created successfully
      400:
        description: Creation failed
      401:
        description: Admin authentication required
      403:
        description: Super admin required
    """
    data = request.get_json()

    result = create_admin(data)

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result), 201


@admin_bp.route("/admins/<int:admin_id>/deactivate", methods=["PATCH"])
@super_admin_required()
def disable_admin(admin_id):
    """
    PATCH /api/admin/admins/<admin_id>/deactivate
    Deactivate an admin (Super admin only)
    ---
    tags:
      - Admin Management
    security:
      - super_admin: []
    parameters:
      - in: path
        name: admin_id
        required: true
        type: integer
        description: The admin ID
    responses:
      200:
        description: Admin deactivated successfully
      401:
        description: Admin authentication required
      403:
        description: Super admin required
      404:
        description: Admin not found
    """
    result = deactivate_admin(admin_id)

    if not result["success"]:
        return jsonify(result), 404

    return jsonify(result), 200


@admin_bp.route("/admins/<int:admin_id>/activate", methods=["PATCH"])
@super_admin_required()
def enable_admin(admin_id):
    """
    PATCH /api/admin/admins/<admin_id>/activate
    Activate an admin (Super admin only)
    ---
    tags:
      - Admin Management
    security:
      - super_admin: []
    parameters:
      - in: path
        name: admin_id
        required: true
        type: integer
        description: The admin ID
    responses:
      200:
        description: Admin activated successfully
      401:
        description: Admin authentication required
      403:
        description: Super admin required
      404:
        description: Admin not found
    """
    result = activate_admin(admin_id)

    if not result["success"]:
        return jsonify(result), 404

    return jsonify(result), 200


@admin_bp.route("/admins/<int:admin_id>/reset-password", methods=["PATCH"])
@super_admin_required()
def change_admin_password(admin_id):
    """
    PATCH /api/admin/admins/<admin_id>/reset-password
    Reset an admin's password (Super admin only)
    ---
    tags:
      - Admin Management
    security:
      - super_admin: []
    parameters:
      - in: path
        name: admin_id
        required: true
        type: integer
        description: The admin ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - password
          properties:
            password:
              type: string
              example: "newsecurepassword123"
    responses:
      200:
        description: Password reset successfully
      400:
        description: Password is required
      401:
        description: Admin authentication required
      403:
        description: Super admin required
      404:
        description: Admin not found
    """
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


import logging
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.order import Order, OrderItem

admin_orders_bp = Blueprint('admin_orders', __name__, url_prefix='/api/admin/orders')
logger = logging.getLogger(__name__)


@admin_orders_bp.route('/', methods=['GET'])
def get_all_orders():
    """
    GET /api/admin/orders
    Get all orders with optional filtering
    ---
    tags:
      - Admin Orders
    parameters:
      - in: query
        name: status
        required: false
        type: string
        enum: [Pending, Paid, Cancelled]
        description: Filter by payment status
      - in: query
        name: page
        required: false
        type: integer
        default: 1
        description: Page number
      - in: query
        name: per_page
        required: false
        type: integer
        default: 20
        description: Items per page
    responses:
      200:
        description: Paginated list of orders
      500:
        description: Failed to fetch orders
    """
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
    """
    GET /api/admin/orders/<order_id>
    Get single order details
    ---
    tags:
      - Admin Orders
    parameters:
      - in: path
        name: order_id
        required: true
        type: integer
        description: The order ID
    responses:
      200:
        description: Order details
      404:
        description: Order not found
      500:
        description: Failed to fetch order
    """
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
    """
    PUT /api/admin/orders/<order_id>/status
    Update order payment status
    ---
    tags:
      - Admin Orders
    parameters:
      - in: path
        name: order_id
        required: true
        type: integer
        description: The order ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [Pending, Paid, Cancelled]
              example: "Paid"
    responses:
      200:
        description: Status updated successfully
      400:
        description: Invalid status value
      500:
        description: Failed to update status
    """
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
    """
    GET /api/admin/orders/stats
    Get order statistics for dashboard
    ---
    tags:
      - Admin Orders
    responses:
      200:
        description: Order statistics
      500:
        description: Failed to fetch statistics
    """
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
