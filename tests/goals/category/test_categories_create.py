import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import GoalCategory
from tests.goals.utils import BaseTestCase


@pytest.mark.django_db
class TestCategoryCreate(BaseTestCase):
    url = reverse('goals:create_category')

    def test_create_success(self, auth_client, board):
        board, _ = board
        response = auth_client.post(self.url, data={
            'title': 'Category',
            'board': board.id
        })
        category = GoalCategory.objects.last()
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'id': category.id,
            'created': self.date_time_str(category.created),
            'updated': self.date_time_str(category.updated),
            'title': category.title,
            'is_deleted': category.is_deleted,
            'board': category.board.id
        }

    def test_create_unauthorized(self, client, faker):
        response = client.post(self.url, data=faker.pydict(1))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_invalid_data(self, auth_client):
        response = auth_client.post(self.url, data={
            'title': 'Category',
            'board': '1'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not GoalCategory.objects.last()

    def test_can_not_create_in_alien_board(self, auth_client, alien_board):
        board, _ = alien_board
        response = auth_client.post(self.url, data={
            'title': 'Category',
            'board': board.id
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'You do not have permission to perform this action.'}

    def test_create_in_board_as_a_writer(self, auth_client, alien_board_writer):
        board, _ = alien_board_writer

        response = auth_client.post(self.url, data={
            'title': 'Category',
            'board': board.id
        })

        category = GoalCategory.objects.last()

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'id': category.id,
            'created': self.date_time_str(category.created),
            'updated': self.date_time_str(category.updated),
            'title': category.title,
            'is_deleted': category.is_deleted,
            'board': category.board.id
        }

    def test_create_in_board_as_a_reader(self, auth_client, alien_board_reader):
        board, _ = alien_board_reader

        response = auth_client.post(self.url, data={
            'title': 'Category',
            'board': board.id
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_can_not_create_in_deleted_board(self, auth_client, board):
        board, _ = board
        board_id = board.id
        board.is_deleted = True
        board.save()
        response = auth_client.post(self.url, data={
            'title': 'Category',
            'board': board_id
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'board': ['Нельзя создать категорию в удаленной доске.']}

    def test_can_not_create_deleted(self, auth_client, board):
        board, _ = board
        response = auth_client.post(self.url, data={
            'title': 'Category',
            'board': board.id,
            'is_deleted': True

        })
        category = GoalCategory.objects.last()
        assert response.status_code == status.HTTP_201_CREATED
        assert category.is_deleted is False
