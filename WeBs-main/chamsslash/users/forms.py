
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

from users.models import Userm
class ProfileForm(UserChangeForm):#изменение данных через профайл
    class Meta:
        model = Userm
        fields = (
            "image",
            "first_name",
            "last_name",
            "username",
            "email",)

    image = forms.ImageField(required=False)
    password = forms.CharField()
    username = forms.CharField()
    email = forms.CharField()
# your_app_name/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Userm

class UserRegistrationForm(UserCreationForm):
    image = forms.ImageField(required=False, label='Изображение профиля')

    class Meta:
        model = Userm
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "image",
            "password1",
            "password2",
        )

    # Опционально: вы можете добавить валидацию для email или других полей
    def clean_email(self):
        email = self.cleaned_data.get('email')#тут получаем очищенные данные те которые прошли через валидацию
        #клинед дата хранит все поля формы(которые мы ввели) если они прошли валидацию(те те которые прошли через валидацию становятся очищенными)
        if Userm.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email


class UserLoginForm(AuthenticationForm):#ну сверка даных и поиск схлжих с ними в бд

    class Meta:
        model = Userm
        fields = ['username', 'password']

    username = forms.CharField()#какие поля будем сверять с моделью выше(НО В МОДЕЛИ ВЫШЕ МЫ УКАЗАЛИ ОПРЕДЕЛЕННЫЕ ПОЛЯ ) те сверять мы будем с это моделью но с ограниченными полями
    password = forms.CharField()