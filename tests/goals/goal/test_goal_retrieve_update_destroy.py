import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Goal
from tests.goals.utils import BaseTestCase


@pytest.mark.django_db
class TestGoalRetrieve(BaseTestCase):
    def test_retrieve_its_own_goal_success(self, auth_client, goal, user):
        url = reverse('goals:retrieve_update_goal', args=[goal.id])
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': goal.id,
            'user': {'email': user.email,
                     'first_name': user.first_name,
                     'id': user.id,
                     'last_name': user.last_name,
                     'username': user.username},
            'category': goal.category.id,
            'created': self.date_time_str(goal.created),
            'updated': self.date_time_str(goal.updated),
            'title': goal.title,
            'description': goal.description,
            'due_date': goal.due_date,
            'status': goal.status,
            'priority': goal.priority
        }

    def test_retrieve_goal_from_an_alien_board_as_an_writer(self, auth_client, user, goal_alien_board_writer):
        url = reverse('goals:retrieve_update_goal', args=[goal_alien_board_writer.id])

        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': goal_alien_board_writer.id,
            'user': {'email': user.email,
                     'first_name': user.first_name,
                     'id': user.id,
                     'last_name': user.last_name,
                     'username': user.username},
            'category': goal_alien_board_writer.category.id,
            'created': self.date_time_str(goal_alien_board_writer.created),
            'updated': self.date_time_str(goal_alien_board_writer.updated),
            'title': goal_alien_board_writer.title,
            'description': goal_alien_board_writer.description,
            'due_date': goal_alien_board_writer.due_date,
            'status': goal_alien_board_writer.status,
            'priority': goal_alien_board_writer.priority
        }

    def test_retrieve_goal_from_an_alien_board_as_an_reader(self, auth_client, user, goal_alien_board_reader):
        url = reverse('goals:retrieve_update_goal', args=[goal_alien_board_reader.id])

        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': goal_alien_board_reader.id,
            'user': {'email': user.email,
                     'first_name': user.first_name,
                     'id': user.id,
                     'last_name': user.last_name,
                     'username': user.username},
            'category': goal_alien_board_reader.category.id,
            'created': self.date_time_str(goal_alien_board_reader.created),
            'updated': self.date_time_str(goal_alien_board_reader.updated),
            'title': goal_alien_board_reader.title,
            'description': goal_alien_board_reader.description,
            'due_date': goal_alien_board_reader.due_date,
            'status': goal_alien_board_reader.status,
            'priority': goal_alien_board_reader.priority
        }

    def test_retrieve_from_an_alien_board(self, auth_client, goal_alien_board):
        url = reverse('goals:retrieve_update_goal', args=[goal_alien_board.id])
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_goal_from_an_archive(self, auth_client, goal):
        goal.status = Goal.Status.archived
        goal.save()
        url = reverse('goals:retrieve_update_goal', args=[goal.id])
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_goal_with_deleted_category(self, auth_client, goal):
        goal.category.is_deleted = True
        goal.category.save()

        url = reverse('goals:retrieve_update_goal', args=[goal.id])
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_unauthorized(self, client):
        url = reverse('goals:retrieve_update_goal', args=[1])

        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUpdateGoal(BaseTestCase):
    def test_update_its_own_goal(self, auth_client, goal):
        url = reverse('goals:retrieve_update_goal', args=[goal.id])

        response = auth_client.patch(url, data={'title': 'New title'})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['title'] == 'New title'

    def test_can_not_update_readonly_fields(self, auth_client, goal):
        goal_id = goal.id
        user_id = goal.user.id
        url = reverse('goals:retrieve_update_goal', args=[goal.id])

        response = auth_client.patch(url, data={'id': 4, 'user': 3})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['id'] == goal_id
        assert response.json()['user']['id'] == user_id

    def test_update_in_alien_board_as_a_writer(self, auth_client, goal_alien_board_writer):
        url = reverse('goals:retrieve_update_goal', args=[goal_alien_board_writer.id])

        response = auth_client.patch(url, data={'title': 'New title'})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['title'] == 'New title'

    def test_update_in_alien_board_as_a_reader(self, auth_client, goal_alien_board_reader):
        url = reverse('goals:retrieve_update_goal', args=[goal_alien_board_reader.id])

        response = auth_client.patch(url, data={'title': 'New title'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_in_alien_board(self, auth_client, goal_alien_board):
        url = reverse('goals:retrieve_update_goal', args=[goal_alien_board.id])

        response = auth_client.patch(url, data={'title': 'New title'})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_unauthorized(self, client):
        url = reverse('goals:retrieve_update_goal', args=[1])

        response = client.patch(url, data={'title': 'New title'})
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestDestroyGoal(BaseTestCase):
    def test_destroy_its_own_goal(self, auth_client, goal):
        url = reverse('goals:retrieve_update_goal', args=[goal.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        goal = Goal.objects.get(id=goal.id)
        assert goal.status == Goal.Status.archived

    def test_destroy_from_an_alien_board_as_a_writer(self, auth_client, goal_alien_board_writer):
        url = reverse('goals:retrieve_update_goal', args=[goal_alien_board_writer.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        goal = Goal.objects.get(id=goal_alien_board_writer.id)
        assert goal.status == Goal.Status.archived

    def test_destroy_from_an_alien_board_as_a_reader(self, auth_client, goal_alien_board_reader):
        url = reverse('goals:retrieve_update_goal', args=[goal_alien_board_reader.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        goal = Goal.objects.get(id=goal_alien_board_reader.id)
        assert not goal.status == Goal.Status.archived

    def test_destroy_from_an_alien_board(self, auth_client, goal_alien_board):
        url = reverse('goals:retrieve_update_goal', args=[goal_alien_board.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        goal = Goal.objects.get(id=goal_alien_board.id)
        assert not goal.status == Goal.Status.archived

    def test_destroy_unauthorized(self, client):
        url = reverse('goals:retrieve_update_goal', args=[1])

        response = client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
