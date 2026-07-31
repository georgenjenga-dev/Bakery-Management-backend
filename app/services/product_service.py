from app.extensions import db
from app.models.models import Product


def get_all_products():
    """
    Returns all products ordered by newest first.
    """
    products = Product.query.order_by(Product.created_at.desc()).all()
    return [product.to_dict() for product in products]


def get_product(product_id):
    """
    Returns a single product or None.
    """
    return db.session.get(Product, product_id)


def create_product(data):
    """
    Creates a new bakery product.
    """

    product = Product(
        name=data["name"],
        description=data.get("description"),
        price=data["price"],
        stock=data["stock"],
        image=data.get("image"),
        category=data.get("category")
    )

    db.session.add(product)
    db.session.commit()

    return product


def update_product(product, data):
    """
    Updates an existing product.
    """

    product.name = data.get("name", product.name)
    product.description = data.get("description", product.description)
    product.price = data.get("price", product.price)
    product.stock = data.get("stock", product.stock)
    product.image = data.get("image", product.image)
    product.category = data.get("category", product.category)

    db.session.commit()

    return product


def delete_product(product):
    """
    Deletes a product.
    """

    db.session.delete(product)
    db.session.commit()


def search_products(keyword):
    """
    Searches products by name.
    """

    products = Product.query.filter(
        Product.name.ilike(f"%{keyword}%")
    ).all()

    return [product.to_dict() for product in products]


def get_products_by_category(category):
    """
    Returns products belonging to one category.
    """

    products = Product.query.filter_by(
        category=category
    ).all()

    return [product.to_dict() for product in products]


def update_stock(product, quantity):
    """
    Reduces stock after an order.
    """

    product.stock -= quantity

    db.session.commit()

    return product