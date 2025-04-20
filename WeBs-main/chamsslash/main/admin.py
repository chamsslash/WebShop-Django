from django.contrib import admin



from main.models import Categories, Products

# admin.site.register(Categories)
# admin.site.register(Products)


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name",]

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}#автоматически применяется slugify (особенность работы  prepopulated_fields для отображения в админке)
    list_display = ["name", "quantity", "price"]
    search_fields = ["name", "description"]
    list_filter = [ "quantity", "category","event"]
    fields = [
        "name",
        "category",
        "slug",
        "description",
        "image",
        "price",
        "quantity",
        "event"
    ]
