from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.db.models import Sum
from django.middleware.csrf import get_token
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api import serializers as s
from carts.models import Cart
from main.models import Categories, Products
from users.models import Inventory

ORDERINGS = ['id', '-id', 'name', '-name', 'price', '-price', 'event']


def cart_owner(request):
    """Корзина залогиненного пользователя — по user, анонима — по ключу сессии."""
    if request.user.is_authenticated:
        return {'user': request.user}
    if not request.session.session_key:
        request.session.create()
    return {'session_key': request.session.session_key}


def cart_items(request):
    return Cart.objects.filter(**cart_owner(request)).select_related('product', 'product__category')


def cart_total(items):
    return sum((item.total_price() for item in items), 0)


def error(message, code=status.HTTP_400_BAD_REQUEST):
    return Response({'success': False, 'error': message}, status=code)


# ---------- Служебное ----------

@extend_schema(tags=['Auth'], responses=inline_serializer('Csrf', {'csrfToken': serializers.CharField()}))
class CsrfView(APIView):
    """Ставит cookie `csrftoken` и возвращает его. Значение передавать в заголовке `X-CSRFToken` во всех POST."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'csrfToken': get_token(request)})


# ---------- Каталог ----------

@extend_schema(tags=['Каталог'])
class CategoryListView(generics.ListAPIView):
    """Все категории."""
    queryset = Categories.objects.all()
    serializer_class = s.CategorySerializer
    pagination_class = None


class ProductPagination(PageNumberPagination):
    page_size = 8


@extend_schema(
    tags=['Каталог'],
    parameters=[
        OpenApiParameter('q', str, description='Поиск по названию (без учёта регистра)'),
        OpenApiParameter('category', str, description='Слаг категории, например `gifs`'),
        OpenApiParameter('order_by', str, enum=ORDERINGS,
                         description='Сортировка; `event` — только лимитированные товары'),
    ],
)
class ProductListView(generics.ListAPIView):
    """Список товаров с поиском, фильтром по категории, сортировкой и пагинацией (8 на страницу)."""
    serializer_class = s.ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        queryset = Products.objects.select_related('category')
        params = self.request.query_params
        if q := params.get('q'):
            queryset = queryset.filter(name__icontains=q)
        if category := params.get('category'):
            queryset = queryset.filter(category__slug=category)
        order_by = params.get('order_by')
        if order_by == 'event':
            queryset = queryset.filter(event=True)
        if order_by in ORDERINGS:
            queryset = queryset.order_by(order_by)
        return queryset


@extend_schema(tags=['Каталог'])
class ProductDetailView(generics.RetrieveAPIView):
    """Один товар по слагу."""
    queryset = Products.objects.select_related('category')
    serializer_class = s.ProductSerializer
    lookup_field = 'slug'


# ---------- Корзина ----------

@extend_schema(tags=['Корзина'], responses=s.CartSerializer)
class CartView(APIView):
    """Содержимое корзины. Работает и для анонима (корзина привязана к сессии)."""
    permission_classes = [AllowAny]

    def get(self, request):
        items = list(cart_items(request))
        for item in items:
            item.total_price = item.product.price * item.quantity
        data = {
            'items': items,
            'total_price': sum((i.total_price for i in items), 0),
            'total_quantity': sum(i.quantity for i in items),
        }
        return Response(s.CartSerializer(data, context={'request': request}).data)


@extend_schema(tags=['Корзина'], request=s.CartAddRequest,
               responses={200: s.CartAddResponse, 400: s.ErrorResponse})
class CartAddView(APIView):
    """Добавить товар в корзину (+1, если уже есть). Работает и без логина."""
    permission_classes = [AllowAny]

    def post(self, request):
        body = s.CartAddRequest(data=request.data)
        if not body.is_valid():
            return error('Товар не указан.')
        try:
            product = Products.objects.get(id=body.validated_data['product_id'])
        except Products.DoesNotExist:
            return error('Товар не найден.')

        owner = cart_owner(request)
        item, created = Cart.objects.get_or_create(**owner, product=product, defaults={'quantity': 1})
        if not created:
            item.quantity += 1
            item.save()

        count = Cart.objects.filter(**owner).aggregate(total=Sum('quantity'))['total'] or 0
        return Response({'success': True, 'cart_count': count})


@extend_schema(tags=['Корзина'], request=s.CartUpdateRequest,
               responses={200: s.CartUpdateResponse, 400: s.ErrorResponse})
class CartUpdateQuantityView(APIView):
    """Изменить количество позиции на ±1. При 0 позиция удаляется."""
    permission_classes = [AllowAny]

    def post(self, request):
        body = s.CartUpdateRequest(data=request.data)
        if not body.is_valid():
            return error('Не указаны данные для изменения количества.')
        try:
            item = cart_items(request).get(id=body.validated_data['cart_item_id'])
        except Cart.DoesNotExist:
            return error('Товар не найден в корзине.')

        item.quantity += 1 if body.validated_data['action'] == 'increase' else -1
        if item.quantity <= 0:
            item.delete()
            new_quantity, item_total = 0, 0
        else:
            item.save()
            new_quantity, item_total = item.quantity, item.total_price()

        return Response(s.CartUpdateResponse({
            'success': True,
            'new_quantity': new_quantity,
            'item_total_price': item_total,
            'total_price': cart_total(cart_items(request)),
        }).data)


@extend_schema(tags=['Корзина'], request=s.CartRemoveRequest,
               responses={200: s.CartRemoveResponse, 400: s.ErrorResponse})
class CartRemoveView(APIView):
    """Удалить позицию из корзины целиком."""
    permission_classes = [AllowAny]

    def post(self, request):
        body = s.CartRemoveRequest(data=request.data)
        if not body.is_valid():
            return error('Не указан cart_item_id.')
        deleted, _ = cart_items(request).filter(id=body.validated_data['cart_item_id']).delete()
        if not deleted:
            return error('Товар не найден в корзине.')
        return Response(s.CartRemoveResponse({'success': True, 'total_price': cart_total(cart_items(request))}).data)


@extend_schema(tags=['Корзина'], request=None,
               responses={200: s.OrderResponse, 400: s.ErrorResponse})
class OrderView(APIView):
    """Оформить заказ: списывает баланс и переносит товары из корзины в инвентарь."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        with transaction.atomic():
            items = Cart.objects.filter(user=request.user).select_related('product')
            if not items.exists():
                return error('Корзина пуста.')
            total = cart_total(items)
            if request.user.money < total:
                return error('Недостаточно средств на балансе.')

            request.user.money -= total
            request.user.save()
            Inventory.objects.bulk_create(
                Inventory(user=request.user, product=i.product, quantity=i.quantity) for i in items
            )
            items.delete()
        return Response({'success': True, 'message': 'Заказ успешно оформлен!'})


