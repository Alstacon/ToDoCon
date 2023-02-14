import pytest
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.mark.django_db
class TestRetrieveProfile:
    url = reverse('core:profile-view')

    def test_get_profile(self, auth_client, user):
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }

    def test_profile_get_not_authorized(self, client):
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUpdateProfile:
    url = reverse('core:profile-view')

    def test_profile_update_success(self, auth_client, user):
        response = auth_client.patch(self.url, data={
            'first_name': 'name',
            'last_name': 'last name',
            'email': 'newmail@mail.ru'
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': user.id,
            'username': user.username,
            'first_name': 'name',
            'last_name': 'last name',
            'email': 'newmail@mail.ru'
        }

    def test_profile_update_unauthorized(self, client):
        response = client.patch(self.url, data={'email': 'newmail@mail.ru'})

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestDestroyProfile:
    url = reverse('core:profile-view')

    def test_destroy_success(self, auth_client, django_user_model):
        initial_count: int = django_user_model.objects.count()
        response = auth_client.delete(self.url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert django_user_model.objects.count() == initial_count

    @pytest.mark.parametrize('backend', settings.AUTHENTICATION_BACKENDS)
    def test_destroy_clean_session(self, client, user, backend):
        client.force_login(user=user, backend=backend)
        assert client.cookies['sessionid'].value
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not client.cookies['sessionid'].value

    def test_destroy_unauthorized(self, client):
        response = client.delete(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
