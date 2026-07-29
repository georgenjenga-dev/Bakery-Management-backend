from flask import Flask
from app.extensions import db, migrate, bcrypt, jwt
from config import Config

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Import models so Flask-Migrate can detect them
    from app.models.models import Product, Order, OrderItem, Admin
    
    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    return app