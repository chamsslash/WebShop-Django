from django.db import models

# Create your models here.
from django.db import models
from main.models import Products

from users.models import Userm


class CartQueryset(models.QuerySet):
    
    def total_price(self):
        return sum(cart.products_price() for cart in self)
    
    def total_quantity(self):
        if self:
            return sum(cart.quantity for cart in self)
        return 0
    

from django.db import models
from django.conf import settings  # Для использования модели пользователя
from main.models import Products  # Предполагаем, что товары хранятся в модели Products

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Пользователь',
        related_name='cart_items'
    )
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Количество'
    )
    session_key = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name='Ключ сессии'
    )
    created_timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        db_table = 'cart'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        ordering = ('created_timestamp',)

    def __str__(self):
        return f"{self.user or self.session_key} - {self.product.name} ({self.quantity})"

    def total_price(self):
        """
        Рассчитывает общую стоимость текущей записи в корзине.
        """
        return self.product.price * self.quantity
