from django import forms
from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    """
    Форма для создания и редактирования заказа.
    """
    class Meta:
        model = Order
        fields = ['table_number', 'status']


class OrderItemForm(forms.ModelForm):
    """
    Форма для добавления элемента заказа.
    """
    class Meta:
        model = OrderItem
        fields = ['item', 'quantity']
        labels = {
            'item': '',
            'quantity': '',
        }


OrderItemFormSet = forms.inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=1
)