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
    ---
    tags:
      - Products
    responses:
      200:
        description: List of all products
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  description:
                    type: string
                  price:
                    type: number
                  stock:
                    type: integer
                  image:
                    type: string
                  category:
                    type: string
                  created_at:
                    type: string
    """

    products = get_all_products()

    return success_response(products)


@product_bp.get("/<int:product_id>")
def single_product(product_id):
    """
    GET /products/<product_id>
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: product_id
        required: true
        type: integer
        description: The product ID
    responses:
      200:
        description: Product details
      404:
        description: Product not found
    """

    product = get_product(product_id)

    if not product:
        return error_response("Product not found", 404)

    return success_response(product.to_dict())


@product_bp.get("/search")
def search():
    """
    GET /products/search
    ---
    tags:
      - Products
    parameters:
      - in: query
        name: q
        required: true
        type: string
        description: Search keyword
    responses:
      200:
        description: Search results
      400:
        description: Search keyword is required
    """

    keyword = request.args.get("q")

    if not keyword:
        return error_response(
            "Search keyword is required"
        )

    products = search_products(keyword)

    return success_response(products)


@product_bp.get("/category/<string:category>")
def category_products(category):
    """
    GET /products/category/<category>
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: category
        required: true
        type: string
        description: Product category name
    responses:
      200:
        description: Products in the category
    """

    products = get_products_by_category(category)

    return success_response(products)


@product_bp.post("/")
@admin_required()
def add_product():
    """
    POST /products
    ---
    tags:
      - Products
    security:
      - admin: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
            - stock
          properties:
            name:
              type: string
              example: "Chocolate Cake"
            description:
              type: string
              example: "Rich chocolate cake with ganache"
            price:
              type: number
              example: 2500.00
            stock:
              type: integer
              example: 50
            image:
              type: string
              example: "https://example.com/cake.jpg"
            category:
              type: string
              example: "Cakes"
    responses:
      201:
        description: Product created successfully
      400:
        description: Validation error
      401:
        description: Admin authentication required
      403:
        description: Super admin required
    """

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
    """
    PUT /products/<product_id>
    ---
    tags:
      - Products
    security:
      - admin: []
    parameters:
      - in: path
        name: product_id
        required: true
        type: integer
        description: The product ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            price:
              type: number
            stock:
              type: integer
            image:
              type: string
            category:
              type: string
    responses:
      200:
        description: Product updated successfully
      400:
        description: Validation error
      401:
        description: Admin authentication required
      404:
        description: Product not found
    """

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
    """
    DELETE /products/<product_id>
    ---
    tags:
      - Products
    security:
      - admin: []
    parameters:
      - in: path
        name: product_id
        required: true
        type: integer
        description: The product ID
    responses:
      200:
        description: Product deleted successfully
      401:
        description: Admin authentication required
      404:
        description: Product not found
    """

    product = get_product(product_id)

    if not product:
        return error_response(
            "Product not found",
            404,
        )

    delete_product(product)

    return success_response(
        message="Product deleted successfully"
    )

   