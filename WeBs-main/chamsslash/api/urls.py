from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from api import views

app_name = 'api'
urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='docs'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),

    path('csrf/', views.CsrfView.as_view(), name='csrf'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),

    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product'),

    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.CartAddView.as_view(), name='cart_add'),
    path('cart/update-quantity/', views.CartUpdateQuantityView.as_view(), name='cart_update'),
    path('cart/remove/', views.CartRemoveView.as_view(), name='cart_remove'),
    path('cart/order/', views.OrderView.as_view(), name='order'),

    path('me/', views.MeView.as_view(), name='me'),
    path('me/inventory/', views.InventoryView.as_view(), name='inventory'),
    path('me/earn/', views.EarnMoneyView.as_view(), name='earn'),
]
