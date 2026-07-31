import os
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
    app.config.from_object(Config)

    allowed_origins = [
        "https://bakery-management-frontend-dh1c.onrender.com",
        "http://localhost:5173",
        "http://localhost:5000",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5000",
    ]
    frontend_env = os.environ.get("FRONTEND_URL")
    if frontend_env and frontend_env not in allowed_origins:
        allowed_origins.append(frontend_env)

    CORS(
        app,
        resources={r"/*": {"origins": allowed_origins}},
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

    from app.models.models import Product, Admin, ContactMessage
    from app.models.order import Order, OrderItem
    
    from app.routes.admin_routes import admin_bp, admin_orders_bp
    from app.routes.product_routes import product_bp
    from app.routes.order_routes import order_bp
    from app.routes.contact_routes import contact_bp

    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_orders_bp)
    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(order_bp, url_prefix="/api/orders")
    app.register_blueprint(contact_bp, url_prefix="/api/contact")

    with app.app_context():
        try:
            db.create_all()
            if not Admin.query.filter_by(email="admin@bakery.com").first():
                admin = Admin(username="admin", email="admin@bakery.com", role="super_admin")
                admin.set_password("admin123")
                db.session.add(admin)
                db.session.commit()
            
            if Product.query.count() == 0:
                default_products = [
                    Product(
                        name="Chocolate Cake",
                        description="Rich chocolate sponge layered with creamy chocolate frosting.",
                        price=1500.0,
                        stock=15,
                        image="https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600",
                        category="Cake"
                    ),
                    Product(
                        name="Croissant",
                        description="Freshly baked buttery croissant with a flaky crust.",
                        price=180.0,
                        stock=25,
                        image="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSoAfVdKKxy4oIF9yOGG7mYNm7URUao4-uDeTO4uj2Syw&s=10",
                        category="Pastry"
                    ),
                    Product(
                        name="Vanilla Cupcake",
                        description="Vanilla cupcake topped with smooth buttercream frosting.",
                        price=150.0,
                        stock=30,
                        image="https://images.unsplash.com/photo-1486427944299-d1955d23e34d?w=600",
                        category="Cupcake"
                    ),
                    Product(
                        name="French Bread",
                        description="Crispy outside and soft inside, baked fresh every morning.",
                        price=60.0,
                        stock=40,
                        image="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600",
                        category="Bread"
                    ),
                    Product(
                        name="Donuts",
                        description="Soft donuts glazed with chocolate and vanilla icing.",
                        price=120.0,
                        stock=20,
                        image="https://images.unsplash.com/photo-1551024601-bec78aea704b?w=600",
                        category="Pastry"
                    ),
                    Product(
                        name="Cookies",
                        description="Crunchy chocolate chip cookies baked daily.",
                        price=100.0,
                        stock=50,
                        image="https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=600",
                        category="Cookies"
                    )
                ]
                db.session.add_all(default_products)
                db.session.commit()
        except Exception as e:
            app.logger.warning(f"Database initialization warning: {e}")

    @app.route("/")
    def index():
        return jsonify({
            "message": "Bakery Management API",
            "status": "online",
            "endpoints": {
                "products": "/api/products",
                "orders": "/api/orders",
                "payments": "/api/payments",
                "admin": "/api/admin",
                "contact": "/api/contact",
            }
        }), 200

    return app