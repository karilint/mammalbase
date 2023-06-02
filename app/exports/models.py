from django.db import models
from django.db.models import Model, ForeignKey
from django.core.files.storage import default_storage


class ExportFile(Model):
    file = models.FileField(default_storage)

    def __str__(self):
        return self.file.name

