import re
from app.models.models import ORDER_STATUS


def validate_required_fields(data, required_fields):
    """
    Checks whether all required fields exist and are not empty.
    """
    for field in required_fields:
        value = data.get(field)

        if value is None:
            return False, f"{field} is required"

        if isinstance(value, str) and value.strip() == "":
            return False, f"{field} cannot be empty"

    return True, None


def validate_price(price):
    """
    Price must be a positive number.
    """
    try:
        price = float(price)

        if price <= 0:
            return False, "Price must be greater than zero"

    except (TypeError, ValueError):
        return False, "Invalid price"

    return True, None


def validate_stock(stock):
    """
    Stock cannot be negative.
    """
    try:
        stock = int(stock)

        if stock < 0:
            return False, "Stock cannot be negative"

    except (TypeError, ValueError):
        return False, "Invalid stock value"

    return True, None


def validate_quantity(quantity):
    """
    Quantity must be at least 1.
    """
    try:
        quantity = int(quantity)

        if quantity <= 0:
            return False, "Quantity must be at least 1"

    except (TypeError, ValueError):
        return False, "Invalid quantity"

    return True, None


def validate_phone(phone):
    """
    Accepts:
    0712345678
    0112345678
    +254712345678
    +254112345678
    """

    pattern = r"^(?:\+254|0)(7|1)\d{8}$"

    if not re.match(pattern, phone):
        return False, "Invalid phone number"

    return True, None


def validate_order_status(status):
    """
    Checks whether the supplied status is valid.
    """
    if status not in ORDER_STATUS:
        return False, f"Status must be one of: {', '.join(ORDER_STATUS)}"

    return True, None


def validate_product(data):
    """
    Full product validation.
    """

    valid, error = validate_required_fields(
        data,
        ["name", "price", "stock"]
    )

    if not valid:
        return valid, error

    valid, error = validate_price(data["price"])

    if not valid:
        return valid, error

    valid, error = validate_stock(data["stock"])

    if not valid:
        return valid, error

    return True, None


def validate_order(data):
    """
    Full order validation.
    """

    valid, error = validate_required_fields(
        data,
        [
            "customer_name",
            "phone_number",
            "delivery_address"
        ]
    )

    if not valid:
        return valid, error

    valid, error = validate_phone(data["phone_number"])

    if not valid:
        return valid, error

    return True, None
def validate_email(email):

    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if not re.match(pattern, email):
        return False, "Invalid email address"

    return True, None


def validate_contact(data):

    valid, error = validate_required_fields(
        data,
        [
            "full_name",
            "email",
            "subject",
            "message"
        ]
    )

    if not valid:
        return valid, error

    return validate_email(data["email"])