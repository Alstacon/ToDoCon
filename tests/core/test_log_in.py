import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestLogin:
    url = reverse('core:login-view')

    def test_login_success(self, client, user_factory, faker):
        password = faker.password()
        user = user_factory.create(password=password)
        response = client.post(self.url, data={
            'username': user.username,
            'password': password,
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'username': user.username, 'password': password}

    def test_login_user_not_found(self, client, user_factory, faker):
        user = user_factory.build()
        response = client.post(self.url, data={
            'username': user.username,
            'password': faker.password(),
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_credentials(self, client, user, faker):
        response = client.post(self.url, data={
            'username': 'random_name',
            'password': faker.password(),
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN
