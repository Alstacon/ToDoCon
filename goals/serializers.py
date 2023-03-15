from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from rest_framework import serializers

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
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')

    def create(self, validated_data: dict) -> Board:
        user = validated_data.pop('user')
        board: Board = Board.objects.create(**validated_data)
        BoardParticipant.objects.create(user=user, board=board, role=BoardParticipant.Role.owner)

        return board


class BoardParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.Role.choices[1:])
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    def validate(self, attrs: dict) -> dict:
        if attrs['user'] == self.context['request'].user and attrs['role'] != BoardParticipant.Role.owner:
            raise ValidationError({'Failed to update owner role'})
        return attrs

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardSerializer(serializers.ModelSerializer):
    participants = BoardParticipantSerializer(many=True)

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')

    def update(self, instance: Board, validated_data: dict) -> Board:
        """Удаляет из списка всех участников, кроме владельца и записывает заново."""
        with transaction.atomic():
            BoardParticipant.objects.filter(board=instance).exclude(user=self.context['request'].user).delete()
            BoardParticipant.objects.bulk_create([
                BoardParticipant(
                    user=participant['user'],
                    role=participant['role'],
                    board=instance,
                )
                for participant in validated_data.pop('participants', [])
            ])

            if title := validated_data.get('title'):
                instance.title = title
                instance.save(update_fields=('title',))

        return instance


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated', 'is_deleted')

    def validate_board(self, value: Board) -> Board:
        if value.is_deleted:
            raise ValidationError('Нельзя создать категорию в удаленной доске.')
        if not BoardParticipant.objects.filter(
                board=value,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user.id
        ):
            raise PermissionDenied
        return value


class GoalCategorySerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created', 'updated', 'board']


class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        if value.is_deleted:
            raise ValidationError(message='Нельзя создать цель в удаленной категории')

        if not BoardParticipant.objects.filter(
                board=value.board.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user.id
        ):
            raise PermissionDenied
        return value


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

    def validate_goal(self, value: Goal) -> Goal:
        if value.status == Goal.Status.archived:
            raise ValidationError('Нельзя оставить комментарий к удаленной цели.')
        if value.category.board.is_deleted:
            raise ValidationError('Нельзя оставить комментарий к цели в удаленной доске.')
        if not BoardParticipant.objects.filter(
                board=value.category.board.id,
                user_id=self.context['request'].user.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ):
            raise PermissionDenied
        return value


class GoalCommentSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal')
