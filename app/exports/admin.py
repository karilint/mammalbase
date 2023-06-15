from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import ExportFile

# Register your models here.

admin.site.register(ExportFile, SimpleHistoryAdmin)
