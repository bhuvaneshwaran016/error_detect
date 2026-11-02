import pytest
from orderflow.inventory import InventoryError


def test_reserve_reduces_stock(inventory):
    inventory.reserve("KB-01", 3)
    assert inventory.get("KB-01").stock == 17


@pytest.mark.parametrize("quantity", [0, -1, -5])
def test_reserve_rejects_non_positive_quantity(inventory, quantity):
    with pytest.raises(InventoryError):
        inventory.reserve("KB-01", quantity)


def test_release_restores_stock(inventory):
    inventory.reserve("KB-01", 4)
    inventory.release("KB-01", 4)
    assert inventory.get("KB-01").stock == 20


def test_release_rejects_negative_quantity(inventory):
    with pytest.raises(InventoryError):
        inventory.release("KB-01", -2)


def test_reserve_is_atomic_for_insufficient_stock(inventory):
    before = inventory.get("KB-01").stock
    with pytest.raises(InventoryError):
        inventory.reserve("KB-01", before + 1)
    assert inventory.get("KB-01").stock == before
