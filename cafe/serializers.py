from rest_framework import serializers
from .models import Order, OrderItem, Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'price']


class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    item_name = serializers.CharField(write_only=True)  # Название блюда для записи
    item_price = serializers.DecimalField(write_only=True, max_digits=10, decimal_places=2)  # Цена блюда для записи

    class Meta:
        model = OrderItem
        fields = ['id', 'item', 'item_name', 'item_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=False)

    class Meta:
        model = Order
        fields = ['id', 'table_number', 'status', 'created_at', 'completed_at', 'order_items']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items', [])
        order = Order.objects.create(**validated_data)

        for order_item_data in order_items_data:
            item_name = order_item_data.pop('item_name')
            item_price = order_item_data.pop('item_price')
            item, created = Item.objects.get_or_create(
                name=item_name,
                defaults={'price': item_price}
            )
            OrderItem.objects.create(order=order, item=item, **order_item_data)

        return order