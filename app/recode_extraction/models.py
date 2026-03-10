from django.conf import settings
from django.db import models


class SourceDocument(models.Model):
    pdf_file = models.FileField(upload_to='recode_sources/')
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    citation = models.CharField(max_length=1000, blank=True)
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


    def build_citation(self) -> str:
        year = self.year or ''
        authors = (self.authors or 'Unknown').strip()
        title = (self.title or 'Untitled').strip().rstrip('.')
        if year:
            return f'{authors}, {year}. {title}.'
        return f'{authors}. {title}.'

    def save(self, *args, **kwargs):
        if not (self.citation or '').strip():
            self.citation = self.build_citation()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class SourceExtractionRun(models.Model):
    class Status(models.TextChoices):
        QUEUED = 'queued', 'Queued'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
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
    pass1_evidence_package = models.JSONField(default=dict, blank=True)
    pass2_structured_package = models.JSONField(default=dict, blank=True)
    qc_summary = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.source_id}:{self.status}'


class ExtractedEntity(models.Model):
    class EntityType(models.TextChoices):
        TAXON = 'taxon', 'Taxon'
        TRAIT = 'trait', 'Trait'
        VALUE = 'value', 'Value'

    extraction_run = models.ForeignKey(
        SourceExtractionRun,
        on_delete=models.CASCADE,
        related_name='entities',
    )
    entity_type = models.CharField(max_length=20, choices=EntityType.choices)
    text = models.TextField()
    start_offset = models.IntegerField(null=True, blank=True)
    end_offset = models.IntegerField(null=True, blank=True)
    page_number = models.PositiveIntegerField(null=True, blank=True)
    confidence = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']



class ExtractedAssertionModel(models.Model):
    class ReviewStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    extraction_run = models.ForeignKey(
        SourceExtractionRun,
        on_delete=models.CASCADE,
        related_name='assertions',
    )
    subject_taxon = models.CharField(max_length=250)
    trait_name = models.CharField(max_length=250)
    value_raw = models.CharField(max_length=250)
    unit = models.CharField(max_length=50, blank=True)
    context = models.TextField(blank=True)
    confidence = models.FloatField(default=0)
    evidence_start = models.IntegerField(null=True, blank=True)
    evidence_end = models.IntegerField(null=True, blank=True)
    page_number = models.PositiveIntegerField(null=True, blank=True)
    mapped_trait_id = models.CharField(max_length=100, blank=True)
    ets_payload = models.JSONField(default=dict, blank=True)
    ets_persisted = models.BooleanField(default=False)
    review_status = models.CharField(max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)
    edited_value = models.CharField(max_length=250, blank=True)
    edited_unit = models.CharField(max_length=50, blank=True)
    reviewer_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='recode_reviewed_assertions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    unmapped_reason = models.CharField(max_length=1000, blank=True)
    qc_errors = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
