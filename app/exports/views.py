from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, FileResponse
from .models import ExportFile
from .tasks import ets_export_query_set
from django.contrib.auth.decorators import login_required
from .forms import MeasurementsForm
from django.core.validators import validate_email


@login_required
def export_to_tsv(request):
    """A view that renders an export form."""
    if request.method == 'POST':
        form = MeasurementsForm(request.POST)
        if form.is_valid():
            user_email = request.POST['user_email']
            checkboxes = request.POST.getlist('export_choices')
            export_file = ExportFile(file=None)
            export_file.save()
            export_file_id = export_file.pk
            is_admin_or_contributor = is_user_data_admin_or_contributor(request)
            ets_export_query_set.delay(user_email, export_file_id, is_admin_or_contributor, checkboxes)
            return redirect('submission')
    else:
        form = MeasurementsForm()
    context = {'form': form}
    return render(request, 'export/export_ets.html', context)


def is_user_data_admin_or_contributor(request):
    groups = request.user.groups.all()
    for group in groups:
        print(f"group id type: {group.id}")
        if group.id in [1, 2]:
            return True
    return False


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
