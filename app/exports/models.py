from django.db import models
from django.core.files import File
from django.core.files.storage import default_storage


# Create your models here.



class ExportFile(models.Model):
    name = models.CharField(max_length=128)
    file = models.FileField(default_storage)

    def __str__(self):
        return self.name
