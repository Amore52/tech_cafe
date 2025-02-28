import pytest
from django.urls import reverse
from django.utils import timezone
from cafe.models import Order, Item, OrderItem
from cafe.forms import OrderForm, OrderItemFormSet


@pytest.mark.django_db
def test_index_view(client):
    """
    Проверяет, что представление index возвращает статус 200 и использует правильный шаблон.
    """
    response = client.get(reverse('index'))
    assert response.status_code == 200
    assert 'index.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_order_list_view(client):
    """
    Проверяет, что представление order_list возвращает статус 200 и использует правильный шаблон.
    """
    response = client.get(reverse('order_list'))
    assert response.status_code == 200
    assert 'order_list.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_order_list_view_with_filter(client):
    """
    Проверяет, что представление order_list корректно фильтрует заказы по статусу.
    """
    Order.objects.create(table_number=1, status='pending')
    Order.objects.create(table_number=2, status='paid')

    response = client.get(reverse('order_list') + '?status=paid')
    assert response.status_code == 200
    assert len(response.context['orders']) == 1
    assert response.context['orders'][0].status == 'paid'


@pytest.mark.django_db
def test_add_order_view_get(client):
    """
    Проверяет, что GET-запрос к add_order возвращает форму и formset.
    """
    response = client.get(reverse('add_order'))
    assert response.status_code == 200
    assert isinstance(response.context['form'], OrderForm)
    assert isinstance(response.context['order_item_formset'], OrderItemFormSet)


@pytest.mark.django_db
def test_add_order_view_post(client):
    """
    Проверяет, что POST-запрос к add_order создает новый заказ и перенаправляет на order_list.
    """
    item = Item.objects.create(name="Чай", price=100)
    data = {
        'table_number': 1,
        'status': 'pending',
        'order_items-TOTAL_FORMS': 1,
        'order_items-INITIAL_FORMS': 0,
        'order_items-0-item': item.id,
        'order_items-0-quantity': 2,
    }

    response = client.post(reverse('add_order'), data)
    assert response.status_code == 302
    assert response.url == reverse('order_list')

    order = Order.objects.first()
    assert order is not None
    assert order.table_number == 1
    assert order.status == 'pending'
    assert order.order_items.count() == 1


@pytest.mark.django_db
def test_edit_order_view_get(client):
    """
    Проверяет, что GET-запрос к edit_order возвращает форму и formset.
    """
    order = Order.objects.create(table_number=1, status='pending')
    response = client.get(reverse('edit_order', args=[order.id]))
    assert response.status_code == 200
    assert isinstance(response.context['form'], OrderForm)
    assert isinstance(response.context['order_item_formset'], OrderItemFormSet)


@pytest.mark.django_db
def test_edit_order_view_post(client):
    """
    Проверяет, что POST-запрос к edit_order обновляет заказ и перенаправляет на order_list.
    """
    order = Order.objects.create(table_number=1, status='pending')
    item = Item.objects.create(name="Чай", price=100)
    OrderItem.objects.create(order=order, item=item, quantity=1)

    data = {
        'table_number': 2,
        'status': 'paid',
        'order_items-TOTAL_FORMS': 1,
        'order_items-INITIAL_FORMS': 1,
        'order_items-0-item': item.id,
        'order_items-0-quantity': 3,
        'order_items-0-id': OrderItem.objects.first().id,
    }

    response = client.post(reverse('edit_order', args=[order.id]), data)
    assert response.status_code == 302
    assert response.url == reverse('order_list')

    order.refresh_from_db()
    assert order.table_number == 2
    assert order.status == 'paid'
    assert order.order_items.first().quantity == 3


@pytest.mark.django_db
def test_delete_order_view(client):
    """
    Проверяет, что представление delete_order удаляет заказ и перенаправляет на order_list.
    """
    order = Order.objects.create(table_number=1, status='pending')
    response = client.post(reverse('delete_order', args=[order.id]))
    assert response.status_code == 302
    assert response.url == reverse('order_list')
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_calculate_revenue_view(client):
    """
    Проверяет, что представление calculate_revenue корректно вычисляет выручку за сегодняшний день.
    """
    today = timezone.now().date()
    order = Order.objects.create(table_number=1, status='paid', completed_at=timezone.now())
    item = Item.objects.create(name="Чай", price=100)
    OrderItem.objects.create(order=order, item=item, quantity=2)

    response = client.get(reverse('calculate_revenue'))
    assert response.status_code == 200
    assert response.context['total_revenue'] == 200
    assert response.context['today'] == today