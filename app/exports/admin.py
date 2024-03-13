""" exports.admin - Registering models for django admin? """

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import ExportFile

admin.site.register(ExportFile, SimpleHistoryAdmin)
