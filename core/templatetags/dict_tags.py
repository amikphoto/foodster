# templatetags/dict_tags.py
from datetime import datetime
from django.template.defaultfilters import date as django_date

from django import template
register = template.Library()

@register.filter
def get_id(value):
    """Извлекает id из словаря или возвращает значение как есть"""
    if isinstance(value, dict):
        return value.get('id', '')
    return value


@register.filter
def format_date(value, arg='%d.%m.%Y'):
    """Извлекает дату и форматирует с указанным форматом"""
    if isinstance(value, dict):
        date = value.get('date', None)
    else:
        date = value

    if date:
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    date = datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    return date
        return date.strftime(arg)
    return date