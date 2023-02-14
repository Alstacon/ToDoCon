import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestSignup:
    url = reverse('core:signup-view')

    def test_signup_success(self, client, user_factory):
        user_data = user_factory.build()

        response = client.post(self.url, data={
            'username': user_data.username,
            'password': user_data.password,
            'password_repeat': user_data.password
        })

        assert response.status_code == status.HTTP_201_CREATED

    def test_signup_invalid_password(self, client, user_factory):
        user_data = user_factory.build()

        response = client.post(self.url, data={
            'username': user_data.username,
            'password': '123',
            'password_repeat': '123'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_invalid_password_repeat(self, client, user_factory):
        user_data = user_factory.build()

        response = client.post(self.url, data={
            'username': user_data.username,
            'password': user_data.password,
            'password_repeat': 'wrong password'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'password_repeat': ['Passwords must match']}

    def test_signup_used_username(self, client, user_factory, faker):
        user_saved = user_factory.create()

        response = client.post(self.url, data={
            'username': user_saved.username,
            'password': faker.password(),
            'password_repeat': faker.password()

        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'username': ['A user with that username already exists.']}