# ---------- Пользователь ----------

@extend_schema(tags=['Пользователь'], request=None, responses=s.MoneyResponse)
class EarnMoneyView(APIView):
    """«Заработать»: +10 к балансу за вызов."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.money += 10
        request.user.save()
        return Response({'success': True, 'new_balance': request.user.money})


@extend_schema(tags=['Пользователь'])
class MeView(generics.RetrieveUpdateAPIView):
    """Текущий пользователь (GET) и редактирование профиля (PATCH)."""
    serializer_class = s.UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Пользователь'])
class InventoryView(generics.ListAPIView):
    """Купленные товары текущего пользователя."""
    serializer_class = s.InventoryItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Inventory.objects.filter(user=self.request.user).select_related('product', 'product__category')


# ---------- Auth (сессионная, через cookie) ----------

def attach_anon_cart(request, session_key, user):
    if session_key:
        Cart.objects.filter(session_key=session_key, user__isnull=True).update(user=user, session_key=None)


@extend_schema(tags=['Auth'], request=s.LoginSerializer,
               responses={200: s.UserSerializer, 400: s.ErrorResponse})
class LoginView(APIView):
    """Вход. Ставит сессионную cookie; анонимная корзина переносится в аккаунт.
    После входа Django меняет csrftoken — перечитайте cookie."""
    permission_classes = [AllowAny]

    def post(self, request):
        body = s.LoginSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        user = authenticate(request, **body.validated_data)
        if user is None:
            return error('Неверный логин или пароль.')
        session_key = request.session.session_key
        login(request, user)
        attach_anon_cart(request, session_key, user)
        return Response(s.UserSerializer(user, context={'request': request}).data)


@extend_schema(tags=['Auth'], request=s.RegisterSerializer,
               responses={201: s.UserSerializer, 400: OpenApiResponse(description='Ошибки валидации по полям')})
class RegisterView(APIView):
    """Регистрация и сразу вход."""
    permission_classes = [AllowAny]

    def post(self, request):
        body = s.RegisterSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        session_key = request.session.session_key
        user = body.save()
        login(request, user)
        attach_anon_cart(request, session_key, user)
        return Response(s.UserSerializer(user, context={'request': request}).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Auth'], request=None, responses={204: None})
class LogoutView(APIView):
    """Выход."""
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
