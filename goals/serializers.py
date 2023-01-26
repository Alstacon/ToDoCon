from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from core.models import User
from core.serializers import ProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'


class BoardCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')

    def create(self, validated_data):
        user = validated_data.pop('user')
        board = Board.objects.create(**validated_data)
        BoardParticipant.objects.create(user=user, board=board, role=BoardParticipant.Role.owner)

        return board


class BoardParticipantSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all()
    )

    role = serializers.ChoiceField(
        required=True, choices=BoardParticipant.Role
    )

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardSerializer(serializers.ModelSerializer):
    participants = BoardParticipantSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')

    def update(self, instance, validated_data) -> Board:
        owner = validated_data.pop('user')
        new_participants: list[dict] = validated_data.pop('participants')
        old_participants: dict = instance.participants.exclude(user=owner)
        new_by_id = {part['user'].id: part for part in new_participants}
        # {1: {id: 1, username: 'name', role: 1, ...}, }

        with transaction.atomic():
            # определить и выкинуть тех, кого не будет в новом списке участников
            for old_part in old_participants:
                if old_part.user_id not in new_by_id.keys():
                    old_part.delete()
                # для всех, кто остался
                else:
                    # проверяем, изменилась ли роль -> изменяем
                    if old_part.role != new_by_id[old_part.user_id]['role']:
                        old_part.role = new_by_id[old_part.user_id]['role']
                        old_part.save()
                    # получаем обработанного старого участника и удаляем из словаря новых
                    new_by_id.pop(old_part.user_id)
            # для всех, кто остался в новых
            for new_part in new_by_id.values():
                BoardParticipant.objects.create(
                    user=new_part['user'],
                    board=instance,
                    role=new_part['role']
                )
            instance.title = validated_data['title']
            instance.save()
        return instance


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.filter(is_deleted=False)
    )

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated', 'is_deleted')

    def create(self, validated_data):
        board_id = self.initial_data.pop('board', None)
        board = get_object_or_404(Board, pk=board_id)

        if not board.participants.filter(Q(user=self.context['request'].user.id)
                                         & ~Q(role=BoardParticipant.Role.reader)).exists():
            raise PermissionDenied({'non_field_errors': ['''You don't have permission''']})

        category = GoalCategory.objects.create(**validated_data)
        return category


class GoalCategorySerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated', 'board')


class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = serializers.PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.filter(is_deleted=False)
    )

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')

    def create(self, validated_data):
        category_id = self.initial_data.pop('category', None)
        category = get_object_or_404(GoalCategory, pk=category_id)
        board = category.board

        if not board.participants.filter(Q(user=self.context['request'].user.id)
                                         & ~Q(role=BoardParticipant.Role.reader)).exists():
            raise PermissionDenied({'non_field_errors': ['''You don't have permission''']})

        goal = Goal.objects.create(**validated_data)
        return goal


class GoalSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')

    def create(self, validated_data):
        goal_id = self.initial_data.pop('goal', None)
        goal = get_object_or_404(Goal, pk=goal_id)
        board = goal.category.board
        if not board.participants.filter(Q(user=self.context['request'].user.id)
                                         & ~Q(role=BoardParticipant.Role.reader)).exists():
            raise PermissionDenied({'non_field_errors': ['''You don't have permission''']})

        comment = GoalComment.objects.create(**validated_data)
        return comment


class GoalCommentSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal')
