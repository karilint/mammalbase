from django.db import models
from django.db.models.query import QuerySet

from django_userforeignkey.models.fields import UserForeignKey
from simple_history.models import HistoricalRecords

class CustomQuerySet(QuerySet):
    def delete(self):
        self.update(is_active=False)

class ActiveManager(models.Manager):
    def is_active(self):
        return self.model.objects.filter(is_active=True)

    def get_queryset(self):
        return CustomQuerySet(self.model, using=self._db)

# https://medium.com/@KevinPavlish/
# add-common-fields-to-all-your-django-models-bce033ac2cdc
class BaseModel(models.Model):
    """
    A base model including basic fields for each Model
    see. https://pypi.org/project/django-userforeignkey/
    """
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = UserForeignKey(
            auto_user_add=True,
            verbose_name="The user that is automatically assigned",
            related_name='createdby_%(class)s')
    modified_by = UserForeignKey(
            auto_user=True,
            verbose_name="The user that is automatically assigned",
            related_name='modifiedby_%(class)s')
    # https://django-simple-history.readthedocs.io/en/2.6.0/index.html
    history = HistoricalRecords(
            history_change_reason_field=models.TextField(null=True),
            inherit=True)
    # https://stackoverflow.com/questions/5190313/
    # django-booleanfield-how-to-set-the-default-value-to-true
    is_active = models.BooleanField(
            default=True,
            help_text='Is the record active')
    objects = ActiveManager()

    # https://stackoverflow.com/questions/4825815/
    # prevent-delete-in-django-model
    #    def delete(self):
    #        self.is_active = False
    #        self.save()

    # Code by ChatGPT4
    def delete(self):
        """
        Recursively soft delete this object and cascade the soft delete to
        related objects.
        """
        # Handle related fields with cascading deletion
        for rel in self._meta.related_objects:
            if (rel.on_delete == models.CASCADE
                    and hasattr(rel.related_model, 'is_active')):
                related_manager = getattr(self, rel.get_accessor_name())
                related_objects = related_manager.all()

                # Recursively soft delete the related objects
                for related_obj in related_objects:
                    # This will ensure related objects of related_obj are
                    # also soft-deleted
                    related_obj.delete()

        # Soft delete the current object
        self.is_active = False
        self.save()

    class Meta:
        abstract = True
