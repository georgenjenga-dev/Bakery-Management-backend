"""
Run this script to create the orders and order_items tables.
Add to your existing migration setup or run standalone.
"""

from app import db, create_app
from app.models.order import Order, OrderItem

app = create_app()

with app.app_context():
    # Create only the new tables
    db.create_all()
    print("Orders tables created successfully!")
    print("Tables: orders, order_items")