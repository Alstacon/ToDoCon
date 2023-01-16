from django.contrib import admin

from goals.models import GoalCategory


class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created', 'updated')
    search_fields = ('name', 'user')


admin.site.register(GoalCategory, GoalCategoryAdmin)
