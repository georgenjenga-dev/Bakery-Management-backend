from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate, bcrypt, jwt
from config import Config
from app.routes.payments import payments_bp
from app.routes.admin_orders import admin_orders_bp



def create_app():
    app = Flask(__name__)
    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_orders_bp)
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

    # Import models so Flask-Migrate can detect them
    from app.models.models import Product, Order, OrderItem, Admin
    
    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    return app