######################################################################
# Product Store Service with UI
######################################################################
from flask import jsonify, request, abort, url_for
from service.models import Product, Category
from service.common import status
from . import app


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# HOME PAGE
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# UTILITY FUNCTION
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] != content_type:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )


######################################################################
# CREATE A NEW PRODUCT
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """Creates a Product"""
    check_content_type("application/json")

    data = request.get_json()
    product = Product()
    product.deserialize(data)
    product.create()

    location_url = url_for(
        "get_products",
        product_id=product.id,
        _external=True
    )

    return (
        jsonify(product.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# LIST ALL PRODUCTS (WITH FILTERS)
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns all Products or filters them"""
    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")

    if name:
        products = Product.find_by_name(name)

    elif category:
        try:
            category_enum = Category[category]
        except KeyError:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Invalid category: {category}",
            )

        products = Product.find_by_category(category_enum)

    elif available:
        products = Product.find_by_availability(
            available.lower() == "true"
        )

    else:
        products = Product.all()

    results = [product.serialize() for product in products]
    return jsonify(results), status.HTTP_200_OK


######################################################################
# READ A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """Retrieve a single Product"""
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with id '{product_id}' was not found.",
        )

    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """Update an existing Product"""
    check_content_type("application/json")

    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with id '{product_id}' was not found.",
        )

    data = request.get_json()
    product.deserialize(data)
    product.update()

    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """Delete a Product"""
    product = Product.find(product_id)
    if product:
        product.delete()

    return "", status.HTTP_204_NO_CONTENT