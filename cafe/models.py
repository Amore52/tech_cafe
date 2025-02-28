from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.db.models import F, Sum


class Order(models.Model):
    """
    Модель заказа в кафе.
    Содержит информацию о номере стола, статусе заказа, времени создания и выполнения.
    """
    STATUS_PENDING = 'pending'
    STATUS_PREPARE = 'prepare'
    STATUS_READY = 'ready'
    STATUS_PAID = 'paid'

    STATUS = [
        (STATUS_PENDING, 'В ожидании'),
        (STATUS_PREPARE, 'Заказ готовится'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_PAID, 'Заказ выполнен')
    ]
    table_number = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Номер столика')
    status = models.CharField(max_length=10, choices=STATUS, default='STATUS_PENDING', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата и время выполнения')

    def __str__(self):
        return f'Заказ №{self.id}'

    @property
    def total_price(self) -> float:
        """
        Вычисляет общую стоимость заказа на основе связанных элементов заказа.
        Возвращает сумму стоимости всех блюд в заказе.
        """
        total = self.order_items.aggregate(
            total=Sum(F('item__price') * F('quantity')))
        return total['total'] or 0

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_PAID and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != self.STATUS_PAID:
            self.completed_at = None
        super().save(*args, **kwargs)


class Item(models.Model):
    """
    Модель блюда в кафе.
    Содержит название и цену блюда.
    """
    name = models.CharField(max_length=100, verbose_name='Название блюда')
    price = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                validators=[MinValueValidator(0)],
                                verbose_name='Цена')

    def __str__(self):
        return self.name


class OrderItem(models.Model):
    """
    Модель элемента заказа.
    Связывает заказ с блюдом и указывает количество.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.save()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.save()

