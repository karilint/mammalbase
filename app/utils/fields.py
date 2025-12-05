# utils/fields.py

from django.conf import settings
from django.db.models import ForeignKey, SET_NULL
from middleware.current_user import get_current_user

class AutoUserForeignKey(ForeignKey):
    """Custom ForeignKey to automatically assign current user."""

    def __init__(self, auto_user=False, auto_user_add=False, **kwargs):
        self.auto_user = auto_user
        self.auto_user_add = auto_user_add

        kwargs['to'] = settings.AUTH_USER_MODEL
        kwargs['on_delete'] = SET_NULL
        kwargs.setdefault('null', True)
        kwargs.setdefault('blank', True)
        kwargs.setdefault('editable', False)

        super().__init__(**kwargs)

    def pre_save(self, model_instance, add):
        current_user = get_current_user()
        object_user = self.value_from_object(model_instance)

        if current_user and current_user.is_authenticated:
            if self.auto_user:
                setattr(model_instance, self.name, current_user)
            elif self.auto_user_add and add and not object_user:
                setattr(model_instance, self.name, current_user)
        return super().pre_save(model_instance, add)
