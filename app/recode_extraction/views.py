import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SourceDocumentUploadForm
from .models import ExtractedAssertionModel, SourceDocument, SourceExtractionRun
from .services import create_extraction_run
from .services.review import (
    apply_assertion_review,
    bulk_approve_above_threshold,
    export_assertions_csv,
    persist_approved_assertions_to_ets,
)
from .tasks import run_recode_pipeline


@login_required
def source_document_list(request):
    documents = SourceDocument.objects.select_related('uploader').all()
    return render(request, 'recode_extraction/source_document_list.html', {'documents': documents})


@login_required
def source_document_upload(request):
    if request.method == 'POST':
        form = SourceDocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploader = request.user
            document.save()
            messages.success(request, 'PDF source uploaded successfully.')
            return redirect('recode_source_document_detail', pk=document.pk)
    else:
        form = SourceDocumentUploadForm()

    return render(request, 'recode_extraction/source_document_upload.html', {'form': form})


@login_required
def source_document_detail(request, pk: int):
    document = get_object_or_404(SourceDocument.objects.select_related('uploader'), pk=pk)
    runs = document.extraction_runs.all()
    return render(
        request,
        'recode_extraction/source_document_detail.html',
        {'document': document, 'runs': runs},
    )


@login_required
def source_document_run_extraction(request, pk: int):
    document = get_object_or_404(SourceDocument, pk=pk)
    if request.method != 'POST':
        return redirect('recode_source_document_detail', pk=document.pk)

    dry_run = request.POST.get('dry_run') == '1'
    extraction_backend = request.POST.get('extraction_backend', 'baseline')
    confidence_threshold = float(request.POST.get('confidence_threshold', '0') or '0')

    run_params = {
        'actor_id': request.user.pk,
        'dry_run': dry_run,
        'extraction_backend': extraction_backend,
        'confidence_threshold': confidence_threshold,
        'mapping_version': 'v1',
    }

    if os.environ.get('RECODE_ASYNC', '0') == '1':
        run_recode_pipeline.delay(document.pk, run_params)
        messages.success(request, 'RECODE extraction queued in background.')
    else:
        run = create_extraction_run(document, **run_params)
        mode = 'dry run' if dry_run else 'full run'
        messages.success(request, f'Extraction run {run.pk} completed ({mode}).')

    return redirect('recode_source_document_detail', pk=document.pk)


@login_required
def extraction_run_detail(request, run_id: int):
    run = get_object_or_404(SourceExtractionRun.objects.select_related('source'), pk=run_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_assertion':
            assertion = get_object_or_404(ExtractedAssertionModel, pk=request.POST.get('assertion_id'), extraction_run=run)
            apply_assertion_review(
                assertion,
                reviewer=request.user,
                review_status=request.POST.get('review_status', assertion.status),
                edited_value=request.POST.get('edited_value', ''),
                edited_unit=request.POST.get('edited_unit', ''),
                mapped_trait_id=request.POST.get('mapped_trait_id', ''),
                reviewer_note=request.POST.get('reviewer_note', ''),
            )
            messages.success(request, f'Assertion {assertion.pk} updated.')
        elif action == 'bulk_approve':
            threshold = float(request.POST.get('threshold', '0') or '0')
            bulk_approve_above_threshold(run, reviewer=request.user, threshold=threshold)
            messages.success(request, f'Approved pending assertions with confidence ≥ {threshold}.')
        elif action == 'persist_approved':
            try:
                persist_approved_assertions_to_ets(run)
                messages.success(request, 'Approved assertions persisted to ETS.')
            except Exception as exc:
                messages.error(request, f'ETS persistence failed: {exc}')
        return redirect('recode_extraction_run_detail', run_id=run.pk)

    assertions_qs = run.assertions.all()
    trait_filter = request.GET.get('trait')
    taxon_filter = request.GET.get('taxon')
    page_filter = request.GET.get('page')
    confidence_min = request.GET.get('confidence_min')
    review_status_filter = request.GET.get('review_status')

    if trait_filter:
        assertions_qs = assertions_qs.filter(trait_name__icontains=trait_filter)
    if taxon_filter:
        assertions_qs = assertions_qs.filter(subject_taxon__icontains=taxon_filter)
    if page_filter:
        assertions_qs = assertions_qs.filter(page_number=page_filter)
    if confidence_min:
        assertions_qs = assertions_qs.filter(confidence__gte=float(confidence_min))
    if review_status_filter:
        assertions_qs = assertions_qs.filter(status=review_status_filter)

    if request.GET.get('export') == 'csv':
        csv_data = export_assertions_csv(run, queryset=assertions_qs)
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="recode_run_{run.pk}_review.csv"'
        return response

    summary = {
        'entities': run.entities.count(),
        'assertions': run.assertions.count(),
        'mapped': run.assertions.filter(mapped_trait_id__gt='').count(),
        'unmapped': run.assertions.filter(mapped_trait_id='').count(),
    }

    context = {
        'run': run,
        'assertions': assertions_qs.order_by('id'),
        'summary': summary,
        'review_status_choices': ExtractedAssertionModel.Status.choices,
        'filters': {
            'trait': trait_filter or '',
            'taxon': taxon_filter or '',
            'page': page_filter or '',
            'confidence_min': confidence_min or '',
            'review_status': review_status_filter or '',
        },
    }
    return render(request, 'recode_extraction/extraction_run_detail.html', context)
