import pytest
from django.urls import reverse
from rest_framework import status

from goals.serializers import BoardListSerializer


@pytest.mark.django_db
class TestBoardsList:
    url = reverse('goals:board_list')

    def test_get_list(self, auth_client, board_factory, user):
        boards = board_factory.create_batch(size=2, with_owner=user)

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for board in BoardListSerializer(boards, many=True).data:
            assert board in response.data

    def test_get_list_of_alien_as_a_participant(self, auth_client, alien_board_reader, alien_board_writer):
        reader_board, _ = alien_board_reader
        writer_board, _ = alien_board_writer
        boards = [reader_board, writer_board]

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for board in BoardListSerializer(boards, many=True).data:
            assert board in response.data

    def test_can_not_get_alien_boards(self, auth_client, board_factory):
        board_factory.create_batch(size=2)

        response = auth_client.get(self.url)

        assert response.data == []

    def test_get_list_unauthorized(self, client):
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_ordering_by_title(self, auth_client, board_factory, user):
        for title in ['Test title', 'Title', 'New title']:
            board_factory.create(title=title, with_owner=user)

        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert [board['title'] for board in response.json()] == ['New title', 'Test title', 'Title']

    def test_pagination(self, auth_client, board_factory, user):
        board_factory.create_batch(size=10, with_owner=user)

        limit_response = auth_client.get(self.url, {'limit': 3})
        assert limit_response.status_code == status.HTTP_200_OK
        assert limit_response.json()['count'] == 10
        assert len(limit_response.json()['results']) == 3

        offset_response = auth_client.get(self.url, {'limit': 100, 'offset': 8})
        assert offset_response.status_code == status.HTTP_200_OK
        assert offset_response.json()['count'] == 10
        assert len(offset_response.json()['results']) == 2
