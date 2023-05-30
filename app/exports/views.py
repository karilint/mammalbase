from django.shortcuts import render
from . import tasks
from django.http import StreamingHttpResponse, HttpResponseNotFound, FileResponse
from django.http import HttpResponse
from .models import ExportFile
from .tasks import create_poc_tsv_file

import csv


def export_to_tsv(request):
    """A view that streams a large TSV file."""
    create_poc_tsv_file.delay()
    return render(request, template_name='export/export_measurements.html')


def get_exported_file(request, file_id):
    try:
        file_model = ExportFile.objects.filter(id=file_id)[0]
        f = file_model.file.open()
        return FileResponse(f, as_attachment=True)
    except IOError:
        return HttpResponseNotFound('<h1>File not exist</h1>')
    except IndexError:
        return HttpResponseNotFound('<h1>File not exist</h1>')
