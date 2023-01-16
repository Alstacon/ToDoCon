from django.db import models

from core.models import User


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления')


class GoalCategory(BaseModel):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Автор')
    name = models.CharField(max_length=255, verbose_name='Название')
    is_deleted = models.BooleanField(default=False, verbose_name='Удалена')
