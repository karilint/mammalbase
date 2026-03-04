from django.contrib import admin

from .models import (
    ExtractedAssertionModel,
    ExtractedEntity,
    SourceDocument,
    SourceExtractionRun,
)


@admin.register(SourceDocument)
class SourceDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'year', 'doi', 'uploader', 'created_at')
    search_fields = ('title', 'authors', 'doi')


@admin.register(SourceExtractionRun)
class SourceExtractionRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'status', 'current_stage', 'progress_percent', 'model_version', 'created_at', 'started_at', 'finished_at')
    list_filter = ('status', 'model_version')


@admin.register(ExtractedEntity)
class ExtractedEntityAdmin(admin.ModelAdmin):
    list_display = ('id', 'extraction_run', 'entity_type', 'text', 'page_number', 'confidence')
    list_filter = ('entity_type',)


@admin.register(ExtractedAssertionModel)
class ExtractedAssertionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'extraction_run', 'subject_taxon', 'trait_name', 'value_raw', 'ets_persisted')
    list_filter = ('ets_persisted',)
