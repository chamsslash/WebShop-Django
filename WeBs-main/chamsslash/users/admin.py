from django.contrib import admin
from users.models import Userm
# Register your models here.
@admin.register(Userm)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "first_name", "last_name", "email",]
    search_fields = ["username", "first_name", "last_name", "email",]

    