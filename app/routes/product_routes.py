from flask import Blueprint, request


from app.utils.helpers import (
    success_response,
    error_response,
    admin_required,
)

from app.utils.validators import validate_product

from app.services.product_service import (
    get_all_products,
    get_product,
    create_product,
    update_product,
    delete_product,
    search_products,
    get_products_by_category,
)

product_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/products",
)


@product_bp.get("/")
def products():
    """
    GET /products
    """

    products = get_all_products()

    return success_response(products)


@product_bp.get("/<int:product_id>")
def single_product(product_id):

    product = get_product(product_id)

    if not product:
        return error_response("Product not found", 404)

    return success_response(product.to_dict())


@product_bp.get("/search")
def search():

    keyword = request.args.get("q")

    if not keyword:
        return error_response(
            "Search keyword is required"
        )

    products = search_products(keyword)

    return success_response(products)


@product_bp.get("/category/<string:category>")
def category_products(category):

    products = get_products_by_category(category)

    return success_response(products)


@product_bp.post("/")
@admin_required()
def add_product():

    data = request.get_json()

    valid, error = validate_product(data)

    if not valid:
        return error_response(error)

    product = create_product(data)

    return success_response(
        product.to_dict(),
        "Product created successfully",
        201,
    )


@product_bp.put("/<int:product_id>")
@admin_required()
def edit_product(product_id):

    product = get_product(product_id)

    if not product:
        return error_response(
            "Product not found",
            404,
        )

    data = request.get_json()

    valid, error = validate_product(data)

    if not valid:
        return error_response(error)

    product = update_product(
        product,
        data,
    )

    return success_response(
        product.to_dict(),
        "Product updated successfully",
    )


@product_bp.delete("/<int:product_id>")
@admin_required()
def remove_product(product_id):

    product = get_product(product_id)

    if not product:
        return error_response(
            "Product not found",
            404,
        )

    delete_product(product)

   