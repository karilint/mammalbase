from django.shortcuts import render
from django.http import HttpResponseNotFound, FileResponse
from .models import ExportFile
from .tasks import create_poc_tsv_file
from django.contrib.auth.decorators import login_required


@login_required
def export_to_tsv(request):
    """A view that streams a large TSV file."""
    create_poc_tsv_file.delay()
    return render(request, template_name='export/export_measurements.html')


@login_required
def get_exported_file(request, file_id):
    try:
        file_model = ExportFile.objects.filter(id=file_id)[0]
        f = file_model.file.open()
        return FileResponse(f, as_attachment=True)
    except IOError:
        return HttpResponseNotFound('<h1>File does not exist</h1>')
    except IndexError:
        return HttpResponseNotFound('<h1>File does not exist</h1>')
