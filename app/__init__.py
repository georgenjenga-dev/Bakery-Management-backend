from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger

from config import Config
from app.routes.payments import payments_bp



from app.extensions import (
    db,
    migrate,
    bcrypt,
    jwt
)


def create_app():
    app = Flask(__name__)
    app.register_blueprint(payments_bp)
    app.config.from_object(Config)

    CORS(
        app,
        resources={r"/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    Swagger(app, template={
        "info": {
            "title": "Bakery Management API",
            "description": "API for products, orders, admin, contact, and M-Pesa payments",
            "version": "1.0.0"
        }
    })

    from app.models.models import (
        Admin,
        Product,
        Order,
        OrderItem,
        ContactMessage,
    )

    # Import models so Flask-Migrate can detect them
    from app.models.models import Product, Admin
    from app.models.order import Order, OrderItem
    
    from app.routes.admin_routes import admin_bp, admin_orders_bp
    from app.routes.product_routes import product_bp
    from app.routes.order_routes import order_bp
    from app.routes.contact_routes import contact_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_orders_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(contact_bp)

    @app.route("/")
    def index():
        return jsonify({
            "message": "Bakery Management API",
            "endpoints": {
                "products": "/api/products",
                "orders": "/api/orders",
                "payments": "/api/payments",
                "admin": "/api/admin",
                "contact": "/contact",
            }
        }), 200

    return app