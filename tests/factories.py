import factory

from core.models import User
from goals.models import GoalCategory, Board, BoardParticipant, Goal, GoalComment


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')
    email = ''

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._get_manager(model_class).create_user(*args, **kwargs)


class BoardFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('sentence')

    class Meta:
        model = Board

    @factory.post_generation
    def with_owner(self, create, owner, **kwargs):
        if owner:
            BoardParticipant.objects.create(board=self, user=owner, role=BoardParticipant.Role.owner)


class BoardParticipantFactory(factory.django.DjangoModelFactory):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = BoardParticipant


class CategoryFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence')
    board = factory.SubFactory(BoardFactory)

    class Meta:
        model = GoalCategory


class GoalFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    title = factory.Faker('sentence')

    class Meta:
        model = Goal


class CommentFactory(factory.django.DjangoModelFactory):
    goal = factory.SubFactory(GoalFactory)
    user = factory.SubFactory(UserFactory)
    text = factory.Faker('sentence')

    class Meta:
        model = GoalComment
