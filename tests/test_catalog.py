import pytest
from orderflow.catalog import paginate, search_products


def test_search_is_case_insensitive(inventory):
    assert [p.sku for p in search_products(inventory.all_products(), "KEY")] == ["KB-01"]


def test_search_can_include_inactive_products(inventory):
    found = search_products(inventory.all_products(), "cable", active_only=False)
    assert [p.sku for p in found] == ["OFF-04"]


def test_pagination_first_page_starts_at_zero():
    assert paginate(list(range(25)), 1, 10) == list(range(10))


def test_pagination_second_page_has_next_ten():
    assert paginate(list(range(25)), 2, 10) == list(range(10, 20))


def test_pagination_last_page_returns_remainder():
    assert paginate(list(range(25)), 3, 10) == list(range(20, 25))


@pytest.mark.parametrize("page,page_size", [(0, 10), (-1, 10), (1, 0), (1, -3)])
def test_pagination_rejects_invalid_arguments(page, page_size):
    with pytest.raises(ValueError):
        paginate([1, 2, 3], page, page_size)
