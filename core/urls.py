from django.urls import path

from core.views import CreateUserView, LoginView

urlpatterns = [
    path('signup', CreateUserView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
]
