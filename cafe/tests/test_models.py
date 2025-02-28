import pytest
from cafe.models import Order, Item, OrderItem


@pytest.mark.django_db
def test_order_creation():
    order = Order.objects.create(table_number=1)
    assert order.table_number == 1
    assert order.status == Order.STATUS_PENDING

@pytest.mark.django_db
def test_total_price():
    item = Item.objects.create(name="Чай", price=100)
    order = Order.objects.create(table_number=1)
    OrderItem.objects.create(order=order, item=item, quantity=2)
    assert order.total_price == 200