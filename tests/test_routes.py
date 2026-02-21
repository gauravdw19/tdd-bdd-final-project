######################################################################
# Product API Service Test Suite
######################################################################
import os
import logging
from decimal import Decimal
from unittest import TestCase
from service import app
from service.common import status
from service.models import db, init_db, Product
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/products"


######################################################################
# TEST CASES
######################################################################
class TestProductRoutes(TestCase):
    """Product Service tests"""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        db.session.close()

    def setUp(self):
        self.client = app.test_client()
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    ############################################################
    # Utility function
    ############################################################
    def _create_products(self, count=1):
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(
                BASE_URL,
                json=test_product.serialize()
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ############################################################
    # Basic Tests
    ############################################################
    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Product Catalog Administration", response.data)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["message"], "OK")

    ############################################################
    # CREATE
    ############################################################
    def test_create_product(self):
        test_product = ProductFactory()
        response = self.client.post(
            BASE_URL,
            json=test_product.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(
            Decimal(new_product["price"]),
            test_product.price
        )
        self.assertEqual(
            new_product["available"],
            test_product.available
        )
        self.assertEqual(
            new_product["category"],
            test_product.category.name
        )

    ############################################################
    # READ
    ############################################################
    def test_get_product(self):
        test_product = self._create_products(1)[0]
        response = self.client.get(
            f"{BASE_URL}/{test_product.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)

    def test_get_product_not_found(self):
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ############################################################
    # UPDATE
    ############################################################
    def test_update_product(self):
        test_product = self._create_products(1)[0]
        test_product.name = "Updated Name"

        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            json=test_product.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(data["name"], "Updated Name")

    ############################################################
    # DELETE
    ############################################################
    def test_delete_product(self):
        test_product = self._create_products(1)[0]

        response = self.client.delete(
            f"{BASE_URL}/{test_product.id}"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        response = self.client.get(
            f"{BASE_URL}/{test_product.id}"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    ############################################################
    # LIST
    ############################################################
    def test_list_all_products(self):
        self._create_products(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_query_by_name(self):
        products = self._create_products(5)
        target = products[0]

        response = self.client.get(
            BASE_URL,
            query_string={"name": target.name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertGreater(len(data), 0)

    def test_query_by_category(self):
        products = self._create_products(5)
        target = products[0]

        response = self.client.get(
            BASE_URL,
            query_string={"category": target.category.name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_query_by_availability(self):
        self._create_products(5)
        response = self.client.get(
            BASE_URL,
            query_string={"available": "true"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)