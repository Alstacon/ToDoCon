from datetime import datetime

from rest_framework.fields import DateTimeField


class BaseTestCase:

    @staticmethod
    def date_time_str(date_time: datetime) -> str:
        return DateTimeField().to_representation(date_time)

    @staticmethod
    def to_internal_value(date_time: datetime) -> str:
        return DateTimeField().to_internal_value(date_time)
