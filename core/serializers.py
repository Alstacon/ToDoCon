from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from core.fields import PasswordField
from core.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    password = PasswordField(required=True)
    repeat_password = PasswordField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'repeat_password', 'first_name', 'last_name', 'email']

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['repeat_password']:
            raise ValidationError(detail="Passwords don't match")
        return attrs

    def create(self, validated_data: dict) -> User:
        del validated_data['repeat_password']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializer(serializers.ModelSerializer):
    password = PasswordField(required=True)
    username = serializers.CharField(max_length=20)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data: dict) -> User:
        if not (user := authenticate(
            username=validated_data['username'],
            password=validated_data['password']
        )):
            raise AuthenticationFailed
        return user
