from flask import Blueprint, request

from app.services.order_service import (
    create_order,
    get_all_orders,
    get_order,
    update_order_status,
    delete_order,
    get_orders_by_status,
)

from app.utils.validators import (
    validate_order,
    validate_order_status,
)

from app.utils.helpers import (
    success_response,
    error_response,
    admin_required,
)

order_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/orders",
)


@order_bp.get("/")
@admin_required()
def orders():
    """
    GET /orders
    Returns all orders (Admin only)
    """

    return success_response(get_all_orders())


@order_bp.get("/<int:order_id>")
@admin_required()
def single_order(order_id):

    order = get_order(order_id)

    if not order:
        return error_response(
            "Order not found",
            404,
        )

    return success_response(order.to_dict())


@order_bp.get("/status/<string:status>")
@admin_required()
def orders_by_status(status):

    valid, error = validate_order_status(status)

    if not valid:
        return error_response(error)

    return success_response(
        get_orders_by_status(status)
    )


@order_bp.post("/")
def checkout():
    """
    Customer checkout
    """

    data = request.get_json(silent=True)

    if data is None:
        return error_response(
            "Invalid JSON body"
        )

    valid, error = validate_order(data)

    if not valid:
        return error_response(error)

    try:

        order = create_order(data)

        return success_response(
            order.to_dict(),
            "Order placed successfully",
            201,
        )

    except ValueError as e:

        return error_response(
            str(e),
            400,
        )

    except Exception:

        return error_response(
            "Failed to create order",
            500,
        )


@order_bp.put("/<int:order_id>")
@admin_required()
def change_status(order_id):

    order = get_order(order_id)

    if not order:
        return error_response(
            "Order not found",
            404,
        )

    data = request.get_json(silent=True)

    if data is None:
        return error_response(
            "Invalid JSON body"
        )

    status = data.get("status")

    valid, error = validate_order_status(status)

    if not valid:
        return error_response(error)

    order = update_order_status(
        order,
        status,
    )

    return success_response(
        order.to_dict(),
        "Order updated successfully",
    )


@order_bp.delete("/<int:order_id>")
@admin_required()
def remove_order(order_id):

    order = get_order(order_id)

    if not order:
        return error_response(
            "Order not found",
            404,
        )

    delete_order(order)

    return success_response(
        message="Order deleted successfully"
    )