from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from carts.models import Cart

# JSON-ручки корзины (add / update-quantity / delete / order) живут в api/views.py


class cart_view(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'carts.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        # Возвращаем товары корзины, принадлежащие текущему пользователю
        return Cart.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Рассчитываем общую стоимость товаров в корзине
        total_price = sum(item.product.price * item.quantity for item in context['cart_items'])

        # Добавляем в контекст цену для каждого товара
        for item in context['cart_items']:
            item.total_price = item.product.price * item.quantity  # добавляем поле для общей стоимости товара

        context['total_price'] = total_price
        return context
