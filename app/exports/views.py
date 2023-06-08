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
    measurement_form = MeasurementsForm()
    if request.method == 'POST':
        user_email = request.POST['user_email']
        checkboxes = request.POST.getlist('select_fields_to_be_exported')
        print(f'selected checkboxed {checkboxes}')
        #if email_validation(user_email) == True:
        ets_export_query_set.delay(user_email)
        return redirect('submission')
    context = {'form': measurement_form}
    return render(request, 'export/export_measurements.html', context)


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
