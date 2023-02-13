import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Board
from tests.goals.utils import BaseTestCase


@pytest.mark.django_db
class TestBoardCreate(BaseTestCase):
    url = reverse('goals:create_board')

    def test_create_success(self, auth_client):
        response = auth_client.post(self.url, data={
            'title': 'Board',
        })
        board = Board.objects.last()
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'id': board.id,
            'created': self.date_time_str(board.created),
            'updated': self.date_time_str(board.updated),
            'title': board.title,
            'is_deleted': board.is_deleted,
        }

    def test_create_unauthorized(self, client, faker):
        response = client.post(self.url, data=faker.pydict(1))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_invalid_data(self, auth_client):
        response = auth_client.post(self.url, data={
            'is_deleted': True,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Board.objects.last()

    def test_create_board_participant_in_its_own_board(self, auth_client, another_user):
        response = auth_client.post(self.url, data={
            'title': 'Board',
        })
        assert response.status_code == status.HTTP_201_CREATED
        board = Board.objects.last()
        participants = board.participants.all()
        assert len(participants) == 1
