from django.urls import path

from core.views import CreateUserView, LoginView, ProfileView, PasswordUpdateView

urlpatterns = [
    path('signup', CreateUserView.as_view(), name='signup-view'),
    path('login', LoginView.as_view(), name='login-view'),
    path('profile', ProfileView.as_view(), name='profile-view'),
    path('update_password', PasswordUpdateView.as_view(), name='change_password-view'),
]
