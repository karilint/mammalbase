from django.core.files import File
from django.db import models
from django.core.files.storage import default_storage
from mb.models import BaseModel

class ExportFile(BaseModel):
    file = models.FileField(default_storage)

    def set_file(self, file_object: File):
        self.file = file_object

    def __str__(self):
        return self.file.name

