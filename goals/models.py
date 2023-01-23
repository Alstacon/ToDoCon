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
    title = models.CharField(max_length=255, verbose_name='Название')
    is_deleted = models.BooleanField(default=False, verbose_name='Удалена')


class Goal(BaseModel):
    class Status(models.IntegerChoices):
        to_do = 1, 'К выполнению'
        in_progress = 2, 'В процессе'
        done = 3, 'Выполнено'
        archived = 4, 'Архив'

    class Priority(models.IntegerChoices):
        low = 1, 'Низкий'
        medium = 2, 'Средний'
        high = 3, 'Высокий'
        critical = 4, 'Критический'

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Автор')
    category = models.ForeignKey(GoalCategory, on_delete=models.CASCADE, verbose_name='Категория')
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.to_do, verbose_name='Статус')
    priority = models.PositiveSmallIntegerField(choices=Priority.choices, default=Priority.medium,
                                                verbose_name='Приоритет')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата дедлайна')


class GoalComment(BaseModel):
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, verbose_name='Цель')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    text = models.TextField(verbose_name='Текст комментария')
