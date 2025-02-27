from django.shortcuts import render, get_object_or_404, redirect
from .models import Order
from .forms import OrderForm


def order_list(request):
    orders = Order.objects.all()
    return render(request, 'order_list.html', {'orders': orders})


def add_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total_price = sum(item['price'] for item in order.items)
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
    total_revenue = Order.objects.filter(status='paid').aggregate(total=models.Sum('total_price'))['total'] or 0
    return render(request, 'revenue.html', {'total_revenue': total_revenue})