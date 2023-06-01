from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, FileResponse, HttpResponseRedirect
from .models import ExportFile
from .tasks import create_poc_tsv_file
from django.contrib.auth.decorators import login_required
from .forms import MeasurementsForm

@login_required
def export_to_tsv(request):
    """A view that streams a large TSV file."""
    measurement_form = MeasurementsForm()
    if request.method == 'POST':
        user_email = request.POST['user_email']
        create_poc_tsv_file.delay(user_email)
        return redirect('submission')
    context = {'form': measurement_form}
    return render(request, 'export/export_measurements.html', context)

def form_submitted(request):
    return render(request,'export/form_submitted.html')

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
