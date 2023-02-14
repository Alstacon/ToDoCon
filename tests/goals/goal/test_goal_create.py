import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Goal
from tests.goals.utils import BaseTestCase


@pytest.mark.django_db
class TestGoalCreate(BaseTestCase):
    url = reverse('goals:create_goal')

    def test_create_success(self, auth_client, board):
        board, category = board
        response = auth_client.post(self.url, data={
            'category': category.id,
            'title': 'Test title'
        })

        goal = Goal.objects.last()
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'id': goal.id,
            'category': category.id,
            'created': self.date_time_str(goal.created),
            'updated': self.date_time_str(goal.updated),
            'title': 'Test title',
            'description': goal.description,
            'due_date': goal.due_date,
            'status': goal.status,
            'priority': goal.priority
        }

    def test_create_in_alien_board_as_a_writer(self, auth_client, alien_board_writer):
        board, category = alien_board_writer
        response = auth_client.post(self.url, data={
            'category': category.id,
            'title': 'Test title'
        })

        goal = Goal.objects.last()
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'id': goal.id,
            'category': category.id,
            'created': self.date_time_str(goal.created),
            'updated': self.date_time_str(goal.updated),
            'title': 'Test title',
            'description': goal.description,
            'due_date': goal.due_date,
            'status': goal.status,
            'priority': goal.priority
        }

    def test_create_in_alien_board_as_a_reader(self, auth_client, alien_board_reader):
        board, category = alien_board_reader
        response = auth_client.post(self.url, data={
            'category': category.id,
            'title': 'Test title'
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_in_alien_board(self, auth_client, alien_board):
        board, category = alien_board
        response = auth_client.post(self.url, data={
            'category': category.id,
            'title': 'Test title'
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_unauthorized(self, client):
        response = client.post(self.url, data={})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_invalid_data(self, auth_client, board):
        response = auth_client.post(self.url, data={
            'category': 0,
            'title': 12
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Goal.objects.last()

    def test_create_in_deleted_category(self, auth_client, board):
        board, category = board
        category_id = category.id
        category.is_deleted = True
        category.save()

        response = auth_client.post(self.url, data={
            'category': category_id,
            'title': 'Test title'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'category': ['Нельзя создать цель в удаленной категории']}
