"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    def test_read_a_product(self):
        """It should read a product from the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        new_product = Product.find(product.id)
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_update_a_product(self):
        """It should update a product from the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        new_product = Product.find(product.id)
        self.assertEqual(new_product.id, product.id)

        # Update description
        product.description = "I have no idea what I am updating"
        product.update()
        products = Product.all()
        self.assertEqual(len(products), 1)
        new_product = Product.find(product.id)
        self.assertEqual(new_product.id, product.id)
        self.assertEqual(new_product.description, product.description)

    def test_delete_a_product(self):
        """It should update a product from the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()

        # Assert there is only 1 product in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        new_product = Product.find(product.id)
        self.assertEqual(new_product.id, product.id)

        # Remove product from the database
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should list all products from the database"""
        products = Product.all()
        self.assertEqual(products, [])

        # Create 5 product objects
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()

        # Fetch all products from the database
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """It should find a product by name from the database"""
        products = Product.all()
        self.assertEqual(products, [])

        # Create 5 product objects
        name_dict = {}
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            count = name_dict[product.name] if product.name in name_dict else 0
            name_dict[product.name] = count+1
            product.create()

        # Retrieve the name of the first product in the products list
        products = Product.all()
        name = products[0].name

        # Find the number of occurences of the product name in the List
        name_prods = Product.find_by_name(name)
        self.assertEqual(name_prods.count(), name_dict[name])

    def test_find_product_by_availability(self):
        """It should find a product by availability from the database"""
        products = Product.all()
        self.assertEqual(products, [])

        # Create a batch of 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 10)

        # Retrieve availability of first product
        availability = products[0].available
        count = len([product for product in products if product.available == availability])

        # Retrieve all products with same availability
        prods = Product.find_by_availability(availability)
        self.assertEqual(prods.count(), count)

    def test_find_product_by_category(self):
        """It should find a product by category from the database"""
        products = Product.all()
        self.assertEqual(products, [])

        # Create a batch of 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 10)

        # Retrieve category of first product
        category = products[0].category
        count = len([product for product in products if product.category == category])

        # Retrieve all products with same availability
        prods = Product.find_by_category(category)
        self.assertEqual(prods.count(), count)

    def test_find_product_by_price(self):
        """It should find a product by price from the database"""
        products = Product.all()
        self.assertEqual(products, [])

        # Create a batch of 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 10)

        # Retrieve price of first product
        price = products[0].price
        count = len([product for product in products if product.price == price])

        # Retrieve all products with same availability
        prods = Product.find_by_price(price)
        self.assertEqual(prods.count(), count)

    def test_data_validation_error(self):
        """It tests data validation error"""
        product = ProductFactory()
        product.id = None
        with self.assertRaises(DataValidationError):
            product.update()

        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_deserialize_dict(self):
        """It tests dict deserializing"""
        product = ProductFactory()
        product.id = None

        prod_dict = product.serialize()
        self.assertIsNotNone(prod_dict)

        prod_dict["available"] = "Available"
        self.assertRaises(DataValidationError, lambda: product.deserialize(prod_dict))

        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_deserialize_dict_invalid_attr(self):
        """It tests dict deserializing- invalid attribute """
        product = ProductFactory()
        product.id = None

        prod_dict = product.serialize()
        self.assertIsNotNone(prod_dict)

        with self.assertRaises(DataValidationError):
            product.deserialize([])

    def test_update_price_to_string(self):
        """It should test updating price to string type"""
        products = Product.all()
        self.assertEqual(products, [])

        # Create a batch of 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 10)

        # Retrieve price of first product
        price = products[0].price
        Product.find_by_price(str(price))
        self.assertEqual(products[0].price, price)
