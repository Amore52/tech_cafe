import logging

from django.db import transaction
from django.db.models import Sum, F
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Order
from .forms import OrderForm, OrderItemFormSet


logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')


def order_list(request):
    """
    Отображает список заказов с возможностью фильтрации по номеру стола и статусу.
    """
    query = request.GET.get('query')
    status_filter = request.GET.get('status')
    orders = Order.objects.all().prefetch_related('order_items')
    if query:
        orders = orders.filter(table_number__icontains=query)
    if status_filter:
        orders = orders.filter(status=status_filter)
    status_choices = Order.STATUS
    return render(request, 'order_list.html', {
        'orders': orders,
        'status_choices': status_choices,
    })


def add_order(request):
    """
    Обрабатывает добавление нового заказа.
    """
    if request.method == 'POST':
        form = OrderForm(request.POST)
        order_item_formset = OrderItemFormSet(request.POST)

        if form.is_valid() and order_item_formset.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.save()
                    order_item_formset.instance = order
                    order_item_formset.save()
                return redirect('order_list')
            except Exception as e:
                logger.error(f"Ошибка при сохранении заказа: {e}", exc_info=True)
    else:
        form = OrderForm()
        order_item_formset = OrderItemFormSet()

    return render(request, 'add_order.html', {
        'form': form,
        'order_item_formset': order_item_formset,
    })


def edit_order(request, order_id):
    """
    Обрабатывает редактирование существующего заказа.
    """
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        order_item_formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and order_item_formset.is_valid():
            try:
                form.save()
                order_item_formset.save()
                return redirect('order_list')
            except Exception as e:
                logger.error(f"Ошибка при редактировании заказа: {e}", exc_info=True)

    else:
        form = OrderForm(instance=order)
        order_item_formset = OrderItemFormSet(instance=order)

    return render(request, 'edit_order.html', {
        'form': form,
        'order_item_formset': order_item_formset,
    })


def delete_order(request, order_id):
    """
    Обрабатывает удаление заказа.
    """
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('order_list')


def calculate_revenue(request):
    """
    Вычисляет общую выручку за сегодняшний день для заказов со статусом "оплачено".
    """
    today = timezone.now().date()
    total_revenue = Order.objects.filter(
        status='paid',
        completed_at__date=today
    ).aggregate(
        total=Sum(F('order_items__item__price') * F('order_items__quantity'))
    )['total'] or 0

    return render(request, 'revenue.html', {
        'total_revenue': total_revenue,
        'today': today,
    })