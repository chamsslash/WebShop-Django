from django.contrib import admin
from django.urls import path
from  users import views

app_name = 'users'
urlpatterns = [
    path('registration/', views.registration.as_view(), name='registration'),
    path('login/', views.vhod.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view.as_view(), name='profile'),
    
    
    
]
