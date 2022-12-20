from django.contrib import admin

from core.models import User


@admin.register(User)
class CustomAdminUser(admin.ModelAdmin):
    readonly_fields = ('last_login', 'date_joined')
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ('is_staff', 'is_active', 'is_superuser')


