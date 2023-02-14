import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import GoalCategory, Goal
from tests.goals.utils import BaseTestCase


@pytest.mark.django_db
class TestCategoryRetrieve(BaseTestCase):
    def test_retrieve_its_own_category_success(self, auth_client, user, board):
        board, category = board
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': category.id,
            'user': {'email': user.email,
                     'first_name': user.first_name,
                     'id': user.id,
                     'last_name': user.last_name,
                     'username': user.username},
            'created': self.date_time_str(category.created),
            'updated': self.date_time_str(category.updated),
            'title': category.title,
            'is_deleted': category.is_deleted,
            'board': category.board.id
        }

    def test_retrieve_category_from_an_alien_board_as_an_writer(self, auth_client, user, alien_board_writer):
        board, category = alien_board_writer
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])

        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': category.id,
            'user': {'email': user.email,
                     'first_name': user.first_name,
                     'id': user.id,
                     'last_name': user.last_name,
                     'username': user.username},
            'created': self.date_time_str(category.created),
            'updated': self.date_time_str(category.updated),
            'title': category.title,
            'is_deleted': category.is_deleted,
            'board': category.board.id
        }

    def test_retrieve_category_from_an_alien_board_as_an_reader(self, auth_client, alien_board_reader):
        board, category = alien_board_reader
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])

        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': category.id,
            'user': {'email': category.user.email,
                     'first_name': category.user.first_name,
                     'id': category.user.id,
                     'last_name': category.user.last_name,
                     'username': category.user.username},
            'created': self.date_time_str(category.created),
            'updated': self.date_time_str(category.updated),
            'title': category.title,
            'is_deleted': category.is_deleted,
            'board': category.board.id
        }

    def test_retrieve_from_an_alien_board(self, auth_client, alien_board, another_user):
        board, category = alien_board
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_unauthorized(self, client):
        url = reverse('goals:retrieve_update_destroy_category', args=[1])

        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUpdateCategory(BaseTestCase):
    def test_update_its_own_category(self, auth_client, board):
        board, category = board
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])

        response = auth_client.patch(url, data={'title': 'New title'})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['title'] == 'New title'

    def test_can_not_update_readonly_fields(self, auth_client, board):
        board, category = board
        board_id = board.id
        user_id = category.user.id
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])

        response = auth_client.patch(url, data={'user': 4, 'board': 3})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['board'] == board_id
        assert response.json()['user']['id'] == user_id

    def test_update_in_alien_board_as_a_writer(self, auth_client, alien_board_writer):
        board, category = alien_board_writer
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])

        response = auth_client.patch(url, data={'title': 'New title'})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['title'] == 'New title'

    def test_update_in_alien_board_as_a_reader(self, auth_client, alien_board_reader):
        board, category = alien_board_reader
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])

        response = auth_client.patch(url, data={'title': 'New title'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_in_alien_board(self, auth_client, alien_board):
        board, category = alien_board
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])

        response = auth_client.patch(url, data={'title': 'New title'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_unauthorized(self, client):
        url = reverse('goals:retrieve_update_destroy_category', args=[1])

        response = client.patch(url, data={'title': 'New title'})
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestDestroyCategory(BaseTestCase):
    def test_destroy_its_own_category(self, auth_client, board, goal_factory):
        board, category = board
        goal = goal_factory(category=category)
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])

        response = auth_client.delete(url)

        goal.refresh_from_db()

        assert response.status_code == status.HTTP_204_NO_CONTENT
        category = GoalCategory.objects.get(id=category.id)
        assert category.is_deleted
        assert goal.status == Goal.Status.archived

    def test_destroy_from_an_alien_board_as_a_writer(self, auth_client, alien_board_writer):
        board, category = alien_board_writer
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        category = GoalCategory.objects.get(id=category.id)
        assert category.is_deleted

    def test_destroy_from_an_alien_board_as_a_reader(self, auth_client, alien_board_reader):
        board, category = alien_board_reader
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        category = GoalCategory.objects.get(id=category.id)
        assert not category.is_deleted

    def test_destroy_from_an_alien_board(self, auth_client, alien_board):
        board, category = alien_board
        url = reverse('goals:retrieve_update_destroy_category', args=[category.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        category = GoalCategory.objects.get(id=category.id)
        assert not category.is_deleted

    def test_destroy_unauthorized(self, client):
        url = reverse('goals:retrieve_update_destroy_category', args=[1])

        response = client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
