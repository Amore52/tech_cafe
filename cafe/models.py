from django.db import models

class Order(models.Model):
    STATUS = [
        ('pending', 'В ожидании'),
        ('ready', 'Готово'),
        ('paid', 'Оплачено')
    ]
    table_number = models.IntegerField(related_name='Номер столика')
    items = models.JSONField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, related_name='Сумма заказа')
    status = models.CharField(max_length=10, choices=STATUS, default='В ожидании')
    created_at = models.DateField(auto_now_add=True, related_name='Дата создания')

    def __str__(self):
        return f'Заказ №{self.id}'
