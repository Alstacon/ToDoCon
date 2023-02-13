import pytest
from dateutil import parser
from django.urls import reverse
from rest_framework import status

from goals.serializers import GoalCommentSerializer


@pytest.mark.django_db
class TestCommentsList:
    url = reverse('goals:list_of_comments')

    def test_get_list(self, auth_client, goal, comment_factory):
        comments = comment_factory.create_batch(2, goal=goal)

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for com in GoalCommentSerializer(comments, many=True).data:
            assert com in response.data

    def test_can_not_get_list_from_an_alien_board(self, auth_client, goal_alien_board, comment_factory):
        comment_factory.create_batch(2, goal=goal_alien_board)

        response = auth_client.get(self.url)

        assert response.data == []

    def test_get_list_from_an_alien_board_as_a_writer(self, auth_client, goal_alien_board_writer, comment_factory):
        comments = comment_factory.create_batch(2, goal=goal_alien_board_writer)

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for com in GoalCommentSerializer(comments, many=True).data:
            assert com in response.data

    def test_get_list_from_an_alien_board_as_a_reader(self, auth_client, goal_alien_board_reader, comment_factory):
        comments = comment_factory.create_batch(2, goal=goal_alien_board_reader)

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for com in GoalCommentSerializer(comments, many=True).data:
            assert com in response.data

    def test_get_list_unauthorized(self, client):
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_ordering_created(self, auth_client, comment_factory, goal):
        comment_factory.create_batch(20, goal=goal)

        response = auth_client.get(self.url)

        first = parser.isoparse(response.data[0]['created'])
        last = parser.isoparse(response.data[-1]['created'])

        assert first.time() > last.time()

    def test_pagination(self, auth_client, board, comment_factory, goal):
        comment_factory.create_batch(20, goal=goal)

        limit_response = auth_client.get(self.url, {'limit': 5})

        assert limit_response.status_code == status.HTTP_200_OK
        assert limit_response.json()['count'] == 20
        assert len(limit_response.json()['results']) == 5

        offset_response = auth_client.get(self.url, {'limit': 15, 'offset': 5})

        assert offset_response.status_code == status.HTTP_200_OK
        assert offset_response.json()['count'] == 20
        assert len(offset_response.json()['results']) == 15
