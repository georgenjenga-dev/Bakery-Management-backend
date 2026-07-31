from decimal import Decimal

from app.extensions import db
from app.models.models import Order, OrderItem, Product


def get_all_orders():
    """
    Returns all customer orders.
    """
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return [order.to_dict() for order in orders]


def get_order(order_id):
    """
    Returns one order or None.
    """
    return db.session.get(Order, order_id)


def create_order(data):
    """
    Creates a customer order.

    Expected payload:

    {
        "customer_name": "...",
        "phone_number": "...",
        "delivery_address": "...",
        "items":[
            {
                "product_id":1,
                "quantity":2
            }
        ]
    }
    """

    items = data.get("items", [])

    if not items:
        raise ValueError("Order must contain at least one item")

    total_price = Decimal("0.00")

    order = Order(
        customer_name=data["customer_name"],
        phone_number=data["phone_number"],
        delivery_address=data["delivery_address"],
        status="Pending"
    )

    db.session.add(order)

    for item in items:

        product = db.session.get(Product, item["product_id"])

        if not product:
            raise ValueError(
                f"Product {item['product_id']} does not exist"
            )

        quantity = int(item["quantity"])

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        if product.stock < quantity:
            raise ValueError(
                f"Not enough stock for {product.name}"
            )

        product.stock -= quantity

        subtotal = product.price * quantity

        total_price += subtotal

        order_item = OrderItem(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.price
        )

        db.session.add(order_item)

    order.total_price = total_price

    db.session.commit()

    return order

def update_order_status(order, status):
    """
    Updates an order status.
    """

    order.status = status

    db.session.commit()

    return order


def delete_order(order):
    """
    Deletes an order.
    """

    db.session.delete(order)
    db.session.commit()


def get_orders_by_status(status):
    """
    Returns all orders with the given status.
    """

    orders = Order.query.filter_by(
        status=status
    ).all()

    return [order.to_dict() for order in orders]
