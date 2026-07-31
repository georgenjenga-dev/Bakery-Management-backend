import os

from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger

from config import Config
from app.extensions import db, migrate, bcrypt, jwt

from app.routes.payments import payments_bp
from app.routes.admin_routes import admin_bp, admin_orders_bp
from app.routes.product_routes import product_bp
from app.routes.order_routes import order_bp
from app.routes.contact_routes import contact_bp

from app.models.models import Admin, Product
from app.models.order import Order, OrderItem


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ==================================================
    # CORS
    # ==================================================
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5000",
        "https://bakery-management-frontend-dh1c.onrender.com",
        "https://bakery-management-frontend-41cl.onrender.com",
    ]

    # Supports a single URL or a comma-separated list, e.g.:
    # FRONTEND_URL=https://my-frontend.onrender.com,https://mycustomdomain.com
    frontend_url_env = os.getenv("FRONTEND_URL")
    if frontend_url_env:
        allowed_origins.extend(
            url.strip() for url in frontend_url_env.split(",") if url.strip()
        )

    CORS(
        app,
        resources={r"/*": {"origins": allowed_origins}},
        supports_credentials=True,
    )

    # ==================================================
    # Initialize Extensions
    # ==================================================
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # ==================================================
    # Swagger Documentation
    # ==================================================
    Swagger(
        app,
        template={
            "info": {
                "title": "Bakery Management API",
                "description": "Bakery Management REST API",
                "version": "1.0.0",
            }
        },
    )

    # ==================================================
    # Register Blueprints
    # ==================================================
    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_orders_bp)
    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(order_bp, url_prefix="/api/orders")
    app.register_blueprint(contact_bp, url_prefix="/api/contact")

    # ==================================================
    # Seed Database
    # ==================================================
    with app.app_context():
        try:
            seed_admin()
            seed_products()
        except Exception as e:
            app.logger.warning(f"Database initialization warning: {e}")

    # ==================================================
    # Health Check
    # ==================================================
    @app.get("/")
    def index():
        return jsonify({
            "message": "Bakery Management API",
            "status": "online",
            "database": "PostgreSQL",
            "version": "1.0.0",
            "endpoints": {
                "products": "/api/products",
                "orders": "/api/orders",
                "payments": "/api/payments",
                "admin": "/api/admin",
                "contact": "/api/contact",
                "swagger": "/apidocs/",
            },
        }), 200

    return app


# ============================================================
# Seed Default Admin
# ============================================================
def seed_admin():
    admin_email = os.getenv("ADMIN_EMAIL", "admin@bakery.com")

    if Admin.query.filter_by(email=admin_email).first():
        return

    admin = Admin(
        username=os.getenv("ADMIN_USERNAME", "admin"),
        email=admin_email,
        role="super_admin",
    )
    admin.set_password(os.getenv("ADMIN_PASSWORD", "admin123"))

    db.session.add(admin)
    db.session.commit()


# ============================================================
# Seed Products
# ============================================================
def seed_products():
    if Product.query.first():
        return

    products = [
        Product(
            name="Chocolate Cake",
            description="Rich chocolate sponge layered with creamy chocolate frosting.",
            price=1500,
            stock=15,
            image="https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600",
            category="Cake",
        ),
        Product(
            name="Croissant",
            description="Fresh buttery croissant with a flaky crust.",
            price=180,
            stock=25,
            image="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSoAfVdKKxy4oIF9yOGG7mYNm7URUao4-uDeTO4uj2Syw&s=10",
            category="Pastry",
        ),
        Product(
            name="Vanilla Cupcake",
            description="Vanilla cupcake topped with buttercream frosting.",
            price=150,
            stock=30,
            image="https://images.unsplash.com/photo-1486427944299-d1955d23e34d?w=600",
            category="Cupcake",
        ),
        Product(
            name="French Bread",
            description="Freshly baked French bread.",
            price=60,
            stock=40,
            image="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600",
            category="Bread",
        ),
        Product(
            name="Donuts",
            description="Soft donuts glazed with chocolate and vanilla icing.",
            price=120,
            stock=20,
            image="https://images.unsplash.com/photo-1551024601-bec78aea704b?w=600",
            category="Pastry",
        ),
        Product(
            name="Cookies",
            description="Crunchy chocolate chip cookies baked daily.",
            price=100,
            stock=50,
            image="https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=600",
            category="Cookies",
        ),
    ]

    db.session.add_all(products)
    db.session.commit()