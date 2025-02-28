from django.db import models
from django.utils import timezone
from django.db.models import F, Sum


class Order(models.Model):
    STATUS = [
        ('pending', 'В ожидании'),
        ('prepare', 'Заказ готовится'),
        ('ready', 'Заказ готов'),
        ('paid', 'Заказ выполнен')
    ]
    table_number = models.IntegerField(verbose_name='Номер столика')
    status = models.CharField(max_length=10, choices=STATUS, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата и время выполнения')

    def __str__(self):
        return f'Заказ №{self.id}'

    @property
    def total_price(self) -> float:
        total = self.order_items.aggregate(
            total=Sum(F('item__price') * F('quantity')))
        return total['total'] or 0

    def save(self, *args, **kwargs):
        if self.status == 'paid' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'paid':
            self.completed_at = None
        super().save(*args, **kwargs)


class Item(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название блюда')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.name


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.save()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.save()

