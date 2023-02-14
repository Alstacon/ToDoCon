from django.db import models

from core.models import User


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления')


class Board(BaseModel):
    title = models.CharField(max_length=255, verbose_name='Доска')
    is_deleted = models.BooleanField(default=False, verbose_name='Удалена')

    class Meta:
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'

    def __str__(self):
        return self.title


class GoalCategory(BaseModel):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Автор', related_name='category')
    title = models.CharField(max_length=255, verbose_name='Название')
    is_deleted = models.BooleanField(default=False, verbose_name='Удалена')
    board = models.ForeignKey(
        Board, on_delete=models.PROTECT, related_name='category', verbose_name='Доска'
    )

    def __str__(self):
        return self.title


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

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Автор', related_name='goals')
    category = models.ForeignKey(GoalCategory, on_delete=models.CASCADE, verbose_name='Категория', related_name='goals')
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.to_do, verbose_name='Статус')
    priority = models.PositiveSmallIntegerField(choices=Priority.choices, default=Priority.medium,
                                                verbose_name='Приоритет')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата дедлайна')

    def __str__(self):
        return self.title


class GoalComment(BaseModel):
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, verbose_name='Цель', related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор', related_name='comments')
    text = models.TextField(verbose_name='Текст комментария')

    def __str__(self):
        return self.text


class BoardParticipant(BaseModel):
    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
        unique_together = ('board', 'user')

    class Role(models.IntegerChoices):
        owner = 1, 'Владелец'
        writer = 2, 'Редактор'
        reader = 3, 'Читатель'

    board = models.ForeignKey(
        Board,
        on_delete=models.PROTECT,
        related_name='participants',
        verbose_name='Доска'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='participants',
        verbose_name='Пользователь'
    )

    role = models.PositiveSmallIntegerField(
        choices=Role.choices, default=Role.owner, verbose_name='Роль'
    )
