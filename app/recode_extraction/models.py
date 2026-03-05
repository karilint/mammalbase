from django.conf import settings
from django.db import models


class SourceDocument(models.Model):
    pdf_file = models.FileField(upload_to='recode_sources/')
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    doi = models.CharField(max_length=100, blank=True)
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recode_source_documents',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class SourceExtractionRun(models.Model):
    class Status(models.TextChoices):
        QUEUED = 'queued', 'Queued'
        RUNNING = 'running', 'Running'
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'

    source = models.ForeignKey(
        SourceDocument,
        on_delete=models.CASCADE,
        related_name='extraction_runs',
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    current_stage = models.CharField(max_length=50, blank=True)
    progress_percent = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    logs = models.TextField(blank=True)
    model_version = models.CharField(max_length=50, blank=True)
    parameters = models.JSONField(default=dict, blank=True)
    extracted_text_package = models.JSONField(default=dict, blank=True)
    unmapped_traits = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def source_document(self):
        return self.source

    def __str__(self):
        return f'{self.source_id}:{self.status}'


class ExtractedEntity(models.Model):
    extraction_run = models.ForeignKey(
        SourceExtractionRun,
        on_delete=models.CASCADE,
        related_name='entities',
    )
    entity_type = models.CharField(max_length=64)
    text = models.TextField()
    span_external_id = models.CharField(max_length=128, db_index=True, default='')
    token_ids = models.JSONField(default=list, blank=True)
    start_offset_utf16 = models.IntegerField(null=True, blank=True)
    end_offset_utf16 = models.IntegerField(null=True, blank=True)
    page_number = models.PositiveIntegerField(null=True, blank=True)
    snippet = models.TextField(blank=True)
    confidence = models.FloatField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['extraction_run', 'span_external_id'],
                name='uniq_entity_per_run_span_external_id',
            )
        ]


class ExtractedRelation(models.Model):
    extraction_run = models.ForeignKey(
        SourceExtractionRun,
        on_delete=models.CASCADE,
        related_name='relations',
    )
    relation_type = models.CharField(max_length=64)
    head_entity = models.ForeignKey(
        ExtractedEntity,
        on_delete=models.CASCADE,
        related_name='out_relations',
    )
    tail_entity = models.ForeignKey(
        ExtractedEntity,
        on_delete=models.CASCADE,
        related_name='in_relations',
    )
    drawn_from_token_id = models.CharField(max_length=64, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    page_number = models.PositiveIntegerField(null=True, blank=True)
    snippet = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['extraction_run', 'relation_type', 'head_entity', 'tail_entity', 'drawn_from_token_id'],
                name='uniq_relation_per_run_endpoints',
            )
        ]


class ExtractedAssertionModel(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        IMPORTED = 'imported', 'Imported'
        FAILED = 'failed', 'Failed'

    extraction_run = models.ForeignKey(
        SourceExtractionRun,
        on_delete=models.CASCADE,
        related_name='assertions',
    )
    subject_taxon = models.CharField(max_length=250)
    trait_name = models.CharField(max_length=250)
    value_raw = models.CharField(max_length=250)
    unit = models.CharField(max_length=50, blank=True)
    unit_text = models.CharField(max_length=50, blank=True)
    sex_text = models.CharField(max_length=100, blank=True)
    lstage_text = models.CharField(max_length=100, blank=True)
    count_text = models.CharField(max_length=100, blank=True)
    ref_text = models.CharField(max_length=250, blank=True)
    locality_text = models.CharField(max_length=250, blank=True)
    coord_text = models.CharField(max_length=250, blank=True)
    date_text = models.CharField(max_length=100, blank=True)
    context = models.TextField(blank=True)
    confidence = models.FloatField(default=0)
    evidence_start = models.IntegerField(null=True, blank=True)
    evidence_end = models.IntegerField(null=True, blank=True)
    page_number = models.PositiveIntegerField(null=True, blank=True)
    token_ids = models.JSONField(default=list, blank=True)
    snippet = models.TextField(blank=True)
    mapped_trait_id = models.CharField(max_length=100, blank=True)
    ets_payload = models.JSONField(default=dict, blank=True)
    ets_persisted = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    edited_value = models.CharField(max_length=250, blank=True)
    edited_unit = models.CharField(max_length=50, blank=True)
    reviewer_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='recode_reviewed_assertions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    unmapped_reason = models.CharField(max_length=250, blank=True)
    imported_source_measurement_value_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
