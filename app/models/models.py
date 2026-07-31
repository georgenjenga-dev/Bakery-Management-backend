from datetime import datetime
from decimal import Decimal

from ..extensions import db, bcrypt

ORDER_STATUS = (
    "Pending",
    "Preparing",
    "Ready",
    "Completed",
    "Cancelled"
)


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    description = db.Column(db.Text)

    price = db.Column(db.Numeric(10, 2), nullable=False)

    stock = db.Column(db.Integer, nullable=False, default=0)

    image = db.Column(db.String(255))

    category = db.Column(db.String(100))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    order_items = db.relationship(
        "OrderItem",
        back_populates="product",
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "stock": self.stock,
            "image": self.image,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
        }


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(
        db.String(120),
        nullable=False
    )

    phone_number = db.Column(
        db.String(20),
        nullable=False
    )

    delivery_address = db.Column(
        db.Text,
        nullable=False
    )

    total_price = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    order_items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "phone_number": self.phone_number,
            "delivery_address": self.delivery_address,
            "total_price": float(self.total_price),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "items": [
                item.to_dict()
                for item in self.order_items
            ],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    unit_price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    order = db.relationship(
        "Order",
        back_populates="order_items"
    )

    product = db.relationship(
        "Product",
        back_populates="order_items"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
        }
class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    subject = db.Column(
        db.String(200),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "created_at": self.created_at.isoformat()
        }    