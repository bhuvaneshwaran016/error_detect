import pytest
from orderflow.pricing import calculate_discount, calculate_tax, calculate_total, money
from orderflow.shipping import shipping_fee


def test_money_uses_half_up_rounding():
    assert money(2.675) == 2.68


def test_discount_code_is_whitespace_and_case_insensitive():
    assert calculate_discount(100, " save10 ") == 10.00


def test_unknown_discount_code_is_rejected():
    with pytest.raises(ValueError):
        calculate_discount(100, "SAVE100")


def test_tax_is_rounded_to_cents():
    assert calculate_tax(10.05, 0.075) == 0.75


def test_total_adds_shipping():
    assert calculate_total(100, 10, 7.2, 5) == 102.2


def test_free_shipping_threshold_uses_post_discount_subtotal():
    assert shipping_fee(99.99, 1) == 7.99
    assert shipping_fee(100.00, 1) == 0.0
