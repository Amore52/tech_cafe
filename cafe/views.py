from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order
from .forms import OrderForm
from django.utils import timezone


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
        if form.is_valid():
            order = form.save(commit=False)
            order.save()
            return redirect('order_list')
    else:
        form = OrderForm()
    return render(request, 'add_order.html', {'form': form})


def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            order.total_price = sum(item['price'] for item in order.items)
            order.save()
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)
    return render(request, 'edit_order.html', {'form': form})


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
    total_revenue = orders_today.aggregate(total=Sum('total_price'))['total'] or 0
    return render(request, 'revenue.html', {
        'total_revenue': total_revenue,
        'today': today,
    })