from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from django.views.generic import DetailView, ListView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from main.models import Products
from main.utils import q_search
class money_view(TemplateView):
    template_name = 'money.html'
    from django.http import JsonResponse

# «Заработать» (update_money) — JSON-ручка в api/views.py: EarnMoneyView

class about_view(TemplateView):
    template_name = 'about.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Инструкция'
        context['content'] = "Инструкция"
        context['text_on_page'] = "Покупка товаров осуществляется либо на сайте( на главной странице),либо в нашем телеграм боте(перейти по вкладке 'телеграм бот').Свои купленные товары можно посотреть во вкладке инвентарь."
        context['text_on_page1'] = "Для получения денег можно перейти во вкладку -- заработать или в одну из вкладок в нашем телеграм боте"
        return context
#кварги это точ то выше те мы получае уже контекст которые автоматически передается и потом его мы 

from django.views.generic import ListView
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Products

class products_view(ListView):
    model = Products
    template_name = 'main.html'  # Ваш основной шаблон
    context_object_name = 'products'#как будет называться контекстная перемнная с кверисетом
    paginate_by = 8  # Количество товаров на странице

    def get_queryset(self):
        queryset = super().get_queryset()

        # Поиск по названию
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        # Фильтрация по категории
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)#category__slug два нижних подчеркивания тк обращаемся к модели которая релатионшип

        # Сортировка
        order_by = self.request.GET.get('order_by')
        if order_by == 'event':
            queryset = queryset.filter(event=True)
        if order_by:
            queryset = queryset.order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем параметры запроса в контекст для сохранения состояния в шаблоне(типо если это нажато то у него будет стиль другой)
        context['q'] = self.request.GET.get('q', '')
        context['category'] = self.request.GET.get('category', '')
        context['order_by'] = self.request.GET.get('order_by', '')
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Если это AJAX-запрос, возвращаем частичные шаблоны в формате JSON
            products_html = render_to_string('product_list_partial.html', context, request=self.request)
            pagination_html = render_to_string('pagination_partial.html', context, request=self.request)
            data = {
                'products_html': products_html,
                'pagination_html': pagination_html,
            }
            return JsonResponse(data)
        else:
            return super().render_to_response(context, **response_kwargs)#кварги это парметры которые ма переопределили в начале(до переопр методов)

class product_view(DetailView):#у нее только паджинации нет и есть метод get_object(типо толкьо один обьект)
    template_name = 'inventorycard.html'#надо сгенирировать
    context_object_name = "product"
    slug_url_kwarg = "product_slug"#кварг потому шо там еще может быть слаг какой нить
    #модель не надо мол сюда идет квери сет а ы просто вместо этого саи ручками выберем из продуктов нужный нам
    def get_object(self, queryset = None):#мы выбираем этот оин продукт не из кверисета
        product = get_object_or_404(Products, slug=self.kwargs[self.slug_url_kwarg])
        #типо мы берем из всех обьектов где слаг такой то ,те ы уже точно знаем что это атрибут именно продуктов и не надо это указывать(просто пишем слаг а не Products.slug = блабла)
        return product
    #те там где та под капотом создется переменная в которую идет результат из метода get object (object =  get_object()) в нашем случае это будет равно object = product(которую мы переопр в методе)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)#переменная которая возвращается в методе get object становится object к которому мы можем обращаться
        context["title"] = self.object.name
        context["description"] = self.object.description
        context['bought'] =  False
        return context
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import Inventory

class InventoryView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inventory_items'] = Inventory.objects.filter(user=self.request.user)
        return context

 
  
