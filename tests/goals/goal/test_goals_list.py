import pytest
from django.urls import reverse
from rest_framework import status

from goals.serializers import GoalSerializer
from tests.goals.utils import BaseTestCase


@pytest.mark.django_db
class TestGoalList(BaseTestCase):
    url = reverse('goals:list_of_goals')

    def test_get_list(self, auth_client, board, goal_factory):
        _, category = board
        goals = goal_factory.create_batch(2, category=category)

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for cat in GoalSerializer(goals, many=True).data:
            assert cat in response.data

    def test_can_not_get_list_from_an_alien_board(self, auth_client, alien_board, goal_factory):
        _, category = alien_board
        goal_factory.create_batch(2, category=category)

        response = auth_client.get(self.url)

        assert response.data == []

    def test_get_list_from_an_alien_board_as_a_participant_writer(self, auth_client, alien_board_writer, goal_factory):
        _, category = alien_board_writer
        goals = goal_factory.create_batch(2, category=category)

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for goal in GoalSerializer(goals, many=True).data:
            assert goal in response.data

    def test_get_list_from_an_alien_board_as_a_participant_reader(self, auth_client, alien_board_reader, goal_factory):
        _, category = alien_board_reader
        goals = goal_factory.create_batch(2, category=category)

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for goal in GoalSerializer(goals, many=True).data:
            assert goal in response.data

    def test_get_list_unauthorized(self, client):
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_pagination(self, auth_client, board, goal_factory):
        _, category = board
        goal_factory.create_batch(12, category=category)

        limit_response = auth_client.get(self.url, {'limit': 5})

        assert limit_response.status_code == status.HTTP_200_OK
        assert limit_response.json()['count'] == 12
        assert len(limit_response.json()['results']) == 5

        offset_response = auth_client.get(self.url, {'limit': 15, 'offset': 5})

        assert offset_response.status_code == status.HTTP_200_OK
        assert offset_response.json()['count'] == 12
        assert len(offset_response.json()['results']) == 7

    def test_ordering_by_due_date(self, auth_client, goal_factory, board):
        _, category = board
        for date in ['2024-01-01', '2023-02-24', '2023-06-01']:
            goal_factory.create(category=category, due_date=date)

        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert '2023-02-24' in self.date_time_str(response.json()[0]['due_date'])
        assert '2024-01-01' in self.date_time_str(response.json()[-1]['due_date'])
