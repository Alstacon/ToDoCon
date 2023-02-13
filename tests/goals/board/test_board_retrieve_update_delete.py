import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import BoardParticipant, Goal
from tests.goals.utils import BaseTestCase


@pytest.mark.django_db
class TestBoardRetrieve(BaseTestCase):
    def test_retrieve_its_own_board(self, auth_client, board, user):
        board, _ = board
        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])

        participant = board.participants.last()

        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        assert participant.user == user

        assert response.json() == {
            'id': board.id,
            'created': self.date_time_str(board.created),
            'updated': self.date_time_str(board.updated),
            'title': board.title,
            'is_deleted': board.is_deleted,
            'participants': [{
                'id': participant.id,
                'role': BoardParticipant.Role.owner.value,
                'user': user.username,
                'created': self.date_time_str(participant.created),
                'updated': self.date_time_str(participant.updated),
                'board': participant.board_id
            }]
        }

    def test_retrieve_board_as_a_participant(self, auth_client, alien_board_reader, alien_board_writer):
        board_writer, _ = alien_board_writer
        board_reader, _ = alien_board_reader

        url_writer = reverse('goals:retrieve_update_destroy_board', args=[board_writer.id])
        url_reader = reverse('goals:retrieve_update_destroy_board', args=[board_reader.id])

        response_writer = auth_client.get(url_writer)
        assert response_writer.status_code == status.HTTP_200_OK

        response_reader = auth_client.get(url_reader)
        assert response_reader.status_code == status.HTTP_200_OK

    def test_retrieve_alien_board(self, auth_client, alien_board):
        board, _ = alien_board

        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])

        response = auth_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_deleted_board(self, auth_client, board):
        board, _ = board
        board.is_deleted = True
        board.save()

        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])

        response = auth_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_unauthorized(self, client):
        url = reverse('goals:retrieve_update_destroy_board', args=[1])
        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBoardUpdate:
    def test_update_its_own_board(self, auth_client, board):
        board, _ = board
        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])
        response = auth_client.patch(url, data={'title': 'New title'})

        assert response.status_code == status.HTTP_200_OK

        board.refresh_from_db()
        assert response.json()['title'] == 'New title'

    def test_can_not_update_or_edit_board_participants_as_a_writer_or_reader(self, auth_client, alien_board_writer,
                                                                             alien_board_reader, another_user):
        board_writer, _ = alien_board_writer
        board_reader, _ = alien_board_reader

        url_writer = reverse('goals:retrieve_update_destroy_board', args=[board_writer.id])
        url_reader = reverse('goals:retrieve_update_destroy_board', args=[board_reader.id])

        response_writer = auth_client.patch(url_writer, data={
            'title': 'New title',
            'participants':
                [{
                    'role': BoardParticipant.Role.writer,
                    'user': another_user.username,
                }]
        }, format='json')
        response_reader = auth_client.patch(url_reader, data={
            'title': 'New title',
            'participants':
                [{
                    'role': BoardParticipant.Role.writer,
                    'user': another_user.username,
                }]
        }, format='json')

        assert response_writer.status_code == status.HTTP_403_FORBIDDEN
        assert response_reader.status_code == status.HTTP_403_FORBIDDEN

    def test_can_not_update_alien_board(self, auth_client, alien_board):
        board, _ = alien_board

        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])

        response = auth_client.patch(url, data={'title': 'New title'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_add_participants_by_owner(self, auth_client, board, user, another_user):
        board, _ = board

        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])

        assert BoardParticipant.objects.count() == 1
        assert board.participants.last().user == user
        response = auth_client.patch(url, data={
            'participants':
                [{
                    'role': BoardParticipant.Role.writer,
                    'user': another_user.username,
                }],
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert BoardParticipant.objects.count() == 2

    def test_change_participants_role(self, auth_client, board, another_user):
        board, _ = board
        BoardParticipant.objects.create(board=board, user=another_user, role=BoardParticipant.Role.reader)

        assert board.participants.last().role == BoardParticipant.Role.reader

        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])
        response = auth_client.patch(url, data={
            'participants':
                [{
                    'role': BoardParticipant.Role.writer,
                    'user': another_user.username,
                }],
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert board.participants.last().user == another_user
        assert board.participants.last().role == BoardParticipant.Role.writer

    def test_can_not_change_owners_role(self, auth_client, board, user):
        board, _ = board

        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])
        response = auth_client.patch(url, data={
            'participants':
                [{
                    'role': BoardParticipant.Role.writer,
                    'user': user.username,
                }],
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert board.participants.last().user == user
        assert board.participants.last().role == BoardParticipant.Role.owner

    def test_can_not_change_participants_role_for_owner(self, auth_client, board, another_user):
        board, _ = board
        BoardParticipant.objects.create(board=board, user=another_user, role=BoardParticipant.Role.reader)

        assert board.participants.last().role == BoardParticipant.Role.reader

        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])
        response = auth_client.patch(url, data={
            'participants':
                [{
                    'role': BoardParticipant.Role.owner,
                    'user': another_user.username,
                }],
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert board.participants.last().user == another_user
        assert board.participants.last().role == BoardParticipant.Role.reader

    def test_can_not_add_participant_as_an_owner(self, auth_client, board, user, another_user):
        board, _ = board
        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])

        assert BoardParticipant.objects.count() == 1
        assert board.participants.last().user == user
        response = auth_client.patch(url, data={
            'participants':
                [{
                    'role': BoardParticipant.Role.owner,
                    'user': another_user.username,
                }],
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert BoardParticipant.objects.count() == 1

    def test_delete_participants_by_owner(self, auth_client, board, another_user, user):
        board, _ = board
        BoardParticipant.objects.create(board=board, user=another_user, role=BoardParticipant.Role.reader)

        assert BoardParticipant.objects.count() == 2
        assert board.participants.last().user == another_user

        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])
        response = auth_client.patch(url)

        assert response.status_code == status.HTTP_200_OK
        assert BoardParticipant.objects.count() == 1
        assert board.participants.last().user == user

    def test_can_not_delete_owner(self, auth_client, board, user):
        board, _ = board

        assert BoardParticipant.objects.count() == 1
        assert board.participants.last().user == user

        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])
        response = auth_client.patch(url)

        assert response.status_code == status.HTTP_200_OK
        assert BoardParticipant.objects.count() == 1
        assert board.participants.last().user == user

    def test_update_unauthorized(self, client):
        url = reverse('goals:retrieve_update_destroy_board', args=[1])

        response = client.patch(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBoardDestroy:
    def test_destroy_its_own_board(self, auth_client, board, user):
        board, category = board
        goal = Goal.objects.create(category=category, user=user)
        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])
        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        board.refresh_from_db()
        goal.refresh_from_db()
        category.refresh_from_db()

        assert board.is_deleted
        assert category.is_deleted
        assert goal.status == Goal.Status.archived

    def test_can_not_destroy_as_a_reader_or_writer(self, auth_client, alien_board_reader, alien_board_writer):
        board_writer, _ = alien_board_writer
        board_reader, _ = alien_board_reader

        url_writer = reverse('goals:retrieve_update_destroy_board', args=[board_writer.id])
        url_reader = reverse('goals:retrieve_update_destroy_board', args=[board_reader.id])

        response_writer = auth_client.delete(url_writer)
        assert response_writer.status_code == status.HTTP_403_FORBIDDEN

        response_reader = auth_client.delete(url_reader)
        assert response_reader.status_code == status.HTTP_403_FORBIDDEN

    def test_destroy_from_alien_board(self, auth_client, alien_board):
        board, _ = alien_board

        url = reverse('goals:retrieve_update_destroy_board', args=[board.id])

        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_destroy_unauthorized(self, client):
        response = client.delete(reverse('goals:retrieve_update_destroy_board', args=[1]))

        assert response.status_code == status.HTTP_403_FORBIDDEN
