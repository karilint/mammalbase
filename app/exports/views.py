from django.shortcuts import render
from django.http import HttpResponseNotFound, FileResponse
from .models import ExportFile
from .tasks import create_poc_tsv_file
from django.contrib.auth.decorators import login_required
from .forms import MeasurementsForm

@login_required
def export_to_tsv(request):
    """A view that streams a large TSV file."""
    if request.method == 'POST': 
        measurement_form = MeasurementsForm(request.POST)
        if measurement_form.is_valid():
            user_email = measurement_form.cleaned_data['user_email']
            create_poc_tsv_file.delay(user_email)
    measurement_form = MeasurementsForm()
    context = {'form': measurement_form}
    return render(request, 'export/export_measurements.html', context)


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
