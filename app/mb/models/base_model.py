""" mb.models.base_model - The parent model for all the other models.

This module should not be imported anywhere else than __init__.py!

To import models elsewhere use subpackage:
from mb.models import ModelName
"""

from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from utils.fields import AutoUserForeignKey
from simple_history.models import HistoricalRecords

class CustomQuerySet(QuerySet):
    """ Custom query to disable delete. Delete just makes entry inactive. """
    def delete(self, *args, **kwargs):
        self.update(is_active=False)

class ActiveManager(models.Manager):
    """ Model for filtering active entries ??? """
    def is_active(self):
        """ Return objects that are currently active """
        return self.model.objects.filter(is_active=True)

    def get_queryset(self):
        """ For getting deletion preventing queryset ??? """
        return CustomQuerySet(self.model, using=self._db)

class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="createdby_%(class)s",
        editable=False,
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="modifiedby_%(class)s",
        editable=False,
    )
    history = HistoricalRecords(
        history_change_reason_field=models.TextField(null=True),
        inherit=True
    )
    is_active = models.BooleanField(default=True)
    objects = ActiveManager()

    def delete(self, *args, **kwargs):
        for rel in self._meta.related_objects:
            if (rel.on_delete == models.CASCADE and hasattr(rel.related_model, 'is_active')):
                related_manager = getattr(self, rel.get_accessor_name())
                for related_obj in related_manager.all():
                    related_obj.delete()
        self.is_active = False
        self.save()

    class Meta:
        abstract = True
