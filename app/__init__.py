from flask import Flask
from flask_cors import CORS

from config import Config

from app.extensions import (
    db,
    migrate,
    bcrypt,
    jwt
)


def create_app():
    app = Flask(__name__)

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

    from app.models.models import (
        Admin,
        Product,
        Order,
        OrderItem,
        ContactMessage,
    )

    from app.routes.admin_routes import admin_bp
    from app.routes.product_routes import product_bp
    from app.routes.order_routes import order_bp
    from app.routes.contact_routes import contact_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(contact_bp)

    return app