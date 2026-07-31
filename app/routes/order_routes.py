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
    ---
    tags:
      - Orders
    security:
      - admin: []
    responses:
      200:
        description: List of all orders
      401:
        description: Admin authentication required
    """

    return success_response(get_all_orders())


@order_bp.get("/<int:order_id>")
@admin_required()
def single_order(order_id):
    """
    GET /orders/<order_id>
    ---
    tags:
      - Orders
    security:
      - admin: []
    parameters:
      - in: path
        name: order_id
        required: true
        type: integer
        description: The order ID
    responses:
      200:
        description: Order details
      401:
        description: Admin authentication required
      404:
        description: Order not found
    """

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
    """
    GET /orders/status/<status>
    ---
    tags:
      - Orders
    security:
      - admin: []
    parameters:
      - in: path
        name: status
        required: true
        type: string
        enum: [Pending, Preparing, Ready, Completed, Cancelled]
        description: Order status to filter by
    responses:
      200:
        description: Orders with the given status
      400:
        description: Invalid status value
      401:
        description: Admin authentication required
    """

    valid, error = validate_order_status(status)

    if not valid:
        return error_response(error)

    return success_response(
        get_orders_by_status(status)
    )


@order_bp.post("/")
def checkout():
    """
    POST /orders
    Customer checkout to place a new order
    ---
    tags:
      - Orders
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - customer_name
            - customer_phone
            - delivery_address
            - items
          properties:
            customer_name:
              type: string
              example: "Jane Wanjiru"
            customer_phone:
              type: string
              example: "254712345678"
            delivery_address:
              type: string
              example: "Kilimani, Nairobi"
            items:
              type: array
              items:
                type: object
                required:
                  - product_id
                  - quantity
                properties:
                  product_id:
                    type: integer
                    example: 1
                  quantity:
                    type: integer
                    example: 2
    responses:
      201:
        description: Order placed successfully
      400:
        description: Validation error or invalid input
      500:
        description: Failed to create order
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
    """
    PUT /orders/<order_id>
    Update order status (Admin only)
    ---
    tags:
      - Orders
    security:
      - admin: []
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
              enum: [Pending, Preparing, Ready, Completed, Cancelled]
              example: "Ready"
    responses:
      200:
        description: Order status updated successfully
      400:
        description: Invalid status value
      401:
        description: Admin authentication required
      404:
        description: Order not found
    """

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
    """
    DELETE /orders/<order_id>
    ---
    tags:
      - Orders
    security:
      - admin: []
    parameters:
      - in: path
        name: order_id
        required: true
        type: integer
        description: The order ID
    responses:
      200:
        description: Order deleted successfully
      401:
        description: Admin authentication required
      404:
        description: Order not found
    """

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