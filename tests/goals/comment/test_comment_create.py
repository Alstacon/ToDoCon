import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import GoalComment, Goal
from tests.goals.utils import BaseTestCase


@pytest.mark.django_db
class TestCommentCreate(BaseTestCase):
    url = reverse('goals:create_comment')

    def test_create_success(self, auth_client, goal):
        response = auth_client.post(self.url, data={
            'text': 'Test comment',
            'goal': goal.id
        })
        comment = GoalComment.objects.last()
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'id': comment.id,
            'created': self.date_time_str(comment.created),
            'updated': self.date_time_str(comment.updated),
            'text': 'Test comment',
            'goal': comment.goal.id
        }

    def test_create_unauthorized(self, client, faker):
        response = client.post(self.url, data=faker.pydict(1))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_invalid_data(self, auth_client):
        response = auth_client.post(self.url, data={
            'text': 'Category',
            'goal': '1'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not GoalComment.objects.last()

    def test_can_not_create_in_alien_board(self, auth_client, goal_alien_board):
        response = auth_client.post(self.url, data={
            'title': 'Category',
            'goal': goal_alien_board.id
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'You do not have permission to perform this action.'}

    def test_create_in_alien_board_as_a_writer(self, auth_client, goal_alien_board_writer):
        response = auth_client.post(self.url, data={
            'text': 'Category',
            'goal': goal_alien_board_writer.id
        })

        comment = GoalComment.objects.last()

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'id': comment.id,
            'created': self.date_time_str(comment.created),
            'updated': self.date_time_str(comment.updated),
            'text': comment.text,
            'goal': comment.goal.id
        }

    def test_create_in_alien_board_as_a_reader(self, auth_client, goal_alien_board_reader):
        response = auth_client.post(self.url, data={
            'text': 'Category',
            'goal': goal_alien_board_reader.id
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_can_not_create_in_deleted_goal(self, auth_client, goal):
        goal.status = Goal.Status.archived
        goal.save()
        response = auth_client.post(self.url, data={
            'text': 'Category',
            'goal': goal.id
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'goal': ['Нельзя оставить комментарий к удаленной цели.']}

    def test_can_not_create_in_deleted_board(self, auth_client, goal):
        goal.category.board.is_deleted = True
        goal.category.board.save()
        response = auth_client.post(self.url, data={
            'text': 'Category',
            'goal': goal.id
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'goal': ['Нельзя оставить комментарий к цели в удаленной доске.']}
