from django.urls import path

from core.views import UserCreateView, LoginView

urlpatterns = [
    path('signup', UserCreateView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
]
