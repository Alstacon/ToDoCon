from django.urls import path

from core.views import CreateUserView, LoginView, ProfileView, PasswordUpdateView

urlpatterns = [
    path('signup', CreateUserView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('update_password', PasswordUpdateView.as_view(), name='profile'),
]
