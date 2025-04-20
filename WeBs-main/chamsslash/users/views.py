from django.contrib import auth, messages

from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView

from carts.models import Cart
from users.forms import UserLoginForm, ProfileForm
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin


from users.models import Userm  

class profile_view(LoginRequiredMixin, UpdateView):
    model = Userm
    form_class = ProfileForm
    template_name = 'profile.html'
    success_url = reverse_lazy('user:profile')  

    def get_object(self, queryset=None):
        # Возвращает текущего авторизованного пользователя
        return self.request.user
        #его данные автоматом подставляются в шаблон тк там мы используем {{form.username}} и тд
# class vhod(LoginView):
#     template_name = 'login.html'
#     form_class = UserLoginForm #типо валидация
#     success_url = reverse_lazy('allproducts')
#     def form_valid(self, form):
#         session_key = self.request.session.session_key# забираем сессионный ключ

#         user = form.get_user()#там специальная форма для которой уже преопределен метод для получения пользователя!"

#         if user:
#             auth.login(self.request, user)
#             if session_key:
#                 # delete old authorized user carts
#                 forgot_carts = Cart.objects.filter(user=user)#после логина удаляем все корзины по его пользлвателю(из формы валидной) которые он оставил в пред захлж в акк
#                 if forgot_carts.exists():
#                     forgot_carts.delete()
#                 # add new authorized user carts from anonimous session
#                 Cart.objects.filter(session_key=session_key).update(user=user)

#                 messages.success(self.request, f"{user.username}, Вы вошли в аккаунт")

#                 return HttpResponseRedirect(self.get_success_url())


from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib import auth
from users.forms import UserRegistrationForm
from carts.models import Cart  # Убедитесь, что модель Cart определена в вашем приложении

class registration(CreateView):
    template_name = 'registration.html'  # Путь к вашему шаблону
    form_class = UserRegistrationForm
    success_url = reverse_lazy('user:profile')  

    def form_valid(self, form):
        response = super().form_valid(form)#респонс в таких метод атоматически подставляется в return те там под катопом(return response) которы мы можем переопределить(как тут например)
        user = self.object  # Получаем созданного пользователя(опять же из метода get object)
        auth.login(self.request, user)  # Авторизуем пользователя

        session_key = self.request.session.session_key
        if session_key:
            Cart.objects.filter(session_key=session_key).update(user=user)

        messages.success(self.request, f"{user.username}, Вы успешно зарегистрированы и вошли в аккаунт.")
        return response

    def form_invalid(self, form):
        # Логирование ошибок (опционально)
        print(form.errors)  # печатает ошибки возникшие в форме
        messages.error(self.request, "Исправьте ошибки в форме.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)#получаем основнеой словарь с контестом с кваргами(перемнные выше) потом будем его дополнять
        context['title'] = 'Регистрация'
        return context
    def dispatch(self, request, *args, **kwargs):
        # Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            return redirect('user:profile')  # Перенаправляем на профиль или главную страницу
        return super().dispatch(request, *args, **kwargs)#возвращаем работу стандартного диспетчера если все норм
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        # Выход пользователя
        logout(request)# тут автоматом и юзер из request подставится
        # Перенаправление после выхода
        return redirect('main:product_list')  # Замените 'home' на имя URL вашей главной страницы
from django.contrib.auth import login as auth_login
class vhod(LoginView):
    template_name = 'login.html'
    form_class = UserLoginForm

    def form_valid(self, form):
        # Получаем пользователя из формы
        user = form.get_user()#у нас же спец форма поэтому сразу получаем пользователя из нее
        #она еще и сама проверяет есть ли такой
        # Входим в систему
        auth_login(self.request, user)

        # Перенаправляем на success_url
        return super().form_valid(form)#если у нас возвращается все из автоматической валидно формы то значит у нас продолжаются оставльные процессы к примеру перенаправление на др страницу по выполнению