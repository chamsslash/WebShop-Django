"""Демо-данные для локального запуска: python manage.py seed"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from main.models import Categories, Products
from users.models import Userm

CATEGORIES = [('Стикеры', 'stickers'), ('Аватарки', 'avatars'), ('Гифки', 'gifs')]


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми категориями, товарами и пользователями'

    def handle(self, *args, **options):
        cats = [Categories.objects.get_or_create(slug=slug, defaults={'name': name})[0]
                for name, slug in CATEGORIES]

        images = sorted(p.name for p in (Path(settings.MEDIA_ROOT) / 'goods_images').iterdir()
                        if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.webp'})
        for i, img in enumerate(images[:20], start=1):
            Products.objects.get_or_create(
                slug=f'product-{i}',
                defaults={
                    'name': f'Товар {i}',
                    'description': f'Описание тестового товара номер {i}.',
                    'image': f'goods_images/{img}',
                    'price': 10 * i,
                    'quantity': 100,
                    'category': cats[i % len(cats)],
                    'event': i % 5 == 0,
                },
            )

        if not Userm.objects.filter(username='admin').exists():
            Userm.objects.create_superuser('admin', 'admin@example.com', 'admin')
        if not Userm.objects.filter(username='test').exists():
            user = Userm.objects.create_user('test', 'test@example.com', 'test12345')
            user.money = 10000
            user.save()

        self.stdout.write(self.style.SUCCESS(
            f'Готово: {Categories.objects.count()} категорий, {Products.objects.count()} товаров. '
            'Логины: admin/admin (админка), test/test12345 (баланс 10000)'))
