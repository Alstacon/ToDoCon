import pytest
from django.urls import reverse
from rest_framework import status

from goals.serializers import GoalCategorySerializer


@pytest.mark.django_db
class TestCategoriesList:
    url = reverse('goals:list_of_categories')

    def test_get_list(self, auth_client, board, category_factory):
        board, category = board
        categories = category_factory.create_batch(2, board=board)

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for cat in GoalCategorySerializer(categories, many=True).data:
            assert cat in response.data

    def test_can_not_get_list_from_an_alien_board(self, auth_client, alien_board,
                                                  category_factory):
        board, _ = alien_board
        category_factory.create_batch(2, board=board)

        response = auth_client.get(self.url)

        assert response.data == []

    def test_get_list_from_an_alien_board_as_a_writer(self, auth_client, alien_board_writer,
                                                      category_factory):
        board, _ = alien_board_writer
        categories = category_factory.create_batch(2, board=board)

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for cat in GoalCategorySerializer(categories, many=True).data:
            assert cat in response.data

    def test_get_list_from_an_alien_board_as_a_reader(self, auth_client, alien_board_reader,
                                                      category_factory):
        board, _ = alien_board_reader
        categories = category_factory.create_batch(2, board=board)

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for cat in GoalCategorySerializer(categories, many=True).data:
            assert cat in response.data

    def test_get_list_unauthorized(self, client):
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_pagination(self, auth_client, board, category_factory):
        board, _ = board
        category_factory.create_batch(15, board=board)

        limit_response = auth_client.get(self.url, {'limit': 5})

        assert limit_response.status_code == status.HTTP_200_OK
        assert limit_response.json()['count'] == 16
        assert len(limit_response.json()['results']) == 5

        offset_response = auth_client.get(self.url, {'limit': 15, 'offset': 5})

        assert offset_response.status_code == status.HTTP_200_OK
        assert offset_response.json()['count'] == 16
        assert len(offset_response.json()['results']) == 11

    def test_ordering_by_title(self, auth_client, category_factory, board):
        board, category = board
        category.title = 'Test'
        category.save()
        for title in ['Test title', 'Title', 'New title']:
            category_factory.create(title=title, board=board)

        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert [goal['title'] for goal in response.json()] == ['New title', 'Test', 'Test title', 'Title']
