from app import create_app
from app.extensions import db
from app.models.models import Product

app = create_app()

products = [
    {
        "name": "Chocolate Cake",
        "description": "Rich chocolate sponge layered with creamy chocolate frosting.",
        "price": 1500,
        "stock": 15,
        "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600",
        "category": "Cake",
    },
    {
        "name": "Croissant",
        "description": "Freshly baked buttery croissant.",
        "price": 180,
        "stock": 25,
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSoAfVdKKxy4oIF9yOGG7mYNm7URUao4-uDeTO4uj2Syw&s=10",
        "category": "Pastry",
    },
    # add the remaining products...
]

with app.app_context():

    if Product.query.count() == 0:

        for item in products:
            db.session.add(Product(**item))

        db.session.commit()

        print("Products seeded.")

    else:
        print("Products already exist.")