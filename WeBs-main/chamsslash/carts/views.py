from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from carts.mixin import CartMixin
from main.models import  Products
from carts.models import Cart


from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from .models import Cart, Products

# cart/views.py
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User
from .models import Cart, Products



from django.db import models










class add(View):
    def post(self, request, *args, **kwargs):
        try:
            # Получаем данные из POST-запроса
            data = json.loads(request.body)
            product_id = data.get("product_id")

            if not product_id:
                return JsonResponse({"success": False, "error": "Товар не указан."})

            # Проверяем, существует ли товар
            try:
                product = Products.objects.get(id=product_id)
            except Products.DoesNotExist:
                return JsonResponse({"success": False, "error": "Товар не найден."})

            # Проверяем наличие корзины пользователя
            if request.user.is_authenticated:
                user_identifier = request.user
            else:
                # Генерация session_key, если она еще не существует
                if not request.session.session_key:
                    request.session.create()
                user_identifier = request.session.session_key

            user_cart, created = Cart.objects.get_or_create(
                user=user_identifier,
                product=product,
                defaults={"quantity": 1}
            )

            if not created:
                # Если товар уже в корзине, увеличиваем количество
                user_cart.quantity += 1
                user_cart.save()

            # Подсчитываем общее количество товаров в корзине
            if request.user.is_authenticated:
                cart_count = Cart.objects.filter(user=request.user).aggregate(total=models.Sum('quantity'))['total'] or 0
            else:
                cart_count = Cart.objects.filter(user=request.session.session_key).aggregate(total=models.Sum('quantity'))['total'] or 0

            return JsonResponse({"success": True, "cart_count": cart_count})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cart_item_id = data.get("cart_item_id")

            cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
            cart_item.delete()#удаляет товар из бд ну и делает комммит

            total_price = sum(
                item.product.price * item.quantity for item in Cart.objects.filter(user=request.user)
            )

            return JsonResponse({"success": True, "total_price": total_price})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})



from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from carts.models import Cart

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

from carts.models import Cart


class UpdateQuantityView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            # Получаем данные из запроса
            data = json.loads(request.body)
            # Логирование данных
            
            cart_item_id = data.get("cart_item_id")
            action = data.get("action")#аякс отправляет тут у нас идет логирование поэтому мы будем отталкиваться от action мз аякса

            # Проверяем, переданы ли все необходимые данные
            if not cart_item_id or not action:
                return JsonResponse({"success": False, "error": "Не указаны данные для изменения количества."})

            # Проверяем, существует ли товар в корзине
            try:
                cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
            except Cart.DoesNotExist:
                return JsonResponse({"success": False, "error": "Товар не найден в корзине."})

            # Изменяем количество
            if action == "increase":
                cart_item.quantity += 1
            elif action == "decrease":
                cart_item.quantity -= 1

            # Удаляем товар, если количество стало 0
            if cart_item.quantity <= 0:
                cart_item.delete()
        
            else:
                cart_item.save()#коммит
                new_quantity = cart_item.quantity
                item_total_price = cart_item.total_price()

            # Пересчёт общей суммы
            total_price = sum(
                item.total_price() for item in Cart.objects.filter(user=request.user)
            )
          

            return JsonResponse({
                "success": True,
                "new_quantity": new_quantity,
                "item_total_price": item_total_price,
                "total_price": total_price
            })
        
        except Exception as e:
            # Возвращаем текст ошибки для диагностики
            print(f"Ошибка: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from carts.models import Cart
from users.models import Inventory  # Используем модель Inventory из примера выше

class OrderCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # Получаем все товары из корзины текущего пользователя
                user_cart_items = Cart.objects.filter(user=request.user)

                if not user_cart_items.exists():
                    return JsonResponse({"success": False, "error": "Корзина пуста."}, status=400)

                # Рассчитываем общую стоимость товаров в корзине
                total_price = sum(item.product.price * item.quantity for item in user_cart_items)

                # Проверяем, достаточно ли средств у пользователя
                if request.user.money < total_price:
                    return JsonResponse({"success": False, "error": "Недостаточно средств на балансе."}, status=400)

                # Снимаем деньги у пользователя
                request.user.money -= total_price
                request.user.save()

                # Переносим товары из корзины в инвентарь
                for cart_item in user_cart_items:
                    Inventory.objects.create(
                        user=request.user,
                        product=cart_item.product,
                        quantity=cart_item.quantity
                    )

                # Очищаем корзину
                user_cart_items.delete()

                return JsonResponse({"success": True, "message": "Заказ успешно оформлен!"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)