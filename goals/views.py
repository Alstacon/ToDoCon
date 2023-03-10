from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from goals.filters import GoalDateFilter, CategoryBoardFilter
from goals.models import GoalCategory, Goal, GoalComment, Board
from goals.permissions import CategoryPermissions, GoalBoardPermissions, IsOwnerOrReadOnly, BoardPermissions
from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalCreateSerializer, \
    GoalSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, BoardCreateSerializer, BoardListSerializer, \
    BoardSerializer


class GoalCategoryCreateView(CreateAPIView):
    model = GoalCategory
    permission_classes = [CategoryPermissions, ]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [CategoryPermissions, ]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CategoryBoardFilter
    search_fields = ['title']
    ordering_fields = ['title', 'created']
    ordering = ['title']

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related('board__participants').filter(
            board__participants__user_id=self.request.user.id,
            is_deleted=False
        )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [CategoryPermissions]

    def get_queryset(self):
        return GoalCategory.objects.select_related('user').filter(
            is_deleted=False,
        )

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.goals.update(status=Goal.Status.archived)
        return instance


class GoalCreateView(CreateAPIView):
    model = Goal
    permission_classes = [IsAuthenticated, ]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
    model = Goal
    permission_classes = [IsAuthenticated]
    serializer_class = GoalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    search_fields = ['title', 'description']
    ordering_fields = ['due_date']
    ordering = ['due_date', '-priority']

    def get_queryset(self):
        return Goal.objects.select_related('category').filter(
            ~Q(status=Goal.Status.archived) &
            Q(category__is_deleted=False) &
            Q(category__board__participants__user_id=self.request.user.id)
        )


class GoalView(RetrieveUpdateDestroyAPIView):
    model = Goal
    permission_classes = [IsAuthenticated, GoalBoardPermissions]
    serializer_class = GoalSerializer

    def get_queryset(self):
        return Goal.objects.select_related('category').filter(
            ~Q(status=Goal.Status.archived) &
            Q(category__is_deleted=False) &
            Q(category__board__participants__user_id=self.request.user.id)
        )

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.status = Goal.Status.archived
            instance.save(update_fields=('status',))
        return instance


class GoalCommentCreateView(CreateAPIView):
    model = GoalComment
    serializer_class = GoalCommentCreateSerializer
    permission_classes = [IsAuthenticated]


class GoalCommentListView(ListAPIView):
    model = GoalComment
    permission_classes = [IsAuthenticated]
    serializer_class = GoalCommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.filter(
            goal__category__board__participants__user_id=self.request.user.id
        )


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    model = GoalComment
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = GoalCommentSerializer

    def get_queryset(self):
        return GoalComment.objects.filter(goal__category__board__participants__user_id=self.request.user.id)


class BoardCreateView(CreateAPIView):
    serializer_class = BoardCreateSerializer
    permission_classes = [IsAuthenticated, ]


class BoardListView(ListAPIView):
    model = Board
    serializer_class = BoardListSerializer
    permission_classes = [BoardPermissions, ]
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ['title']

    def get_queryset(self):
        return Board.objects.prefetch_related('participants').filter(
            participants__user_id=self.request.user.id,
            is_deleted=False
        )


class BoardView(RetrieveUpdateDestroyAPIView):
    model = Board
    serializer_class = BoardSerializer
    permission_classes = [BoardPermissions, ]

    def get_queryset(self):
        return Board.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.category.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
        return instance
