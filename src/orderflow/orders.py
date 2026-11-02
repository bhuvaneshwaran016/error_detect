from .inventory import Inventory
from .models import Order, OrderItem, OrderStatus
from .payments import PaymentGateway
from .pricing import calculate_discount, calculate_tax, calculate_total, money
from .shipping import shipping_fee


class OrderError(Exception):
    pass


class OrderService:
    def __init__(self, inventory: Inventory, payments: PaymentGateway, tax_rate: float = 0.08):
        self.inventory = inventory
        self.payments = payments
        self.tax_rate = tax_rate
        self.orders: dict[str, Order] = {}

    def create_order(self, order_id: str, customer_id: str, quantities: dict[str, int],
                     discount_code: str | None = None, country: str = "US") -> Order:
        if order_id in self.orders:
            raise OrderError("duplicate order")
        if not customer_id or not quantities:
            raise OrderError("customer and items are required")

        items = []
        subtotal = 0.0
        for sku, quantity in quantities.items():
            product = self.inventory.get(sku)
            if not product.active:
                raise OrderError("inactive product")
            self.inventory.reserve(sku, quantity)
            items.append(OrderItem(sku, quantity, product.price))
            subtotal += product.price * quantity

        subtotal = money(subtotal)
        discount = calculate_discount(subtotal, discount_code)
        taxable = subtotal - discount
        tax = calculate_tax(taxable, self.tax_rate)
        shipping = shipping_fee(taxable, len(items), country)
        total = calculate_total(subtotal, discount, tax, shipping)

        order = Order(order_id, customer_id, items, subtotal, discount, tax, shipping, total)
        self.orders[order_id] = order
        return order

    def pay_order(self, order_id: str, idempotency_key: str) -> str:
        order = self._get_order(order_id)
        if order.status == OrderStatus.CANCELLED:
            raise OrderError("cancelled order cannot be paid")
        reference = self.payments.charge(order_id, order.total, idempotency_key)
        order.payment_reference = reference
        order.status = OrderStatus.PAID
        return reference

    def ship_order(self, order_id: str) -> None:
        order = self._get_order(order_id)
        if order.status != OrderStatus.PAID:
            raise OrderError("only paid orders can ship")
        order.status = OrderStatus.SHIPPED

    def cancel_order(self, order_id: str) -> None:
        order = self._get_order(order_id)
        if order.status == OrderStatus.SHIPPED:
            raise OrderError("shipped order cannot be cancelled")
        for item in order.items:
            self.inventory.release(item.sku, item.quantity)
        order.status = OrderStatus.CANCELLED

    def refund_order(self, order_id: str, amount: float, idempotency_key: str) -> None:
        order = self._get_order(order_id)
        if order.status not in (OrderStatus.PAID, OrderStatus.SHIPPED):
            raise OrderError("order is not refundable")
        if amount > order.total - order.refund_total:
            raise OrderError("refund exceeds remaining balance")
        self.payments.refund(idempotency_key, amount)
        order.refund_total = money(order.refund_total + amount)
        if order.refund_total == order.total:
            order.status = OrderStatus.REFUNDED

    def _get_order(self, order_id: str) -> Order:
        try:
            return self.orders[order_id]
        except KeyError:
            raise OrderError("order not found") from None
