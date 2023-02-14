import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from goals.models import Goal, GoalComment, Board, GoalCategory
from tests.factories import UserFactory, CategoryFactory, BoardParticipantFactory, BoardFactory, GoalFactory, \
    CommentFactory

register(UserFactory)
register(CategoryFactory)
register(BoardParticipantFactory)
register(BoardFactory)
register(GoalFactory)
register(CommentFactory)


@pytest.fixture()
def client() -> APIClient:
    return APIClient()


@pytest.fixture()
def auth_client(client, user) -> APIClient:
    client.force_login(user)
    return client


@pytest.fixture(autouse=True)
def another_user(user_factory):
    return user_factory.create()


@pytest.fixture
def board(board_factory, category_factory, user) -> tuple[Board, GoalCategory]:
    board = board_factory.create(with_owner=user)
    category = category_factory.create(board=board, user=user)
    return board, category


@pytest.fixture
def alien_board(board_factory, another_user, category_factory) -> tuple[Board, GoalCategory]:
    board = board_factory.create(with_owner=another_user)
    category = category_factory.create(board=board, user=another_user)
    return board, category


@pytest.fixture
def alien_board_writer(board_factory, board_participant_factory, category_factory, user) -> tuple[Board, GoalCategory]:
    board = board_factory.create()
    board_participant_factory(board=board, user=user, role=2)
    category = category_factory.create(board=board, user=user)
    return board, category


@pytest.fixture
def alien_board_reader(
        board_factory, board_participant_factory,
        category_factory, another_user, user) -> tuple[Board, GoalCategory]:
    board = board_factory.create()
    board_participant_factory(board=board, user=user, role=3)
    category = category_factory.create(board=board, user=another_user)
    return board, category


@pytest.fixture
def goal(goal_factory, user, board) -> Goal:
    _, category = board
    return goal_factory.create(user=user, category=category)


@pytest.fixture
def goal_alien_board_writer(goal_factory, alien_board_writer, user) -> Goal:
    _, category = alien_board_writer
    return goal_factory.create(user=user, category=category)


@pytest.fixture
def goal_alien_board_reader(goal_factory, alien_board_reader, user) -> Goal:
    _, category = alien_board_reader
    return goal_factory.create(user=user, category=category)


@pytest.fixture
def goal_alien_board(goal_factory, alien_board, another_user) -> Goal:
    _, category = alien_board
    return goal_factory.create(user=another_user, category=category)


@pytest.fixture
def comment(user, goal, comment_factory) -> GoalComment:
    return comment_factory.create(user=user, goal=goal)


@pytest.fixture
def alien_comment(goal_alien_board, comment_factory) -> GoalComment:
    return comment_factory.create(goal=goal_alien_board)


@pytest.fixture
def alien_comment_my_board(goal, comment_factory) -> GoalComment:
    return comment_factory.create(goal=goal)


@pytest.fixture
def comment_alien_board_writer(goal_alien_board_writer, comment_factory, user) -> GoalComment:
    return comment_factory.create(goal=goal_alien_board_writer, user=user)


@pytest.fixture
def alien_comment_alien_board_writer(goal_alien_board_writer, comment_factory, another_user) -> GoalComment:
    return comment_factory.create(goal=goal_alien_board_writer, user=another_user)


@pytest.fixture
def alien_comment_alien_board_reader(goal_alien_board_reader, comment_factory, another_user) -> GoalComment:
    return comment_factory.create(goal=goal_alien_board_reader, user=another_user)


@pytest.fixture
def comment_alien_board_reader(goal_alien_board_reader, comment_factory) -> GoalComment:
    return comment_factory.create(goal=goal_alien_board_reader)
