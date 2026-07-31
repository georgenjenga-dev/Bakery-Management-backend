from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    Swagger(app, template={
        "info": {
            "title": "Bakery Management API",
            "description": "API for products, orders, admin, contact, and M-Pesa payments",
            "version": "1.0.0"
        }
    })
