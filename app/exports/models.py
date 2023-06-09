from django.db import models
from django.core.files.storage import default_storage


class ExportFile(models.Model):
    file = models.FileField(default_storage)

    def __str__(self):
        return self.file.name

