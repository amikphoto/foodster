# core/aggregates.py
from django.db.models import Aggregate, CharField


class GroupConcat(Aggregate):
    """
    GROUP_CONCAT для SQLite (аналог ArrayAgg для PostgreSQL)
    """
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(expressions)s)'
    output_field = CharField()

    def __init__(self, expression, separator=',', **extra):
        super().__init__(expression, **extra)
        self.separator = separator

    def as_sqlite(self, compiler, connection):
        # Для SQLite с кастомным разделителем
        if self.separator != ',':
            self.template = "%(function)s(%(expressions)s, '%(separator)s')"
            return super().as_sql(compiler, connection, separator=self.separator)
        return super().as_sql(compiler, connection)