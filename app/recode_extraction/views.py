from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SourceDocumentUploadForm
from .models import SourceDocument
from .services import create_extraction_run


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
    run = create_extraction_run(document, actor_id=request.user.pk, dry_run=dry_run)
    mode = 'dry run' if dry_run else 'full run'
    messages.success(request, f'Extraction run {run.pk} completed ({mode}).')
    return redirect('recode_source_document_detail', pk=document.pk)
