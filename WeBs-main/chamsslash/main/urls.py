"""
URL configuration for chamsslash project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path
from  main import views

app_name = 'main'
urlpatterns = [
    path('', views.products_view.as_view(), name='product_list'),
    path('money/', views.money_view.as_view(), name= 'money'),
    path('update_money/', views.UpdateMoneyView.as_view(), name='update_money'),
    path('about/', views.about_view.as_view(), name='about'),
    path('search/', views.products_view.as_view(), name='search'),
    path('inventory/', views.InventoryView.as_view(), name='inventory'),
    # path('inventorys/<slug:product_slug>', views.inventory_view.as_view(), name='inventory'),
    path('getproduct/<slug:product_slug>', views.product_view.as_view(), name='getproduct'),
    
    
    
]
