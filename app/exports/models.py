""" exports.models - Exports related models. """
from django.db import models
from django.core.files import File
from django.core.files.storage import default_storage
from mb.models import BaseModel

class ExportFile(BaseModel):
    """ Model to store exported files storing details  """
    file = models.FileField(default_storage)

    # pylint: disable = missing-function-docstring
    def set_file(self, file_object: File):
        self.file = file_object

    def __str__(self):
        return self.file.name
