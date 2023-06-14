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
            print(f'selected checkboxes {checkboxes}')
            #if email_validation(user_email) == True:
            export_file = ExportFile(file=None)
            export_file.save()
            export_file_id = export_file.pk
            ets_export_query_set.delay(user_email, export_file_id)
            return redirect('submission')
    else:
        form = MeasurementsForm()
    context = {'form': form}
    return render(request, 'export/export_ets.html', context)


def form_submitted(request):
    return render(request,'export/form_submitted.html')

#def email_validation(email_address):
#    if not validate_email(email_address):
#        raise forms.ValidationError("Invalid")
#    return True

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
