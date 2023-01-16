from django.db import models
from django_filters import rest_framework
import django_filters

from goals.models import Goal


class GoalDateFilter(rest_framework.FilterSet):

    class Meta:
        model = Goal
        fields = {
            'due_date': ('lte', 'gte'),
            'category': ('exact', 'in'),
            'priority': ('exact', 'in'),
            'status': ('exact', 'in')
        }

        filter_overrides = {
            models.DateTimeField: {'filter_class': django_filters.IsoDateTimeFilter},
        }
