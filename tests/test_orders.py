import pytest
from orderflow.models import OrderStatus
from orderflow.orders import OrderError


def test_create_order_reserves_inventory(service, inventory):
    order = service.create_order("O-1", "C-1", {"KB-01": 2})
    assert inventory.get("KB-01").stock == 18
    assert order.subtotal == 160.00


def test_create_order_rolls_back_all_reservations_if_later_item_fails(service, inventory):
    before = inventory.get("KB-01").stock
    with pytest.raises(Exception):
        service.create_order("O-2", "C-1", {"KB-01": 2, "MISSING": 1})
    assert inventory.get("KB-01").stock == before


def test_create_order_rejects_zero_quantity(service, inventory):
    before = inventory.get("KB-01").stock
    with pytest.raises(Exception):
        service.create_order("O-3", "C-1", {"KB-01": 0})
    assert inventory.get("KB-01").stock == before


def test_inactive_product_cannot_be_ordered(service):
    with pytest.raises(OrderError):
        service.create_order("O-4", "C-1", {"OFF-04": 1})


def test_order_total_and_shipping(service):
    order = service.create_order("O-5", "C-1", {"MS-02": 1})
    assert order.shipping == 7.99
    assert order.total == 34.99


def test_cancel_releases_stock_only_once(service, inventory):
    service.create_order("O-6", "C-1", {"KB-01": 2})
    service.cancel_order("O-6")
    with pytest.raises(OrderError):
        service.cancel_order("O-6")
    assert inventory.get("KB-01").stock == 20


def test_cannot_pay_cancelled_order(service):
    service.create_order("O-7", "C-1", {"MS-02": 1})
    service.cancel_order("O-7")
    with pytest.raises(OrderError):
        service.pay_order("O-7", "key-7")


def test_cannot_pay_same_order_with_different_idempotency_keys(service):
    service.create_order("O-8", "C-1", {"MS-02": 1})
    service.pay_order("O-8", "key-a")
    with pytest.raises(OrderError):
        service.pay_order("O-8", "key-b")


def test_refund_cannot_exceed_captured_payment(service):
    service.create_order("O-9", "C-1", {"MS-02": 1})
    service.pay_order("O-9", "pay-key-9")
    with pytest.raises(Exception):
        service.refund_order("O-9", 1000, "pay-key-9")


def test_refund_updates_status_only_when_fully_refunded(service):
    order = service.create_order("O-10", "C-1", {"MS-02": 1})
    service.pay_order("O-10", "pay-key-10")
    service.refund_order("O-10", order.total / 2, "pay-key-10")
    assert order.status == OrderStatus.PAID
    service.refund_order("O-10", order.total / 2, "pay-key-10")
    assert order.status == OrderStatus.REFUNDED


def test_shipped_order_cannot_be_cancelled(service):
    service.create_order("O-11", "C-1", {"MS-02": 1})
    service.pay_order("O-11", "key-11")
    service.ship_order("O-11")
    with pytest.raises(OrderError):
        service.cancel_order("O-11")
