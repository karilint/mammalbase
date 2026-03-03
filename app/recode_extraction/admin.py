from django.contrib import admin

from .models import SourceDocument, SourceExtractionRun


@admin.register(SourceDocument)
class SourceDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'year', 'doi', 'uploader', 'created_at')
    search_fields = ('title', 'authors', 'doi')


@admin.register(SourceExtractionRun)
class SourceExtractionRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'status', 'model_version', 'created_at', 'started_at', 'finished_at')
    list_filter = ('status', 'model_version')
