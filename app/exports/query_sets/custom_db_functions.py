from django.db.models import Func


class Round2(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 2)'
