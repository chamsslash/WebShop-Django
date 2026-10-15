from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from carts.models import Cart
from main.models import Categories, Products
from users.models import Inventory, Userm


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Products
        fields = ['id', 'name', 'slug', 'description', 'image', 'price', 'quantity', 'event', 'category']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity', 'total_price', 'created_timestamp']


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = serializers.IntegerField()


class InventoryItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Inventory
        fields = ['id', 'product', 'quantity', 'added_timestamp']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userm
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'image', 'money']
        read_only_fields = ['id', 'money']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Userm
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def validate_email(self, email):
        if email and Userm.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        return email

    def validate_password(self, password):
        validate_password(password)
        return password

    def create(self, validated_data):
        return Userm.objects.create_user(**validated_data)


# --- тела запросов и ответы старых AJAX-ручек (формат сохранён ради шаблонов) ---

class CartAddRequest(serializers.Serializer):
    product_id = serializers.IntegerField()


class CartAddResponse(serializers.Serializer):
    success = serializers.BooleanField()
    cart_count = serializers.IntegerField()


class CartUpdateRequest(serializers.Serializer):
    cart_item_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['increase', 'decrease'])


class CartUpdateResponse(serializers.Serializer):
    success = serializers.BooleanField()
    new_quantity = serializers.IntegerField()
    item_total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class CartRemoveRequest(serializers.Serializer):
    cart_item_id = serializers.IntegerField()


class CartRemoveResponse(serializers.Serializer):
    success = serializers.BooleanField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class OrderResponse(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()


class MoneyResponse(serializers.Serializer):
    success = serializers.BooleanField()
    new_balance = serializers.IntegerField()


class ErrorResponse(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    error = serializers.CharField()
