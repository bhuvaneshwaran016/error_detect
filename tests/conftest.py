import pytest
from orderflow.inventory import Inventory
from orderflow.models import Product
from orderflow.orders import OrderService
from orderflow.payments import PaymentGateway


@pytest.fixture
def inventory():
    inv = Inventory()
    inv.add_product(Product("KB-01", "Mechanical Keyboard", 80.00, 20))
    inv.add_product(Product("MS-02", "Wireless Mouse", 25.00, 30))
    inv.add_product(Product("HD-03", "USB-C Hub", 49.99, 8))
    inv.add_product(Product("OFF-04", "Discontinued Cable", 5.00, 10, active=False))
    return inv


@pytest.fixture
def service(inventory):
    return OrderService(inventory, PaymentGateway())
