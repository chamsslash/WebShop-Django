from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class Userm(AbstractUser):
    image = models.ImageField(upload_to='users_images', blank=True, null=True, verbose_name='Аватар')
    money = models.IntegerField(
        default=0,
        verbose_name='Баланс пользователя'
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  # Уникальное имя для обратной связи
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Уникальное имя для обратной связи
        blank=True
    )
    class Meta:
        db_table = 'user'
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
from django.db import models
from django.conf import settings
from main.models import Products

class Inventory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество"
    )
    added_timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )

    class Meta:
        db_table = "inventory"
        verbose_name = "Инвентарь"
        verbose_name_plural = "Инвентарь"

    def __str__(self):
        return f"{self.user} - {self.product.name} ({self.quantity})"
