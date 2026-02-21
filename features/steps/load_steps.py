######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
######################################################################

"""
Product Steps

Steps file for products.feature
"""

import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given('the following products')
def step_impl(context):
    """Delete all Products and load new ones"""

    rest_endpoint = f"{context.base_url}/products"

    # ------------------------------------------------------------------
    # Delete all existing products
    # ------------------------------------------------------------------
    context.resp = requests.get(rest_endpoint)
    assert context.resp.status_code == HTTP_200_OK

    for product in context.resp.json():
        delete_resp = requests.delete(f"{rest_endpoint}/{product['id']}")
        assert delete_resp.status_code == HTTP_204_NO_CONTENT

    # ------------------------------------------------------------------
    # Load new products from feature table
    # ------------------------------------------------------------------
    for row in context.table:
        payload = {
            "name": row["name"],
            "description": row["description"],
            "price": float(row["price"]),
            "available": row["available"] in ["True", "true", "1"],
            "category": row["category"],
        }

        context.resp = requests.post(rest_endpoint, json=payload)
        assert context.resp.status_code == HTTP_201_CREATED