from django.core.exceptions import ValidationError
from django.utils import timezone
import re


def validate_year(value):
    today = timezone.now()
    if value < 0:
        raise ValidationError('Нельзя указывать год меньше "0"')
    if value > today.year:
        raise ValidationError('Нельзя указывать год больше текущего')
    return value


def validate_slug(value):
    regex = re.compile(r'^[-a-zA-Z0-9_]+$')
    if not re.fullmatch(regex, value):
        raise ValidationError(
            'В поле "slug" должны быть только латинские буквы или цифры'
            )
    return value
