from django.db.models import Func

class DateFormat(Func):
    function = 'DATE_FORMAT'
    template = '%(function)s(%(expressions)s)'

class Round2(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 2)'
