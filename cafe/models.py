from django.db import models

class Order(models.Model):
    STATUS = [
        ('pending', 'В ожидании'),
        ('prepare', 'Заказ готовится'),
        ('ready', 'Заказ готов'),
        ('paid', 'Заказ выполнен')
    ]
    table_number = models.IntegerField(verbose_name='Номер столика')
    items = models.JSONField(verbose_name='Заказ')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма заказа')
    status = models.CharField(max_length=10, choices=STATUS, default='В ожидании', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата и время выполнения')

    def __str__(self):
        return f'Заказ №{self.id}'

    def save(self, *args, **kwargs):
        self.total_price = sum(item['price'] for item in self.items)
        if self.status == 'paid' and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)