import csv
from io import StringIO

from django.utils import timezone

from recode_extraction.models import ExtractedAssertionModel, SourceExtractionRun
from recode_extraction.services.orchestrator import import_approved_candidates


def apply_assertion_review(assertion: ExtractedAssertionModel, *, reviewer, review_status: str, edited_value: str = '', edited_unit: str = '', mapped_trait_id: str = '', reviewer_note: str = ''):
    assertion.status = review_status
    if edited_value:
        assertion.edited_value = edited_value
    if edited_unit:
        assertion.edited_unit = edited_unit
    if mapped_trait_id:
        assertion.mapped_trait_id = mapped_trait_id
    if reviewer_note:
        assertion.reviewer_note = reviewer_note
    assertion.reviewed_by = reviewer
    assertion.reviewed_at = timezone.now()
    assertion.save()


def bulk_approve_above_threshold(run: SourceExtractionRun, *, reviewer, threshold: float):
    run.assertions.filter(confidence__gte=threshold, status='pending').update(status='approved', reviewed_by=reviewer, reviewed_at=timezone.now())


def persist_approved_assertions_to_ets(run: SourceExtractionRun):
    import_approved_candidates(run)


def export_assertions_csv(run: SourceExtractionRun, queryset=None) -> str:
    queryset = queryset or run.assertions.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'subject_taxon', 'trait_name', 'value_raw', 'status', 'ets_persisted', 'snippet'])
    for item in queryset:
        writer.writerow([item.pk, item.subject_taxon, item.trait_name, item.value_raw, item.status, item.ets_persisted, item.snippet])
    return output.getvalue()
