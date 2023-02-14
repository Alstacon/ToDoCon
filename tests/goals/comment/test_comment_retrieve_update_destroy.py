import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import GoalComment
from tests.goals.utils import BaseTestCase


@pytest.mark.django_db
class TestCommentRetrieve(BaseTestCase):
    def test_retrieve_its_own_comment_success(self, auth_client, goal, comment, user):
        url = reverse('goals:retrieve_update_destroy_comment', args=[comment.id])
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': comment.id,
            'user': {'email': user.email,
                     'first_name': user.first_name,
                     'id': user.id,
                     'last_name': user.last_name,
                     'username': user.username},
            'created': self.date_time_str(comment.created),
            'updated': self.date_time_str(comment.updated),
            'text': comment.text,
            'goal': comment.goal.id
        }

    def test_retrieve_comment_from_an_alien_board_as_a_writer(self, auth_client, goal_alien_board_writer,
                                                              comment_alien_board_writer):
        url = reverse('goals:retrieve_update_destroy_comment', args=[comment_alien_board_writer.id])

        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': comment_alien_board_writer.id,
            'user': {'email': comment_alien_board_writer.user.email,
                     'first_name': comment_alien_board_writer.user.first_name,
                     'id': comment_alien_board_writer.user.id,
                     'last_name': comment_alien_board_writer.user.last_name,
                     'username': comment_alien_board_writer.user.username},
            'created': self.date_time_str(comment_alien_board_writer.created),
            'updated': self.date_time_str(comment_alien_board_writer.updated),
            'text': comment_alien_board_writer.text,
            'goal': comment_alien_board_writer.goal.id
        }

    def test_retrieve_comment_from_an_alien_board_as_a_reader(self, auth_client, goal_alien_board_reader,
                                                              comment_alien_board_reader):
        url = reverse('goals:retrieve_update_destroy_comment', args=[comment_alien_board_reader.id])

        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': comment_alien_board_reader.id,
            'user': {'email': comment_alien_board_reader.user.email,
                     'first_name': comment_alien_board_reader.user.first_name,
                     'id': comment_alien_board_reader.user.id,
                     'last_name': comment_alien_board_reader.user.last_name,
                     'username': comment_alien_board_reader.user.username},
            'created': self.date_time_str(comment_alien_board_reader.created),
            'updated': self.date_time_str(comment_alien_board_reader.updated),
            'text': comment_alien_board_reader.text,
            'goal': comment_alien_board_reader.goal.id
        }

    def test_retrieve_from_an_alien_board(self, auth_client, goal_alien_board, alien_comment):
        url = reverse('goals:retrieve_update_destroy_comment', args=[alien_comment.id])
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_unauthorized(self, client):
        url = reverse('goals:retrieve_update_destroy_comment', args=[1])

        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUpdateComment(BaseTestCase):
    def test_update_its_own_comment(self, auth_client, comment):
        url = reverse('goals:retrieve_update_destroy_comment', args=[comment.id])

        response = auth_client.patch(url, data={'text': 'New text'})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['text'] == 'New text'

    def test_can_not_update_readonly_fields(self, auth_client, comment):
        comment_id = comment.id
        user_id = comment.user.id
        url = reverse('goals:retrieve_update_destroy_comment', args=[comment.id])

        response = auth_client.patch(url, data={'user': 4, 'id': 3})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['id'] == comment_id
        assert response.json()['user']['id'] == user_id

    def test_update_its_own_in_alien_board_as_a_writer(self, auth_client, comment_alien_board_writer):
        url = reverse('goals:retrieve_update_destroy_comment', args=[comment_alien_board_writer.id])

        response = auth_client.patch(url, data={'text': 'New text'})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['text'] == 'New text'

    def test_update_alien_in_alien_board_as_a_writer(self, auth_client, alien_comment_alien_board_writer):
        url = reverse('goals:retrieve_update_destroy_comment', args=[alien_comment_alien_board_writer.id])

        response = auth_client.patch(url, data={'text': 'New text'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_in_alien_board_as_a_reader(self, auth_client, comment_alien_board_reader):
        url = reverse('goals:retrieve_update_destroy_comment', args=[comment_alien_board_reader.id])

        response = auth_client.patch(url, data={'text': 'New text'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_alien_in_alien_board(self, auth_client, alien_comment):
        url = reverse('goals:retrieve_update_destroy_comment', args=[alien_comment.id])

        response = auth_client.patch(url, data={'text': 'New text'})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_alien_in_its_own_board(self, auth_client, alien_comment_my_board):
        url = reverse('goals:retrieve_update_destroy_comment', args=[alien_comment_my_board.id])

        response = auth_client.patch(url, data={'text': 'New text'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_unauthorized(self, client):
        url = reverse('goals:retrieve_update_destroy_comment', args=[1])

        response = client.patch(url, data={'text': 'New text'})
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestDestroyComment(BaseTestCase):
    def test_destroy_its_own_comment(self, auth_client, comment):
        url = reverse('goals:retrieve_update_destroy_comment', args=[comment.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not GoalComment.objects.last()

    def test_destroy_alien_comment(self, auth_client, alien_comment_my_board):
        url = reverse('goals:retrieve_update_destroy_comment', args=[alien_comment_my_board.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_destroy_its_onw_in_alien_board(self, auth_client, comment_alien_board_writer):
        url = reverse('goals:retrieve_update_destroy_comment', args=[comment_alien_board_writer.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not GoalComment.objects.last()

    def test_destroy_alien_in_alien_board_as_a_writer(self, auth_client, alien_comment_alien_board_writer):
        url = reverse('goals:retrieve_update_destroy_comment', args=[alien_comment_alien_board_writer.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_destroy_alien_in_alien_board_as_a_reader(self, auth_client, alien_comment_alien_board_reader):
        url = reverse('goals:retrieve_update_destroy_comment', args=[alien_comment_alien_board_reader.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_destroy_unauthorized(self, client):
        url = reverse('goals:retrieve_update_destroy_comment', args=[1])

        response = client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
