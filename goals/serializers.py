from rest_framework import serializers

from goals.models import GoalCategory


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')


class GoalCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')
