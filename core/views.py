from django.contrib.auth import login
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from core.models import User
from core.serializers import CreateUserSerializer, LoginSerializer


class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer


class LoginView(CreateAPIView):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(data=request.data, status=status.HTTP_200_OK)
