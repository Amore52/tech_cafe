from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Order
from .forms import OrderForm, OrderItemFormSet


def order_list(request):
    query = request.GET.get('query')
    status_filter = request.GET.get('status')
    orders = Order.objects.all()
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
    if request.method == 'POST':
        form = OrderForm(request.POST)
        order_item_formset = OrderItemFormSet(request.POST)

        if form.is_valid() and order_item_formset.is_valid():
            order = form.save(commit=False)
            order.save()
            order_item_formset.instance = order
            order_item_formset.save()

            return redirect('order_list')
    else:
        form = OrderForm()
        order_item_formset = OrderItemFormSet()

    return render(request, 'add_order.html', {
        'form': form,
        'order_item_formset': order_item_formset,
    })


def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        order_item_formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and order_item_formset.is_valid():
            form.save()
            order_item_formset.save()
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)
        order_item_formset = OrderItemFormSet(instance=order)

    return render(request, 'edit_order.html', {
        'form': form,
        'order_item_formset': order_item_formset,
    })


def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('order_list')


def calculate_revenue(request):
    today = timezone.now().date()
    orders_today = Order.objects.filter(
        status='paid',
        completed_at__date=today
    )
    total_revenue = 0
    for order in orders_today:
        total_revenue += order.total_price

    return render(request, 'revenue.html', {
        'total_revenue': total_revenue,
        'today': today,
    })